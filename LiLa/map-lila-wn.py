import csv, json, re
from data import pwn_mapping

with open('data/LiLa_wordnet.csv') as csvfile:
    csvdict = csv.DictReader(csvfile)
    lila_wn = {}
    for row in csvdict:
        # normalize wn30 id
        wn30 = re.sub('http://wordnet-rdf.princeton.edu/wn30/0*','',row['synset'])
        lila_wn[wn30] = row

with open('data/wikidata_wordnet.csv') as csvfile:
    csvdict = csv.DictReader(csvfile)
    wd_wn = {}
    for row in csvdict:
        wd_wn[row['wn31norm']] = row

found_mappings = {}
for wn31norm in wd_wn:
    # print(wn31norm)
    normre = re.search('(\d+)\-([a-z])', wn31norm)
    wn31num = normre.group(1)
    wn31pos = normre.group(2)
    lookup = wn31pos + wn31num
    if lookup in pwn_mapping.wn31to30:
        wn30 = pwn_mapping.wn31to30[lookup]
        print(f'Converted Wikidata wn31 {lookup} to wn30 {wn30}.')
        normre = re.search('([a-z])(\d+)', wn30)
        wn30num = normre.group(2)
        wn30pos = normre.group(1)
        lilalookup = wn30num + "-" + wn30pos
        if lilalookup in lila_wn:
            print('Found ',str(lila_wn[lilalookup]))
            found_mappings[wd_wn[wn31norm]['wd_item']] = {'lilalem': lila_wn[lilalookup]['lemma_id'], 'lilasense': lila_wn[lilalookup]['sense']}

print(f'Found {str(len(found_mappings))} mappings.')

with open('data/lilasense_wd_mappings.json', 'w') as jsonfile:
    json.dump(found_mappings, jsonfile, indent=2)
