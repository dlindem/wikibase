import time
import sys
import json
import csv
import lwbi


print('\nWill get dictionary distributions and any existing P55 link pointing to them.')

query = """
select ?uri (str(?label) as ?title) ?lcr where
{?uri ldp:P5 lwb:Q24; rdfs:label ?label. filter(lang(?label)="en") # Q24: Dictionary Distribution
 OPTIONAL { ?lcr ldp:P55 ?uri .}
 } group by ?uri ?label ?lcr
"""
print("Waiting for LexBib v3 SPARQL...")
bindings = lwbi.wbi_helpers.execute_sparql_query(query=query, prefix=lwbi.sparql_prefixes)['results']['bindings']
print('Found '+str(len(bindings))+' results to process.\n')
count = 0
for item in bindings:
	count += 1
	distrqid = item['uri']['value'].replace('https://lexbib.elex.is/entity/','')
	title = item['title']['value']
	print('\nNow processing:',distrqid,title)
	if 'lcr' in item:
		lcrqid = item['lcr']['value'].replace('https://lexbib.elex.is/entity/','')
		print('Found P55 link for this dictionary distribution. LCR is '+lcrqid)
	else:
		print('No P55 link for this dictionary distribution. Will create a new Q4 item.')
		lcrqid = lwbi.itemwrite({'qid':False,
		'labels': [{'lang': 'en', 'value': title}],
		'statements': [{'prop_nr': 'P5', 'type': 'item', 'value':'Q4'},
					   {'prop_nr': 'P55', 'type': 'item', 'value':distrqid}]})
