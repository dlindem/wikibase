import csv, json, time, os, sys, re
import nlp
import config_private
from pyzotero import zotero
pyzot = zotero.Zotero(config_private.zotero_group_nr, 'group', config_private.zotero_api_key)

overwrite_existing_json = False
missing_tei_list = []

with open('data/fulltext_items.csv') as file:
    rows = csv.DictReader(file, delimiter="\t")
    for row in rows:

        parent_id = row['parent_id']
        pdf_id = row['pdf_id']
        bibitem_qid = row['item_id']
        lang_iso = row['iso']
        desctext = re.sub(r'[^\w\-_]', '' ,row['description'].strip().replace(" ","_"))
        xmlfile = f"/media/david/FATdisk/ENEOLI/eneoli_fulltext_{bibitem_qid}.tei.xml"
        resultfile = f"/media/david/FATdisk/ENEOLI/eneoli_fulltext_{bibitem_qid}.json"

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
                            delete_op = pyzot.delete_item(pyzot.item(control['.pdf']))
                            print(f"Have deleted this repeated {filext} which raised the problem before: {control['.pdf']}.")
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

        elif control['.json'] and overwrite_existing_json:
            try:
                delete_op = pyzot.delete_item(pyzot.item(control['.json']))
                print(f"Have deleted existing full text json file.")
            except:
                print(f"ERROR: No success deleting full text json file {control['json']}!!")
                time.sleep(1)

        else:

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
                    print(f"Did not find {xmlfile}.")
                    missing_tei_list.append(bibitem_qid)
                    zotitem = pyzot.add_tags(zotitem, 'failed_TEI')
                    print(f"Added 'failed_TEI' tag to {parent_id} ({bibitem_qid}).")
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

        # last step: a body txt for Sketch Engine
        ske_filename = f"/media/david/FATdisk/ENEOLI/NeoCorpus_TXT_for_SkE/{lang_iso}/{bibitem_qid}_{desctext}.txt"
        if not os.path.exists(ske_filename):
            with open(resultfile) as jsonfile:
                teijson = json.load(jsonfile)
                ske_txt = f"{teijson['abstract']} {teijson['body']}"
            with open(ske_filename, 'w') as txtfile:
                txtfile.write(ske_txt)
            print(f"Successfully stored TXT for SkE.")
        else:
            print(f"SkE TXT file is there, no need to produce it.")

        time.sleep(0.5)

with open('data/missing_tei_list.json', 'w') as jsonfile:
    json.dump(missing_tei_list, jsonfile)
