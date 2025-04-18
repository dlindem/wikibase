import csv
import re
import requests

import euswbi

allowed_props_to_import = ['P5', 'P4', 'P3']

def write_wdmapping(wdqid=None, wbqid=None):
	if wdqid and wbqid:
		with open('data/wdmapping.csv', 'a', encoding="utf-8") as csvfile:
			csvfile.write(wbqid + '\t' + wdqid + '\n')


def importitem(importqid, wbqid=False, process_claims=False, process_labels=True, process_aliases=True, process_defs=True, process_sitelinks=True, schemeqid=None, instanceqid=None): #process_claims can be a list with allowed wb properties
	languages_to_consider = "eu es en de fr".split(" ")
	global itemwd2wb
	global itemwb2wd
	global propwd2wb
	global propwb2wd
	global propwbdatatype

	if wbqid:
		wb_existing_item = euswbi.wbi.item.get(wbqid)
	else:
		wb_existing_item = None

	print('Will get ' + importqid + ' from wikidata...')
	# importitem = euswbi.wdi.item.get(entity_id=importqid, user_agent=euswbi.wd_user_agent)
	# importitemjson = importitem.get_json()
	apiurl = 'https://www.wikidata.org/w/api.php?action=wbgetentities&ids=' + importqid + '&format=json'
	# print(apiurl)
	wdjsonsource = requests.get(url=apiurl)
	if importqid in wdjsonsource.json()['entities']:
		importitemjson = wdjsonsource.json()['entities'][importqid]
	else:
		print('Error: Recieved no valid item JSON from Wikidata.')
		return False

	wbitemjson = {'labels': [], 'aliases': [], 'descriptions': [],
				  'statements': [{'prop_nr': 'P1', 'type': 'externalid', 'value': importqid}]}
	if schemeqid:
		wbitemjson['statements'].append({'prop_nr': 'P6', 'type': 'Item', 'value': schemeqid})
	if instanceqid:
		wbitemjson['statements'].append({'prop_nr': 'P5', 'type': 'Item', 'value': instanceqid})
	if not wbqid and importqid in itemwd2wb:
		wbqid = itemwd2wb[importqid]  # item exists and is in mapping file
		wb_existing_item = euswbi.wbi.item.get(wbqid)

	# process labels
	if process_labels:
		for lang in languages_to_consider:
			if wbqid:
				existing_preflabel = wb_existing_item.labels.get(lang)
			else:
				existing_preflabel = None
			if lang in importitemjson['labels']:
				if existing_preflabel:
					if importitemjson['labels'][lang]['value'] != existing_preflabel:
						wbitemjson['aliases'].append({'lang': lang, 'value': importitemjson['labels'][lang]['value']})
				else:
					wbitemjson['labels'].append({'lang': lang, 'value': importitemjson['labels'][lang]['value']})
	# process aliases
	if process_aliases:
		for lang in languages_to_consider:
			if wbqid:
				existing_aliases = wb_existing_item.aliases.get(lang)
				if not existing_aliases:
					existing_aliases = []
				for alias in existing_aliases:
					wbitemjson['aliases'].append({'lang': lang, 'value': alias.value})
			else:
				existing_aliases = []
			if lang in importitemjson['aliases']:
				for entry in importitemjson['aliases'][lang]:
					if entry['value'] not in existing_aliases:
						wbitemjson['aliases'].append({'lang': lang, 'value': entry['value']})
	# process descriptions
	if process_defs:
		for lang in importitemjson['descriptions']:
			if lang in languages_to_consider:
				if {'lang': lang, 'value': importitemjson['descriptions'][lang]['value']} not in wbitemjson['labels']:
					wbitemjson['descriptions'].append(
						{'lang': lang, 'value': importitemjson['descriptions'][lang]['value']})
	# process claims
	if process_claims:
		for claimprop in importitemjson['claims']:
			if claimprop in propwd2wb:  # aligned prop
				wbprop = propwd2wb[claimprop]
				# delete the following two lines for importing all aligned properties' values
				if isinstance(process_claims, list):
					if wbprop not in process_claims:
						continue
				for claim in importitemjson['claims'][claimprop]:
					claimval = claim['mainsnak']['datavalue']['value']
					if propwbdatatype[wbprop] == "WikibaseItem":
						if claimval['id'] not in itemwd2wb:
							print(
								'Will create a new item for ' + claimprop + ' (' + wbprop + ') object property value: ' +
								claimval['id'])
							targetqid = importitem(claimval['id'], process_claims=False) # property target object to be imported without statements
						else:
							targetqid = itemwd2wb[claimval['id']]
							print('Will re-use existing item as property value: wd:' + claimval[
								'id'] + ' > eusterm:' + targetqid)
						statement = {'prop_nr': wbprop, 'type': 'Item', 'value': targetqid}
					else:
						statement = {'prop_nr': wbprop, 'type': propwbdatatype[wbprop], 'value': claimval,
									 'action': 'keep'}
					statement['references'] = [{'prop_nr': 'P1', 'type': 'externalid', 'value': importqid}]
				wbitemjson['statements'].append(statement)
	# process sitelinks
	if process_sitelinks:
		if 'sitelinks' in importitemjson:
			for site in importitemjson['sitelinks']:
				if site.replace('wiki', '') in languages_to_consider:
					wpurl = "https://"+site.replace('wiki', '')+".wikipedia.org/wiki/"+importitemjson['sitelinks'][site]['title'].replace(" ","_")
					print(wpurl)
					wbitemjson['statements'].append({'prop_nr':'P7','type':'url','value':wpurl})

	wbitemjson['qid'] = wbqid  # if False, then create new item
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
query = """select ?item ?wd ?datatype where {
  ?item a wikibase:Property; wikibase:propertyType ?datatype; eusdp:P1 ?wd.}
group by ?item ?wd ?datatype
"""
bindings = euswbi.wbi_helpers.execute_sparql_query(query=query, endpoint=euswbi.wbi_config['SPARQL_ENDPOINT_URL'],
												   prefix=euswbi.sparql_prefixes)['results']['bindings']
