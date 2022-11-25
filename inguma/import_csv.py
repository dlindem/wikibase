import csv
import iwbi

with open ('data/deathdate_from_wikidata.csv') as file:
	importcsv = csv.DictReader(file)
	for row in importcsv:
		# itemdata = {'qid':row['wikibase_item'],'statements':[{'type':'externalid','value':row['viaf'],'prop_nr':'P43','action':'replace'}]}
		itemdata = {'qid':row['wikibase_item'].replace(iwbi.entity_prefix,''),
		'statements':[{'type':'time','value':row['time'],'precision':row['precision'],'prop_nr':'P45','action':'replace'}],
		'references':[{'type':'externalid','prop_nr':'P1','value':row['wd_item'].replace('http://www.wikidata.org/entity/','')}]}
		iwbi.itemwrite(itemdata)
