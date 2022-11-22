# This imports and overwrites labels Q-items with the same P1 (Wikidata Entity) value from Wikidata

import sys, euswbi

# classes_to_consider = "euswb:Q4"  #"euswb:Q17 euswb:Q8"
languages_to_consider = "'eu' 'en' 'es' 'de' 'fr'"
#
# print('Querying eus-lod Wikibase for items with P1 value')
# query = """select ?item ?wduri where {
#   ?item eusdp:P5 ?class; eusdp:P1 ?wd.
#   VALUES ?class {"""+classes_to_consider+"""}
#   BIND (concat("http://www.wikidata.org/entity/",?wd) as ?wduri)
# }
# group by ?item ?wduri
# """
# bindings = euswbi.wbi_helpers.execute_sparql_query(query=query, prefix=euswbi.sparql_prefixes)['results']['bindings']
# print('Found '+str(len(bindings))+' wikidata links for the query.\n')
# count = 0
# for binding in bindings:
# 	count += 1
def import_wd_labels(wdid=None, wbid=None):
	if wbid.startswith('Q'):
		euswbitem = euswbi.wbi.item.get(entity_id=wbid)
	elif wbid.startswith('P'):
		euswbitem = euswbi.property.get(entity_id=wbid)
	print('Querying Wikidata for wd:'+wdid+'...')
	wdprops = ['rdfs:label', 'skos:altLabel', 'schema:description']
	for wdprop in wdprops:
		query = "select ?string ?lang where {wd:"+wdqid+" "+wdprop+" ?string. bind (lang(?string) as ?lang) values ?lang {"+languages_to_consider+"} }"
		wdbindings = euswbi.wbi_helpers.execute_sparql_query(query=query, endpoint="https://query.wikidata.org/sparql", user_agent=euswbi.wd_user_agent)['results']['bindings']
		for wdbinding in wdbindings:
			lang = wdbinding['lang']['value']
			stringval = wdbinding['string']['value']
			print('Found wikidata ',wdprop,lang,stringval)
			if wdprop == 'rdfs:label':
				euswbitem.labels.set(lang,stringval)
			elif wdprop == 'skos:altLabel':
				euswbitem.aliases.set(lang,stringval)
			elif wdprop == 'schema:description':
				euswbitem.descriptions.set(lang,stringval)

	euswbitem.write(summary="Labels, aliases, descs imported from Wikidata for "+languages_to_consider)
	print('Finished writing to euswb '+euswbitem.id+'\n')
