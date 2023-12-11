import sys, os, time, csv, re

sys.path.insert(1, os.path.realpath(os.path.pardir))
os.chdir(os.path.realpath(os.path.pardir))
import euswbi

lexlangprops = {'eu': 'P8', 'es':'P93', 'en': 'P94'}
desclangprops = {'eu': 'P13', 'es':'P95', 'en': 'P96'}
schemeqid = 'Q3766'

# load item mappings from file
with open('data/wdmapping.csv') as csvfile:
	mappingcsv = csvfile.read().split('\n')
	itemwd2wb = {}
	itemwb2wd = {}
	for row in mappingcsv:
		mapping = row.split('\t')
		if len(mapping) == 2:
			itemwb2wd[mapping[0]] = mapping[1]
			itemwd2wb[mapping[1]] = mapping[0]

with open('koloreak/koloreak.tsv', 'r', encoding="utf-8") as csvfile:
    csvrows = csv.DictReader(csvfile, delimiter="\t")

    for row in csvrows:
        print(str(row))
        wdqid = row['Wikidata'].strip()
        wbqid = itemwd2wb[wdqid]
        label_berria = row['labelBerria'].strip().lower()
        agertokia = row['agertokia'].strip()
        testuingurua = row['testuingurua'].strip()
        if len(testuingurua) > 1:
            qualifiers = [{'prop_nr': 'P10', 'type': 'string', 'value': testuingurua}]
        else:
            qualifiers = []
        if agertokia.startswith('http'):
            qualifiers.append({'prop_nr': 'P9', 'type': 'url', 'value': agertokia})
        else:
            qualifiers.append({'prop_nr': 'P11', 'type': 'string', 'value': agertokia})
        statements = [{'prop_nr': 'P8', 'type': 'string', 'value': label_berria,
                           'qualifiers': qualifiers,
                          'action': 'replace'}]
        labels = [{'lang': 'eu', 'value': label_berria}]

        wbqid = euswbi.itemwrite(
            {'qid': wbqid, 'statements': statements, 'labels': labels})
        time.sleep(1)