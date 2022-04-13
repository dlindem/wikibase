import csv
import json
import iwbi
import time

print('___________________________\n')
with open('D:/Inguma/authors_orcid.csv', 'r', encoding="utf-8") as csvfile:
	persons = csv.DictReader(csvfile)

	for person in persons:
		print('Getting data for: '+person['wikibase_item'])
		query = 'select ?wduri WHERE {?wduri wdt:P496 "'+person['orcid']+'" .}' # filter not exists{?wikibase_item idp:P1 ?wd.}
		bindings = iwbi.wbi_helpers.execute_sparql_query(query=query, endpoint="https://query.wikidata.org/sparql", user_agent=iwbi.wd_user_agent)['results']['bindings']
		if len(bindings) > 0:
			wdqid = bindings[0]['wduri']['value'].replace("http://www.wikidata.org/entity/","")
			print('Found wikidata item: '+wdqid)
		else:
			wdqid = None
			print('No result on WD for: '+person['wikibase_item'])

		if wdqid:
			iwbitem = iwbi.wbi.item.get(entity_id=person['wikibase_item'])
			print('IWB item is: '+iwbitem.labels.get('eu').value)
			#wdqid = iwbitem.claims.get('P1')[0].mainsnak.datavalue['value']
			#print('wikidata item is: '+wdqid)
			statements = []
			statements.append(iwbi.ExternalID(value=wdqid, prop_nr="P1"))
			statements.append(iwbi.Item(value="Q5", prop_nr="P5"))
			iwbitem.claims.add(statements)
			iwbitem.write()
			print('new data written to iwb.')
