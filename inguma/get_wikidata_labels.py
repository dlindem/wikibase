# This imports and overwrites labels Q-items with the same P1 (Wikidata Entity) value from Wikidata

import sys, iwbi

print('Querying Inguma Wikibase for items with P1 value')
query = """select ?item ?wduri where {
  ?item idp:P5 iwb:Q6; idp:P1 ?wd.
  BIND (concat("http://www.wikidata.org/entity/",?wd) as ?wduri)
}
group by ?item ?wduri
"""
bindings = iwbi.wbi_helpers.execute_sparql_query(query=query, prefix=iwbi.sparql_prefixes)['results']['bindings']
print('Found '+str(len(bindings))+' wikidata items for the query.\n')
count = 0
for binding in bindings:
	count += 1
	iwbqid = binding['item']['value'].replace('https://wikibase.inguma.eus/entity/','')
	print('['+str(count)+'] Processing IWB '+iwbqid+'...')
	wduri = binding['wduri']['value']
	print('Querying Wikidata for wduri: '+wduri+'...')
	query = """select
(group_concat(distinct concat(?label,"@",lang(?label));SEPARATOR="|") as ?labels)
(group_concat(distinct concat(?altlabel,"@",lang(?altlabel));SEPARATOR="|") as ?altlabels)
(group_concat(distinct concat(?desc,"@",lang(?desc));SEPARATOR="|") as ?descs)

where {<"""+wduri+"""> rdfs:label ?label. optional {<"""+wduri+"""> skos:altLabel ?altlabel.} optional {<"""+wduri+"""> schema:description ?desc.}}
"""
	wdbindings = iwbi.wbi_helpers.execute_sparql_query(query=query, endpoint="https://query.wikidata.org/sparql", user_agent=iwbi.wd_user_agent)['results']['bindings']
	iwbitem = iwbi.wbi.item.get(entity_id=iwbqid)
	for wdbinding in wdbindings:
		# labels
		langstrings = wdbinding['labels']['value'].split('|')
		for langstring in langstrings:
			lang = langstring.split('@')[1]
			stringval = langstring.split('@')[0]
			print('Found wikidata label: ',lang,stringval)
			iwbitem.labels.set(lang,stringval)
		# altlabels
		if 'altlabels' in wdbinding:
			langstrings = wdbinding['altlabels']['value'].split('|')
			for langstring in langstrings:
				lang = langstring.split('@')[1]
				stringval = langstring.split('@')[0]
				print('Found wikidata altlabel: ',lang,stringval)
				iwbitem.aliases.set(lang,stringval)
		# descriptions
		if 'descs' in wdbinding:
			langstrings = wdbinding['descs']['value'].split('|')
			for langstring in langstrings:
				lang = langstring.split('@')[1]
				stringval = langstring.split('@')[0]
				print('Found wikidata description: ',lang,stringval)
				iwbitem.descriptions.set(lang,stringval)
	iwbitem.write()
	print('Finished writing to IWB '+iwbitem.id+'\n')
