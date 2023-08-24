import traceback, time, re, os, requests
from pathlib import Path
from config_private import wb_bot_user
from config_private import wb_bot_pwd
from wikibaseintegrator import wbi_login, WikibaseIntegrator
from wikibaseintegrator.datatypes.string import String
from wikibaseintegrator.datatypes.externalid import ExternalID
from wikibaseintegrator.datatypes.item import Item
from wikibaseintegrator.datatypes.monolingualtext import MonolingualText
from wikibaseintegrator.datatypes.time import Time
# from wikibaseintegrator.datatypes.globecoordinate import GlobeCoordinate
from wikibaseintegrator.datatypes.url import URL
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator import wbi_helpers
from wikibaseintegrator.wbi_enums import ActionIfExists, WikibaseSnakType
from config import props_wd_wb

# from wikibaseintegrator.models.claims import Claims


wbi_config['MEDIAWIKI_API_URL'] = 'https://lexbib.elex.is/w/api.php'
wbi_config['SPARQL_ENDPOINT_URL'] = 'https://lexbib.elex.is/query/sparql'
wbi_config['WIKIBASE_URL'] = 'https://lexbib.elex.is'

login_instance = wbi_login.Login(user=wb_bot_user, password=wb_bot_pwd)

wbi = WikibaseIntegrator(login=login_instance)

sparql_prefixes = """
PREFIX lwb: <https://lexbib.elex.is/entity/>
PREFIX ldp: <https://lexbib.elex.is/prop/direct/>
PREFIX lp: <https://lexbib.elex.is/prop/>
PREFIX lps: <https://lexbib.elex.is/prop/statement/>
PREFIX lpq: <https://lexbib.elex.is/prop/qualifier/>
PREFIX lpr: <https://lexbib.elex.is/prop/reference/>
PREFIX lno: <https://lexbib.elex.is/prop/novalue/>
"""

wd_user_agent = "http://lexbib.elex.is user DavidLbot david.lindemann@ehu.eus"

