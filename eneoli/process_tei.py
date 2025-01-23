import csv, json, time, os, sys, re
import nlp
import config_private
from pyzotero import zotero
pyzot = zotero.Zotero(config_private.zotero_group_nr, 'group', config_private.zotero_api_key)

overwrite_existing_json = False
missing_tei_list = []
disappeared_items = "Qid\tZotero\n"

# with open('data/fulltext_items.csv') as file:
#     rows = csv.DictReader(file, delimiter=",")
#     for row in rows:

import requests

print("Getting data from Wikibase...")
r = requests.get("https://eneoli.wikibase.cloud/query/sparql?format=json&query=PREFIX%20enwb%3A%20%3Chttps%3A%2F%2Feneoli.wikibase.cloud%2Fentity%2F%3E%0APREFIX%20endp%3A%20%3Chttps%3A%2F%2Feneoli.wikibase.cloud%2Fprop%2Fdirect%2F%3E%0APREFIX%20enp%3A%20%3Chttps%3A%2F%2Feneoli.wikibase.cloud%2Fprop%2F%3E%0APREFIX%20enps%3A%20%3Chttps%3A%2F%2Feneoli.wikibase.cloud%2Fprop%2Fstatement%2F%3E%0APREFIX%20enpq%3A%20%3Chttps%3A%2F%2Feneoli.wikibase.cloud%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20%3Fitem_id%20%3Fparent_id%20%3Fpdf_id%20%3Fiso%20(sample(%3Fdesc)%20as%20%3Fdescription)%0A%0Awhere%20%7B%0A%20%20%3Fitem%20endp%3AP5%20enwb%3AQ2%3B%20enp%3AP17%20%3Fzotst.%20%3Fzotst%20enps%3AP17%20%3Fparent_id%3B%20enpq%3AP20%20%3Fpdf_id.%0A%20%20%3Fitem%20endp%3AP7%20%3Flang.%20%3Flang%20endp%3AP50%20%3Fiso.%20%23%20filter(%3Fiso%3D%22fra%22)%20%23%20lang%20fr%0A%20%20%23%20%3Fitem%20endp%3AP6%20enwb%3AQ9.%20%23%20type%20journal%20article%0A%20%20%3Fitem%20schema%3Adescription%20%3Fdesc.%0A%20%20bind(strafter(str(%3Fitem)%2Cstr(enwb%3A))%20as%20%3Fitem_id)%0A%0A%7D%20group%20by%20%3Fitem_id%20%3Fparent_id%20%3Fpdf_id%20%3Fiso%20%3Fdescription%20order%20by%20%3Fiso")
fulltext_items = r.json()['results']['bindings']
count = 0
for row in fulltext_items:
    count += 1
    print(f"\n[{count} of {len(fulltext_items)}]")
    parent_id = row['parent_id']['value']
    pdf_id = row['pdf_id']['value']
    bibitem_qid = row['item_id']['value']
    lang_iso = row['iso']['value']
    desctext = re.sub(r'[^\w\-_]', '' ,row['description']['value'].strip().replace(" ","_"))
    teijson = None
    xmlfile = f"/media/david/FATdisk/ENEOLI/eneoli_fulltext_{bibitem_qid}.tei.xml"
    resultfile = f"/media/david/FATdisk/ENEOLI/eneoli_fulltext_{bibitem_qid}.json"
    ske_filename = f"/media/david/FATdisk/ENEOLI/NeoCorpus_TXT_for_SkE/{lang_iso}/{bibitem_qid}_{desctext.replace('Publication_by_', '')}.txt"

    print(f"\nNow processing {bibitem_qid}, Zotero {parent_id}, language is {lang_iso}.")
    try:
        zotitem = pyzot.item(parent_id)
        zotchildren = pyzot.children(parent_id)
    except Exception as ex:
        print(f"Error retrieving Zotero data for {parent_id}\n", str(ex))
        disappeared_items += f"{bibitem_qid}\t{parent_id}\n"
        time.sleep(2)
        continue
    # print(zotitem)
    # with open('data/testzotitem.json', 'w') as jsonfile:
    #     json.dump({'zotitem':zotitem, 'children':zotchildren}, jsonfile, indent=2)
    control = {'.pdf': None, '.txt': None, '.xml': None, '.json': None}
    for attachment in zotchildren:

        attkey = attachment['key']
        filext_re = None
        # if "enclosure" in attachment['links']:
        #     if 'title' not in attachment['links']['enclosure']:
        #         continue
        #     filext_re = re.search(r'\.\w+$', attachment['links']['enclosure']['title'])
        if "filename" in attachment['data']:
            filext_re = re.search(r'\.\w+$', attachment['data']['filename'])
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
    if control['.json'] and not overwrite_existing_json and os.path.isfile(ske_filename):
        print('Will skip item with existing full text json file and existing SkE text file.')
        continue

    elif overwrite_existing_json:
        try:
            delete_op = pyzot.delete_item(pyzot.item(control['.json']))
            print(f"Have deleted existing full text json file.")
            control['.json'] = None
        except:
            print(f"ERROR: No success deleting full text json file {control['json']}!!")
            time.sleep(1)

  #  else:

    if control['.txt']:
        for file in os.listdir(f"/home/david/Zotero/storage/{control['.txt']}"):
            if file.endswith(".txt"):
                txtfile = f"/home/david/Zotero/storage/{control['.txt']}/{file}"
                try:
                    with open(txtfile, encoding="utf-8") as file:
                        bodytxt = nlp.check_encoding(file.read(), control['.txt'])
                    teijson = {'abstract': '', 'body': bodytxt}
                    print('This item has TXT, have taken text from there as body.')
                except:
                    print(f"TXT file {control['.txt']} is corrupt.")
                    teijson = None

    if not teijson:

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


    if not os.path.exists(ske_filename) or control['.txt']:
        if control['.txt']:
            with open(ske_filename, 'w') as txtfile:
                txtfile.write(bodytxt)
            print(f"Successfully stored TXT for SkE from TXT.")
        elif os.path.isfile(resultfile):
            with open(resultfile) as jsonfile:
                teijson = json.load(jsonfile)
                ske_txt = f"{teijson['abstract']} {teijson['body']}"
            with open(ske_filename, 'w') as txtfile:
                txtfile.write(ske_txt)
            print(f"Successfully stored TXT for SkE from JSON.")

    else:
        print(f"SkE TXT file is there, no need to produce it.")

    teijson['abstract_lemmatized'] = nlp.lemmatize_clean(teijson['abstract'], lang=lang_iso)
    teijson['body_lemmatized'] = nlp.lemmatize_clean(teijson['body'], lang=lang_iso)

    if not teijson['body_lemmatized']:
        print(f"No spacy model for language '{lang_iso}': Lemmatization aborted.")
        time.sleep(1)
        continue


    with open(resultfile, 'w') as jsonfile:
        dumpjson = dict(sorted(teijson.items()))
        json.dump(dumpjson, jsonfile, indent=2)
    print(f"Success processing and saving {resultfile}...")
    if not os.path.isfile(ske_filename):
        if dumpjson['abstract']:
            ske_txt = dumpjson['abstract'] + " "
        else:
            ske_txt = ""
        ske_txt += dumpjson['body']
        with open(ske_filename, 'w') as txtfile:
            txtfile.write(ske_txt)
    print(f"Successfully stored TXT for SkE from JSON.")


    if not control['.json']:
        pyzot.attachment_simple([resultfile], parentid=parent_id)
        print(f"Success attaching {resultfile} to Zotero item {parent_id}...")

    try:
        pyzot.add_tags(zotitem, 'processed_fulltext')
        print(f"Success tagging Zotero item {parent_id}...")
    except:
        print(f"ERROR: No success tagging Zotero item {parent_id}!!")




    time.sleep(0.1)

with open('data/missing_tei_list.json', 'w') as jsonfile:
    json.dump(missing_tei_list, jsonfile)
with open('data/disappeared_zotero_items.csv', 'w') as csvfile:
    csvfile.write(disappeared_items)
