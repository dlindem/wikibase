import csv, json, time, os, sys, re
import nlp
import config_private
from pyzotero import zotero
pyzot = zotero.Zotero(config_private.zotero_group_nr, 'group', config_private.zotero_api_key)

overwrite_existing_json = True


with open('data/fulltext_items.csv') as file:
    rows = csv.DictReader(file)
    for row in rows:

        parent_id = row['parent_id']
        pdf_id = row['pdf_id']
        bibitem_qid = row['item_id']
        lang_iso = row['iso']
        print(f"\nNow processing {bibitem_qid}, Zotero {parent_id}, language is {lang_iso}.")
        zotitem = pyzot.item(parent_id)
        zotchildren = pyzot.children(parent_id)
        # print(zotitem)
        # with open('data/testzotitem.json', 'w') as jsonfile:
        #     json.dump({'zotitem':zotitem, 'children':zotchildren}, jsonfile, indent=2)
        control = {'.pdf': None, '.txt': None, '.xml': None, '.json': None}
        for attachment in zotchildren:
            attkey = attachment['key']
            if "enclosure" in attachment['links']:
                if 'title' not in attachment['links']['enclosure']:
                    continue
                filext_re = re.search(r'\.\w+$', attachment['links']['enclosure']['title'])
                if filext_re:
                    filext = filext_re.group(0)
                    if filext not in control:
                        continue
                    if control[filext] == None: # first match
                        control[filext] = attkey
                        if filext == ".pdf" and attkey != pdf_id:
                            print(f'PROBLEM: {bibitem_qid} as {pdf_id} on wikibase, but {attkey} on Zotero as PDF attachment!!')
                            time.sleep(2)
                    else: # there is already a file of this type
                        print(f'Found duplicate {filext}."')
                        if pdf_id == attkey:
                            print(f"Found the pdf referenced on Wikibase: {pdf_id}")
                            control['.pdf'] = pdf_id
                        elif filext != ".txt": # do not delete extra txt, just stay with the first one
                            try:
                                delete_op = pyzot.delete_item(pyzot.item(attkey))
                                print(f'Have deleted this repeated {filext}: {attkey}.')
                            except:
                                print(f"ERROR: No success deleting {filext}: {attkey}!!")
                                time.sleep(1)

        print(control)
        if control['.json'] and not overwrite_existing_json:
            print('Will skip item with existing full text json file.')
            continue
        elif control['.json'] and overwrite_existing_json:
            try:
                delete_op = pyzot.delete_item(pyzot.item(control['.json']))
                print(f"Have deleted existing full text json file.")
            except:
                print(f"ERROR: No success deleting full text json file {control['json']}!!")
                time.sleep(1)

        xmlfile = f"/media/david/FATdisk/ENEOLI/eneoli_fulltext_{bibitem_qid}.tei.xml"
        resultfile = f"/media/david/FATdisk/ENEOLI/eneoli_fulltext_{bibitem_qid}.json"

        if control['.txt']:
            for file in os.listdir(f"/home/david/Zotero/storage/{control['.txt']}"):
                if file.endswith(".txt"):
                    txtfile = f"/home/david/Zotero/storage/{control['.txt']}/{file}"
                    with open(txtfile, encoding="utf-8") as file:
                        bodytxt = nlp.check_encoding(file.read(), control['.txt'])
                    teijson = {'abstract': '', 'body': bodytxt}
                    print('This item has TXT, have taken text from there as body.')

        else:

            if not os.path.isfile(xmlfile):
                print(f"There is something wrong with {xmlfile}.")
                if not control['.txt']:
                    continue
            else:
                if control['.xml'] == None:
                    pyzot.attachment_simple([xmlfile], parentid=parent_id)
                    print(f"Success attaching {xmlfile} to Zotero {parent_id}...")
            teijson = nlp.getgrobidabstractbody(xmlfile)

        teijson['abstract_lemmatized'] = nlp.lemmatize_clean(teijson['abstract'], lang=lang_iso)
        teijson['body_lemmatized'] = nlp.lemmatize_clean(teijson['body'], lang=lang_iso)

        with open(resultfile, 'w') as jsonfile:
            json.dump(dict(sorted(teijson.items())), jsonfile, indent=2)
        print(f"Success processing and saving {resultfile}...")



        pyzot.attachment_simple([resultfile], parentid=parent_id)
        print(f"Success attaching {resultfile} to Zotero item {parent_id}...")

        try:
            pyzot.add_tags(zotitem, 'processed_fulltext')
            print(f"Success tagging Zotero item {parent_id}...")
        except:
            print(f"ERROR: No success tagging Zotero item {parent_id}!!")

        time.sleep(1)


