import euswbi, get_wikidata_labels
import json, re, time, csv, sys, requests

def getwikidatajson(importqid):
	print('Will get '+importqid+' from wikidata...')
	apiurl = 'https://www.wikidata.org/w/api.php?action=wbgetentities&ids='+importqid+'&format=json'
	#print(apiurl)
	wdjsonsource = requests.get(url=apiurl)
	if importqid in wdjsonsource.json()['entities']:
		return  wdjsonsource.json()['entities'][importqid]
	else:
		print('Error: Recieved no valid item JSON from Wikidata.')
		return False

schemeqid = "Q208"
wdprop_to_import = "P6262"

# load prop aligned to wdprop_to_import
print('Querying for eusterm prop equivalent to '+wdprop_to_import+'...')
query = 'select ?prop where {?prop eusdp:P1 "'+wdprop_to_import+'".}'
bindings = euswbi.wbi_helpers.execute_sparql_query(query=query, endpoint=euswbi.wbi_config['SPARQL_ENDPOINT_URL'], prefix=euswbi.sparql_prefixes)['results']['bindings']
print('Found '+str(len(bindings))+' wikidata alignment.\n')
if len(bindings) == 0:
	newprop = euswbi.wbi.property.new()
	newprop.claims.add([euswbi.ExternalID(value=wdprop_to_import,prop_nr='P1')])
	newprop.labels.set('eu', 'propietate berria')
	newprop.write() #newprop.write(summary="Property created as equivalent to wikidata "+wdprop_to_import+".")
	print('Successfully created '+newprop.id+'. Will not get labels, etc., from Wikidata...')
	get_wikidata_labels.import_wd_labels(wdid=wdprop_to_import, wbid=newprop.id)
	wbprop = newprop.id
elif len(bindings) == 1:
	wbprop = bindings[0]['prop']['value'].replace("https://eusterm.wikibase.cloud/entity/","")
else:
	print('Error. This prop exists more than once on euswb.')
	sys.exit()
print('euswb prop is '+wbprop)
# load wd mappings for the scheme
print('Querying for eusterm scheme '+schemeqid+' P1 wikidata alignment...')
query = "select ?concept ?wikidata where { ?concept eusdp:P6 euswb:"+schemeqid+"; eusdp:P1 ?wikidata. }"
bindings = euswbi.wbi_helpers.execute_sparql_query(query=query, endpoint=euswbi.wbi_config['SPARQL_ENDPOINT_URL'], prefix=euswbi.sparql_prefixes)['results']['bindings']
print('Found '+str(len(bindings))+' wikidata alignments.\n')
mappings = {}
for binding in bindings:
	# importjson = None
	# while not importjson:
	# 	importjson = getwikidatajson(binding['wikidata']['value'])
	# print(str(importjson))
	wbqid = binding['concept']['value'].replace("https://eusterm.wikibase.cloud/entity/","")
	wdqid = binding['wikidata']['value']
	mappings[wdqid] = wbqid