# functions for interaction with wbi
def packstatements(statements, wbitem=None, qualifiers=False, references=False):
	packed_statements = []
	for statement in statements:
		packed_statement = None
		# print(str(statement))
		if "qualifiers" in statement:
			packed_qualifiers = packstatements(statement['qualifiers'], qualifiers=True)
		else:
			packed_qualifiers = []
		if "references" in statement:
			packed_references = packstatements(statement['references'], references=True)
			# print('FOUND REF',statement['references'])
		else:
			packed_references = []
		snaktype = WikibaseSnakType.KNOWN_VALUE
		if 'value' in statement:
			if statement['value'] == False: # novalue statement
				statement['value'] == None
				snaktype = WikibaseSnakType.NO_VALUE

		actions = {
		'append': ActionIfExists.APPEND_OR_REPLACE,
		'replace': ActionIfExists.REPLACE_ALL,
		'force': ActionIfExists.FORCE_APPEND,
		'keep': ActionIfExists.KEEP
		}
		if 'action' in statement:
			action = actions[statement['action']]
		else:
			action = ActionIfExists.APPEND_OR_REPLACE
		if statement['type'].lower() == "string":
			packed_statement = String(value=statement['value'].strip(),prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
		elif statement['type'].lower() == "item" or statement['type'].lower() == "wikibaseitem":
			packed_statement = Item(value=statement['value'], prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
		elif statement['type'].lower() == "externalid":
			packed_statement = ExternalID(value=statement['value'],prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
		elif statement['type'].lower() == "time":
			if 'value' not in statement:
				statement['value'] = statement['time']
			packed_statement = Time(time=statement['value'], precision=statement['precision'], prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
			#print('Time statement: '+str(packed_statement))
		elif statement['type'].lower() == "monolingualtext":
			if 'value' not in statement:
				statement['value'] = statement['text']
			packed_statement = MonolingualText(text=statement['value'], language=statement['lang'], prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
		elif statement['type'].lower() == "url":
			packed_statement = URL(value=statement['value'], prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
		if not packed_statement:
			print('***ERROR: Unknown datatype in '+str(statement))
		# print(str(packed_statement))
		if qualifiers or references:
			packed_statements.append(packed_statement)
		else:
			packed_statement.mainsnak.snaktype = snaktype
			wbitem.claims.add([packed_statement], action_if_exists=action)
	if qualifiers or references:
		return packed_statements
	return wbitem

def itemwrite(itemdata, clear=False): # statements = {'append':[],'replace':[]}
	if itemdata['qid'] == False:
		lwbitem = wbi.item.new()
		print('Will write to new Q-item')
	elif itemdata['qid'].startswith('Q'):
		lwbitem = wbi.item.get(entity_id=itemdata['qid'])
		print('Will write to existing item '+itemdata['qid'])
	else:
		print('No Qid given.')
		return False
	if clear:
		lwbitem.claims = Claims()
	# 	r = lwbitem.write(is_bot=1, clear=clear)

	# labels
	if 'labels' in itemdata:
		langstrings = itemdata['labels']
		for langstring in langstrings:
			lang = langstring['lang']
			stringval = langstring['value']
			#print('Found wikidata label: ',lang,stringval)
			lwbitem.labels.set(lang,stringval)
	# altlabels
	if 'aliases' in itemdata:
		langstrings = itemdata['aliases']
		for langstring in langstrings:
			lang = langstring['lang']
			stringval = langstring['value']
			#print('Found wikidata altlabel: ',lang,stringval)
			lwbitem.aliases.set(lang,stringval)
	# descriptions
	if 'descriptions' in itemdata:
		langstrings = itemdata['descriptions']
		for langstring in langstrings:
			lang = langstring['lang']
			stringval = langstring['value']
			#print('Found wikidata description: ',lang,stringval)
			lwbitem.descriptions.set(lang,stringval)

	# statements
	for statement in itemdata['statements']:
		lwbitem = packstatements([statement], wbitem=lwbitem)

	d = False
	while d == False:
		try:
			print('Writing to LexBib Wikibase...')
			r = lwbitem.write(clear=clear)
			d = True
			print('Successfully written to item: '+lwbitem.id)
		except Exception:
			ex = traceback.format_exc()
			print(ex)
			if "wikibase-validator-label-with-description-conflict" in str(ex):
				print('\nFound an ambiguous item label: same description conflict.')
			presskey = input('Enter 0 for skipping and continue without writing statements, else retry writing.')
			if presskey == "0":
				d = True
				return False
			# 	lwbitem.descriptions.set(language="eu", value="Beste pertsona bat")


	return lwbitem.id

def importitem(importqid, process_claims=True, classqid=None):
	languages_to_consider = "eu es en de fr".split(" ")
	
	print('Will get ' + importqid + ' from wikidata...')
	
	apiurl = 'https://www.wikidata.org/w/api.php?action=wbgetentities&ids=' + importqid + '&format=json'
	# print(apiurl)
	wdjsonsource = requests.get(url=apiurl)
	if importqid in wdjsonsource.json()['entities']:
		importitemjson = wdjsonsource.json()['entities'][importqid]
	else:
		print('Error: Recieved no valid item JSON from Wikidata.')
		return False

	wbitemjson = {'labels': [], 'aliases': [], 'descriptions': [],
				  'statements': [{'prop_nr': 'P2', 'type': 'externalid', 'value': importqid}]}

	# ontology class
	if classqid:
		wbitemjson['statements'].append({'prop_nr': 'P5', 'type': 'Item', 'value': classqid})

	# process labels
	for lang in importitemjson['labels']:
		if lang in languages_to_consider:
			wbitemjson['labels'].append({'lang': lang, 'value': importitemjson['labels'][lang]['value']})
	# process aliases
	for lang in importitemjson['aliases']:
		if lang in languages_to_consider:
			for entry in importitemjson['aliases'][lang]:
				# print('Alias entry: '+str(entry))
				wbitemjson['aliases'].append({'lang': lang, 'value': entry['value']})
	# process descriptions
	for lang in importitemjson['descriptions']:
		if lang in languages_to_consider:
			if {'lang': lang, 'value': importitemjson['descriptions'][lang]['value']} not in wbitemjson['labels']:
				wbitemjson['descriptions'].append(
					{'lang': lang, 'value': importitemjson['descriptions'][lang]['value']})

	# process claims
	if process_claims:
		for claimprop in importitemjson['claims']:
			if claimprop in props_wd_wb:  # aligned prop
				wbprop = props_wd_wb[claimprop]
				for claim in importitemjson['claims'][claimprop]:
					claimval = claim['mainsnak']['datavalue']['value']
					claimtype = claim['mainsnak']['datavalue']['type']
					# if propwbdatatype[wbprop] == "WikibaseItem":
					# 	if claimval['id'] not in itemwd2wb:
					# 		print(
					# 			'Will create a new item for ' + claimprop + ' (' + wbprop + ') object property value: ' +
					# 			claimval['id'])
					# 		targetqid = importitem(claimval['id'], process_claims=False)
					# 	else:
					# 		targetqid = itemwd2wb[claimval['id']]
					# 		print('Will re-use existing item as property value: wd:' + claimval[
					# 			'id'] + ' > eusterm:' + targetqid)
					# 	statement = {'prop_nr': wbprop, 'type': 'Item', 'value': targetqid}
					# else:
					statement = {'prop_nr': wbprop, 'type': claimtype, 'value': claimval,'action': 'keep'}
					statement['references'] = [{'prop_nr': 'P2', 'type': 'externalid', 'value': importqid}]
				wbitemjson['statements'].append(statement)
	# process sitelinks
	if 'sitelinks' in importitemjson:
		for site in importitemjson['sitelinks']:
			if site.replace('wiki', '') in languages_to_consider:
				wpurl = "https://"+site.replace('wiki', '')+".wikipedia.org/wiki/"+importitemjson['sitelinks'][site]['title']
				print(wpurl)
				wbitemjson['statements'].append({'prop_nr':config.wd_sitelinks_prop,'type':'url','value':wpurl})

	wbitemjson['qid'] = False  # if False, then create new item
	result_qid = itemwrite(wbitemjson)
	print('Wikidata item import successful.')
	return result_qid


print('\nlwbi engine loaded.\n')
