import os, re, csv, time
import config_private
from pyzotero import zotero
pyzot = zotero.Zotero(config_private.zotero_group_nr, 'group', config_private.zotero_api_key)

collection = {}
with open ('data/subcorpus_collection.csv', encoding='utf-8') as file:
    csvcontent = csv.DictReader(file, delimiter=",")
    for row in csvcontent:
        print(row)
        collection[row['qid']] = row['\ufeffZotero']

for (root, dirs, files) in os.walk('/media/david/FATdisk/ENEOLI/NeoCorpus_TXT_for_SkE/'):
    print(root, dirs, files)
    lang_re = re.search(r'/([a-z]{3})$', root)
    if lang_re and len(files) > 0:
        lang = lang_re.group(1)
        for filename in files:
            text_qid_re = re.search(r'^Q\d+', filename)
            if text_qid_re and text_qid_re.group(0) in collection:
                source = f"/media/david/FATdisk/ENEOLI/NeoCorpus_TXT_for_SkE/{lang}/{filename}"
                target = f"/media/david/FATdisk/ENEOLI/NeoCorpus_TXT_for_SkE/blending_subcorpus/{lang}_{filename}"
                os.system(f"cp {source} {target}")
                print('copied file.')
                del collection[text_qid_re.group(0)]
    else:
        print(f"Skipped folder {root}.")

input(f"Press ENTER for writing tag to missing items:\n{collection}.")
for qid in collection:
    zotitem = pyzot.item(collection[qid])
    zotitem = pyzot.add_tags(zotitem, 'failed_fulltext_processing')
    print(f"Added 'failed_fulltext_processing' tag to {qid} ({collection[qid]}).")

