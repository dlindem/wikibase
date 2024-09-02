import json, csv, requests, sys, re, time
import config_private, iwb
from pyzotero import zotero

pyzot = zotero.Zotero(config_private.zotero_group_nr, 'group', config_private.zotero_api_key)

with open('data/zotero_oocc.csv') as csvfile:
    mapping = csv.DictReader(csvfile, delimiter="\t")
    for row in mapping:
        print(row)
        zotitem = pyzot.item(row['\ufeffkey'])
        zotitem['data']['archiveLocation'] = row['oocc']
        pyzot.update_item(zotitem)
        time.sleep(0.1)

