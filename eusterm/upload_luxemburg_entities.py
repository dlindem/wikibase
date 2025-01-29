import json, csv, euswbi, time

with open('luxemburg/data/wd_mapping.csv') as csvfile:
    mappingrows = csv.DictReader(csvfile, delimiter=",")
    mapping = {}
    for row in mappingrows:
        mapping[row['wikidata']] = row['eusterm']

with open('luxemburg/data/annotations.json') as file:
    annotations = json.load(file)['wikidata']

for annotation in annotations:
    eustermqid = mapping[annotation.replace("http://www.wikidata.org/entity/", "")]
    print(f"\nNow processing: https://eusterm.wikibase.cloud/entity/{eustermqid}")

    english = annotations[annotation]
    print(english)
    statements = []
    action = 'replace'
    for word in english:
        freq = str(english[word])
        print(f"{word}: {freq}")
        statements.append({"action": action, "prop_nr": "P171", "type": "string", "value": word, "qualifiers":[{"prop_nr": "P172", "type": "string", "value": freq}, {"prop_nr": "P17", "type": "item", "value": "Q18730"}]})
        if action == 'replace':
            euswbi.itemwrite({'qid': eustermqid, 'statements': statements})
            action = 'append'
            statements = []
            time.sleep(0.5)
    if action == 'append':
        euswbi.itemwrite({'qid': eustermqid, 'statements': statements})
        time.sleep(0.5)
