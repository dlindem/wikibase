import csv, euswbi

schemeqid = 'Q3766'

with open('data/wdmapping.csv') as csvfile:
    mapping = csv.reader(csvfile, delimiter='\t')
    wd_to_wb = {}
    for row in mapping:
        wd_to_wb[row[1]] = row[0]


with open('data/koloreak.csv') as csvfile:
    data = csv.DictReader(csvfile, delimiter='\t')
    for row in data:
        statements = []
        qualifiers = []
        # print(str(row))
        wdqid = row['wikidata']
        if wdqid not in wd_to_wb:
            continue
        wbqid = wd_to_wb[wdqid]
        write = False
        if row['testuingurua'] != '':
            qualifiers.append({'type': 'string', 'prop_nr': 'P10', 'value': row['testuingurua'].strip()})
        if row['agertokia1'] != '':
            qualifiers.append({'type': 'string', 'prop_nr':'P11', 'value': row['agertokia1'].strip()})
        if row['agertokia2'] != '':
            qualifiers.append({'type': 'string', 'prop_nr':'P11', 'value': row['agertokia2'].strip()})
        if row['labelBerria'] != '':
            statements.append({'type': 'string', 'prop_nr': 'P8', 'value': row['labelBerria'].lower().strip(), 'qualifiers':qualifiers})
        if len(statements) > 0:
            print(str(statements))
            euswbi.itemwrite({'qid': wbqid, 'statements': statements})


