import csv, json, re

with open('data/lexemes_wikidata_lila.csv') as csvfile:
    csvrows = csv.DictReader(csvfile, delimiter=",")
    lilalem_wd = {}
    for row in csvrows:
        lilalem_wd[row['lila']] = row['lexeme']

with open('data/ili-map-pwn30.tab') as wn30file:
    wn30rows = csv.DictReader(wn30file, delimiter="\t")
    wn30dict = {}
    for row in wn30rows:
        wn30dict[row['ILI']] = row['wn30']
        
with open('data/ili-map-pwn31.tab') as wn31file:
    wn31rows = csv.DictReader(wn31file, delimiter="\t")
    wn31to30 = {}
    for row in wn31rows:
        print(str(row))
        wn31to30[row['wn31']] = wn30dict[row['ILI']]
    
with open('data/LiLa_wordnet.csv') as csvfile:
    csvdict = csv.DictReader(csvfile)
    lila_wn = {}
    for row in csvdict:
        # normalize wn30 id
        wn30 = re.sub('http://wordnet-rdf.princeton.edu/wn30/','',row['synset'])
        lila_wn[wn30] = row

with open('data/wikidata_wordnet.csv') as csvfile:
    csvdict = csv.DictReader(csvfile)
    wd_wn = {}
    for row in csvdict:
        wd_wn[row['wn31']] = row

found_mappings_with_lexeme = {}
found_mappings_without_lexeme = {}
for wn31 in wd_wn:
    # print(wn31norm)
    if wn31 in wn31to30:
        wn30 = wn31to30[wn31]
        print(f'Converted Wikidata wn31 {wn31} to wn30 {wn30}.')
        if wn30 in lila_wn:
            lilalem = lila_wn[wn30]['lemma_id'].replace('http://lila-erc.eu/data/id/','')
            # print('Found ',str(lila_wn[wn30]))
            if lilalem in lilalem_wd:
                found_mappings_with_lexeme[lilalem_wd[lilalem]] = {
                    'lilalem': lila_wn[wn30]['lemma_id'],
                    'lilasense': lila_wn[wn30]['sense'],
                    'wn30': lila_wn[wn30]['synset'],
                    'wn31': 'http://wordnet-rdf.princeton.edu/rdf/id/' + wn31,
                    'wd_item': wd_wn[wn31]['wd_item']
                }
            else:
                found_mappings_without_lexeme[wd_wn[wn31]['wd_item']] = {
                    'lilalem': lilalem,
                    'lilasense': lila_wn[wn30]['sense'],
                    'wn30': lila_wn[wn30]['synset'],
                    'wn31': 'http://wordnet-rdf.princeton.edu/rdf/id/' + wn31
                }

print(f'Found {str(len(found_mappings_with_lexeme))} mappings with lexeme on WD.')
print(f'Found {str(len(found_mappings_without_lexeme))} mappings without lexeme on WD.')

with open('data/lilasense_wd_mappings_lexeme.json', 'w') as jsonfile:
    json.dump(found_mappings_with_lexeme, jsonfile, indent=2)
with open('data/lilasense_wd_mappings_no_lexeme.json', 'w') as jsonfile:
    json.dump(found_mappings_without_lexeme, jsonfile, indent=2)
