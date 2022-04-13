import csv
import json
import iwbi
import time

print('___________________________\n')
with open('D:/Inguma/wduri_inumga_wdqid.csv', 'r', encoding="utf-8") as csvfile:
	persons = csv.DictReader(csvfile)

	for person in persons:
		print('Getting data for: '+person['inguma'])
		query = 'select ?wikibase_item ?wd where {?wikibase_item idp:P3 "'+person['inguma']+'". OPTIONAL {?wikibase_item idp:P1 ?wd.} }'
		bindings = iwbi.wbi_helpers.execute_sparql_query(query=query, prefix=iwbi.sparql_prefixes)['results']['bindings']
		if len(bindings) > 0:
			iwbqid = bindings[0]['wikibase_item']['value'].replace("http://wikibase.inguma.eus/entity/","")
			print('Found wikibase item: '+iwbqid)
			if "wd" in bindings[0]:
				if bindings[0]['wd']['value'].startswith("Q"):
					wdqid = bindings[0]['wd']['value']
					print('Found existing P1 statement: '+wdqid+'.')
					continue
		else:
			iwbqid = None
			print('No result on IWB for: '+person['inguma'])

		if iwbqid:
			iwbitem = iwbi.wbi.item.get(entity_id=iwbqid)
			print('IWB item we will write to: '+iwbitem.labels.get('eu').value)
			statements = []
			statements.append(iwbi.ExternalID(value=person['wdqid'], prop_nr="P1"))
			statements.append(iwbi.Item(value="Q5", prop_nr="P5"))
			iwbitem.claims.add(statements)
			iwbitem.write()
			print('new data written to iwb.')
