# This imports and overwrites labels Q-items with the same P1 (Wikidata Entity) value from Wikidata

import sys, clbwbi

classes_to_consider = "clbwb:Q4"  #"clbwb:Q17 clbwb:Q8"
languages_to_consider = "'cs' 'en' 'de' 'pl'"

print('Querying clb-lod Wikibase for items with P1 value')
query = """select ?item ?wduri where {
  ?item clbdp:P5 ?class; clbdp:P1 ?wd.
  VALUES ?class {"""+classes_to_consider+"""}
  BIND (concat("http://www.wikidata.org/entity/",?wd) as ?wduri)
}
group by ?item ?wduri
"""
bindings = clbwbi.wbi_helpers.execute_sparql_query(query=query, prefix=clbwbi.sparql_prefixes)['results']['bindings']
print('Found '+str(len(bindings))+' wikidata links for the query.\n')
count = 0
for binding in bindings:
	count += 1
	clbwbqid = binding['item']['value'].replace('https://clb-lod.wikibase.cloud/entity/','')
	if clbwbqid.startswith('Q'):
		clbwbitem = clbwbi.wbi.item.get(entity_id=clbwbqid)
	elif clbwbqid.startswith('P'):
		clbwbitem = clbwbi.wbi.property.get(entity_id=clbwbqid)
	print('['+str(count)+'] Processing clbwb '+clbwbqid+'...')
	wdqid = binding['wduri']['value'].replace('http://www.wikidata.org/entity/','')
	print('Querying Wikidata for wd:'+wdqid+'...')
	wdprops = ['rdfs:label', 'skos:altLabel', 'schema:description']
	for wdprop in wdprops:
		query = "select ?string ?lang where {wd:"+wdqid+" "+wdprop+" ?string. bind (lang(?string) as ?lang) values ?lang {"+languages_to_consider+"} }"
		wdbindings = clbwbi.wbi_helpers.execute_sparql_query(query=query, endpoint="https://query.wikidata.org/sparql", user_agent=clbwbi.wd_user_agent)['results']['bindings']
		for wdbinding in wdbindings:
			lang = wdbinding['lang']['value']
			stringval = wdbinding['string']['value']
			print('Found wikidata ',wdprop,lang,stringval)
			if wdprop == 'rdfs:label':
				clbwbitem.labels.set(lang,stringval)
			elif wdprop == 'skos:altLabel':
				clbwbitem.aliases.set(lang,stringval)
			elif wdprop == 'schema:description':
				clbwbitem.descriptions.set(lang,stringval)

	clbwbitem.write(summary="Labels, aliases, descs imported from Wikidata for "+languages_to_consider)
	print('Finished writing to clbwb '+clbwbitem.id+'\n')
