import euswbi
import json, re, time, csv

with open('data/wd_qid_to_import.txt', 'r') as file:
    importqids = file.read().split('\n')

for importqid in importqids:
    importitem = euswbi.wdi.item.get(entity_id=importqid)
    importitemjson = importitem.getjson()
    print(str(importitemjson))
