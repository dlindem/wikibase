import lwbi

issn_log = {'0210-1564': 'Q33972'}

query = """
select ?item ?issn ?journal where {
  {?item ldp:P5 lwb:Q3.} union {?item ldp:P5 lwb:Q24.}
  ?item ldp:P20 ?issn . 
filter not exists {?item ldp:P46|ldp:P9 ?container_or_journal.}
optional {?journal ldp:P5 lwb:Q20; ldp:20 ?issn.}
}    
 """
print("Waiting for LexBib v3 SPARQL...")
bindings = lwbi.wbi_helpers.execute_sparql_query(query=query, prefix=lwbi.sparql_prefixes)['results']['bindings']
print('Found '+str(len(bindings))+' results to process.\n')
count = 0
for item in bindings:
	count += 1
	bibitemqid = item['item']['value'].replace('https://lexbib.elex.is/entity/','')
	print(f"\n[{str(count)}] Will now process bibitem {bibitemqid}...")
	if 'journal' in item:
		journalqid = item['journal']['value']
		print('This journal already exists: ',journalqid)
	elif item['issn']['value'] in issn_log:
		journalqid = issn_log[item['issn']['value']]
		print('ISSN already known from this script run: ' + journalqid)
	else:
		print('Querying Wikidata for ISSN: ' + item['issn']['value'] + '...')
		query = "select ?wd ?enlabel ?eulabel where {?wd wdt:P236 '" + item['issn']['value'] + "'. optional {?wd rdfs:label ?enlabel. filter(lang(?enlabel)='en')} optional {?wd rdfs:label ?eulabel. filter(lang(?eulabel)='eu')}}"
		bindings = lwbi.wbi_helpers.execute_sparql_query(query=query, endpoint="https://query.wikidata.org/sparql",
													user_agent="User:DL2204")['results']['bindings']
		if len(bindings) > 0:
			wdqid = bindings[0]['wd']['value'].replace("http://www.wikidata.org/entity/", "")
			if 'enlabel' in bindings[0]:
				enlabel = bindings[0]['enlabel']['value']
			if 'eulabel' in bindings[0]:
				eulabel = bindings[0]['eulabel']['value']
			print('Found wikidata item', wdqid)
		# 	wdquali = [{'type': 'ExternalID', 'value': wdqid, 'prop_nr': "P1"},
		# 			   {'type': 'monolingualtext', 'lang': 'en', 'value': wdlabel, 'prop_nr': 'P6'}]

			journalqid = lwbi.importitem(wdqid, classqid="Q20")
			issn_log[item['issn']['value']] = journalqid
			print('Created now journal: ',journalqid)
		else:
			journalqid = None
			print('Nothing found on Wikidata for this ISSN.')

	if journalqid:
		lwbi.itemwrite({'qid':bibitemqid,'statements':[{'prop_nr': 'P46', 'type': 'item', 'value': journalqid}]})
