import euswbi
import json, re, time, csv, sys

#classes_to_consider = "euswb:Q4"  #"clbwb:Q17 clbwb:Q8"
languages_to_consider = "'cs' 'en' 'de' 'pl'"

# load item mappings from file
with open('data/wdmapping.csv') as csvfile:
	mappingcsv = csv.DictReader(csvfile)
	itemwd2wb = {}
	itemwb2wd = {}
	for mapping in mappingcsv:
		itemwb2wd[mapping['eusterm']] = mapping['wikidata']
		itemwd2wb[mapping]['wikidata'] = mapping['eusterm']

# load prop mappings from sparql
print('Querying eusterm Wikibase for properties with P1 wikidata alignment...')
query = """select ?item ?wd ?datatype where {
  ?item a wikibase:Property; wikibase:propertyType ?datatype; eusdp:P1 ?wd.}
group by ?item ?wd ?datatype
"""
bindings = euswbi.wbi_helpers.execute_sparql_query(query=query, endpoint=euswbi.wbi_config['SPARQL_ENDPOINT_URL'], prefix=euswbi.sparql_prefixes)['results']['bindings']
print('Found '+str(len(bindings))+' wikidata links for the query.\n')
propwd2wb = {}
propwb2wd = {}
propwbdatatype = {}
for binding in bindings:
	euswbqid = binding['item']['value'].replace('https://eusterm.wikibase.cloud/entity/','')
	propwb2wd[euswbqid] = binding['wd']['value']
	propwd2wb[binding['wd']['value']] = euswbqid
	propwbdatatype[euswbqid] = binding['datatype']['value'].replace('http://wikiba.se/ontology#','')

# load items to import
with open('data/wd_qid_to_import.txt', 'r') as file:
	importqids = file.read().split('\n')

for importqid in importqids:
	if not re.search('^Q[0-9]+', importqid):
		continue
	print('Will get '+importqid+' from wikidata...')
	importitem = euswbi.wdi.item.get(entity_id=importqid, user_agent=euswbi.wd_user_agent)
	importitemjson = importitem.get_json()
	print(str(importitemjson))