print('Found ' + str(len(bindings)) + ' wikidata links for the query.\n')
propwd2wb = {}
propwb2wd = {}
propwbdatatype = {}
for binding in bindings:
	euswbqid = binding['item']['value'].replace('https://eusterm.wikibase.cloud/entity/', '')
	if euswbqid not in propwb2wd:
		propwb2wd[euswbqid] = [binding['wd']['value']]
	else:
		propwb2wd[euswbqid].append(binding['wd']['value'])
	propwd2wb[binding['wd']['value']] = euswbqid
	propwbdatatype[euswbqid] = binding['datatype']['value'].replace('http://wikiba.se/ontology#', '')

# load items to import
with open('data/wikidata-import.csv', 'r') as file:
	importlist = csv.DictReader(file, delimiter="\t")
	seenqid = []
	for row in importlist:
		if not re.search('^Q[0-9]+', row['Wikidata']):
			continue
		if row['Wikidata'] in seenqid:
			continue
		print('Will now import: ' + str(row))
		# presskey = input('Proceed?')
		print('Successfully processed: ' + importitem(row['Wikidata'], process_claims=allowed_props_to_import, schemeqid=row['Scheme'], instanceqid=None))
		seenqid.append(row['Wikidata'])

# # load openrefine alignment CSV
# with open('data/wd_to_eusterm.csv', 'r', encoding='utf-8') as csvfile:
# 	importlist = csv.DictReader(csvfile, delimiter=",")
# 	seenqid = []
# 	for row in importlist:
# 		eustermid = row['concept'].replace('https://eusterm.wikibase.cloud/entity/','')
# 		print(f"\nWill now process {eustermid}")
# 		for key in row:
# 			if key.lower().startswith('wikidata'):
# 				wdqid = row[key].strip()
# 				if wdqid.startswith('Q'):
# 					if wdqid not in seenqid:
# 						print(
# 							'Successfully processed: ' + str(importitem(wdqid, wbqid=eustermid, process_claims=False,
# 																	schemeqid=None, instanceqid=None, process_defs=True, process_aliases=True, process_labels=True, process_sitelinks=False)))
# 						seenqid.append(wdqid)

# print('Successfully processed: ' + importitem("Q842254", wbqid="Q6757", process_claims=allowed_props_to_import, schemeqid=None, instanceqid=None))