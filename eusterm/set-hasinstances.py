import re

import euswbi

# load item mappings from file
with open('data/wdmapping.csv') as csvfile:
	mappingcsv = csvfile.read().split('\n')
	itemwd2wb = {}
	for row in mappingcsv:
		mapping = row.split('\t')
		if len(mapping) == 2:
			itemwd2wb[mapping[1]] = mapping[0]

# load table: wikibase item , wikidata item exactmatches
with open('data/wd-hasinstance.csv') as csvfile:
	matchcsv = csvfile.read().split('\n')
	for row in matchcsv:
		mapping = row.split(',')
		if len(mapping) != 2:
			continue
		wbitem = mapping[0]
		wditems = re.findall('Q[0-9]+', mapping[1])
		for wditem in wditems:
			if wditem not in itemwd2wb:
				print('Error: this item does not exist on Wikibase: ' + wditem)
			else:
				euswbi.itemwrite(
					{'qid': itemwd2wb[wditem], 'statements': [{'type': 'item', 'value': wbitem, 'prop_nr': 'P5'}]})
				print('Successfully set ', wbitem, ' instance of ', itemwd2wb[wditem])