#get wikidata statements
query = """PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
select * where {
?wditem wdt:"""+wdprop_to_import+""" ?value.
values ?wditem {wd:"""+" wd:".join(list(mappings.keys()))+"""}
}
"""
#print(query)
wdbindings = euswbi.wbi_helpers.execute_sparql_query(query=query, endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql", user_agent=euswbi.wd_user_agent)['results']['bindings']
#print(str(wdbindings))
for binding in wdbindings:
	# {'wditem': {'type': 'uri', 'value': 'http://www.wikidata.org/entity/Q6636'}, 'value': {'type': 'literal', 'value': 'homoit0000647'}}
	qid = mappings[binding['wditem']['value'].replace("http://www.wikidata.org/entity/","")]
	statements = [{'type':'externalid','value':binding['value']['value'],'prop_nr':wbprop}]
	euswbi.itemwrite({'qid':qid,'statements':statements})

sys.exit()






def write_wdmapping(wdqid=None, wbqid=None):
	if wdqid and wbqid:
		with open('data/wdmapping.csv', 'a', encoding="utf-8") as csvfile:
			csvfile.write(wbqid+'\t'+wdqid+'\n')

def importitem(importqid, process_claims=True, schemeqid=None, instanceqid=None):

	languages_to_consider = "eu es en de fr".split(" ")
	global itemwd2wb
	global itemwb2wd
	global propwd2wb
	global propwb2wd
	global propwbdatatype

	print('Will get '+importqid+' from wikidata...')
	# importitem = euswbi.wdi.item.get(entity_id=importqid, user_agent=euswbi.wd_user_agent)
	# importitemjson = importitem.get_json()
	apiurl = 'https://www.wikidata.org/w/api.php?action=wbgetentities&ids='+importqid+'&format=json'
	#print(apiurl)
	wdjsonsource = requests.get(url=apiurl)
	if importqid in wdjsonsource.json()['entities']:
		importitemjson =  wdjsonsource.json()['entities'][importqid]
	else:
		print('Error: Recieved no valid item JSON from Wikidata.')
		return False

	wbitemjson = {'labels':[], 'aliases':[], 'descriptions':[], 'statements':[{'prop_nr':'P1','type':'externalid','value':importqid}]}
	if schemeqid:
		wbitemjson['statements'].append({'prop_nr':'P6','type':'Item','value':schemeqid})
	if instanceqid:
		wbitemjson['statements'].append({'prop_nr':'P5','type':'Item','value':instanceqid})
	if importqid in itemwd2wb:
		wbqid = itemwd2wb[importqid] # item exists
		# return wbqid
	else:
		wbqid = False # will create new item

	# process labels
	for lang in importitemjson['labels']:
		if lang in languages_to_consider:
			wbitemjson['labels'].append({'lang':lang, 'value': importitemjson['labels'][lang]['value']})
	# process aliases
	for lang in importitemjson['aliases']:
		if lang in languages_to_consider:
			for entry in importitemjson['aliases'][lang]:
				# print('Alias entry: '+str(entry))
				wbitemjson['aliases'].append({'lang':lang, 'value':entry['value']})
	# process descriptions
	for lang in importitemjson['descriptions']:
		if lang in languages_to_consider:
			if {'lang':lang ,'value':importitemjson['descriptions'][lang]['value']} not in wbitemjson['labels']:
				wbitemjson['descriptions'].append({'lang':lang, 'value': importitemjson['descriptions'][lang]['value']})

	# process claims
	if process_claims:
		for claimprop in importitemjson['claims']:
			if claimprop in propwd2wb: # aligned prop
				wbprop = propwd2wb[claimprop]
				for claim in importitemjson['claims'][claimprop]:
					claimval = claim['mainsnak']['datavalue']['value']
					if propwbdatatype[wbprop] == "WikibaseItem":
						if claimval['id'] not in itemwd2wb:
							print('Will create a new item for '+claimprop+' ('+wbprop+') object property value: '+claimval['id'])
							targetqid = importitem(claimval['id'], process_claims=False)
						else:
							targetqid = itemwd2wb[claimval['id']]
							print('Will re-use existing item as property value: wd:'+claimval['id']+' > eusterm:'+targetqid)
						statement = {'prop_nr':wbprop,'type':'Item','value':targetqid}
					else:
						statement = {'prop_nr':wbprop,'type':propwbdatatype[wbprop],'value':claimval,'action':'keep'}
					statement['references'] = [{'prop_nr':'P1','type':'externalid','value':importqid}]
				wbitemjson['statements'].append(statement)
	# process sitelinks
	# if 'sitelinks' in importitemjson:
	# 	for site in importitemjson['sitelinks']:
	# 		if site.replace('wiki', '') in languages_to_consider:
	# 			wpurl = "https://"+site.replace('wiki', '')+".wikipedia.org/wiki/"+importitemjson['sitelinks'][site]['title']
	# 			print(wpurl)
	# 			wbitemjson['statements'].append({'prop_nr':'P7','type':'url','value':wpurl})

	wbitemjson['qid'] = wbqid # if False, then create new item
	result = euswbi.itemwrite(wbitemjson)
	if result and result not in itemwb2wd:
		itemwb2wd[result] = importqid
		itemwd2wb[importqid] = result
		write_wdmapping(wdqid=importqid, wbqid=result)
	return result

# load item mappings from file
with open('data/wdmapping.csv') as csvfile:
	mappingcsv = csvfile.read().split('\n')
	itemwd2wb = {}
	itemwb2wd = {}
	for row in mappingcsv:
		mapping = row.split('\t')
		if len(mapping) == 2:
			itemwb2wd[mapping[0]] = mapping[1]
			itemwd2wb[mapping[1]] = mapping[0]

# load prop mappings from sparql
print('Querying eusterm Wikibase for properties with P1 wikidata alignment...')
query = "select ?concept ?wikidata where { ?concept eusdp:P6 euswb:Q208; eusdp:P1 ?wikidata. }"
bindings = euswbi.wbi_helpers.execute_sparql_query(query=query, endpoint=euswbi.wbi_config['SPARQL_ENDPOINT_URL'], prefix=euswbi.sparql_prefixes)['results']['bindings']
print('Found '+str(len(bindings))+' wikidata links for the query.\n')
propwd2wb = {}
propwb2wd = {}
propwbdatatype = {}
for binding in bindings:
	euswbqid = binding['item']['value'].replace('https://eusterm.wikibase.cloud/entity/','')
	if euswbqid not in propwb2wd:
		propwb2wd[euswbqid] = [binding['wd']['value']]
	else:
		propwb2wd[euswbqid].append(binding['wd']['value'])
	propwd2wb[binding['wd']['value']] = euswbqid
	propwbdatatype[euswbqid] = binding['datatype']['value'].replace('http://wikiba.se/ontology#','')

# load items to import
with open('data/wikidata-import.csv', 'r') as file:
	importlist = csv.DictReader(file, delimiter="\t")
	seenqid = []
	for row in importlist:
		if not re.search('^Q[0-9]+', row['Wikidata']):
			continue
		if row['Wikidata'] in seenqid:
			continue
		print('Will now import: '+str(row))
		# presskey = input('Proceed?')
		print('Successfully processed: '+importitem(row['Wikidata'], schemeqid=row['Scheme'], instanceqid=None))
		seenqid.append(row['Wikidata'])
