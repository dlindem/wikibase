import euswbi
import json, re, time, csv, sys, requests

# load item mappings from file
with open('data/wdmapping.csv') as csvfile:
	mappingcsv = csvfile.read().split('\n')
	itemwd2wb = {}
	for row in mappingcsv:
		mapping = row.split('\t')
		if len(mapping) == 2:
			itemwd2wb[mapping[1]] = mapping[0]

# load table: wikibase item , wikidata item exactmatches
with open('data/wd-exactmatch.csv') as csvfile:
	matchcsv = csvfile.read().split('\n')
	for row in matchcsv:
		mapping = row.split(',')
		if len(mapping) != 2:
			continue
		wbitem = mapping[0]
		wditem = mapping[1]
		if wditem not in itemwd2wb:
			print('Error: this item does not exist on Wikibase: '+wditem)
		else:
			euswbi.wbi_helpers.merge_items(from_id=itemwd2wb[wditem], to_id=wbitem, login=euswbi.login_instance)
			print('Successfully merged ',itemwd2wb[wditem], "to",wbitem)
