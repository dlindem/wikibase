import traceback, time, re, os, requests
from wikibaseintegrator import wbi_login, WikibaseIntegrator
from wikibaseintegrator.datatypes.string import String
from wikibaseintegrator.datatypes.externalid import ExternalID
from wikibaseintegrator.datatypes.item import Item
from wikibaseintegrator.datatypes.monolingualtext import MonolingualText
from wikibaseintegrator.datatypes.time import Time
from wikibaseintegrator.datatypes.globecoordinate import GlobeCoordinate
from wikibaseintegrator.datatypes.url import URL
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator import wbi_helpers
from wikibaseintegrator.wbi_enums import ActionIfExists, WikibaseSnakType
from wikibaseintegrator.models.qualifiers import Qualifiers
from wikibaseintegrator.models import Sense
import config
import config_private

# from wikibaseintegrator.models.claims import Claims


wbi_config['MEDIAWIKI_API_URL'] = config.api_url
wbi_config['SPARQL_ENDPOINT_URL'] = config.sparql_endpoint
wbi_config['WIKIBASE_URL'] = config.wikibase_url

login_instance = wbi_login.Login(user=config_private.wb_bot_user, password=config_private.wb_bot_pwd)

wbi = WikibaseIntegrator(login=login_instance)

wd_user_agent = config.wikibase_url+", User "+config_private.wb_bot_user



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
			if statement['value'] == False: # unknown value statement
				statement['value'] == None
				snaktype = WikibaseSnakType.UNKNOWN_VALUE

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
		elif statement['type'].lower() == "sense":
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
		xwbitem = wbi.item.new()
		print('Will write to new Q-item', end="")
	elif itemdata['qid'].startswith('Q'):
		xwbitem = wbi.item.get(entity_id=itemdata['qid'])
		print('Will write to existing item '+itemdata['qid'], end="")
	elif itemdata['qid'].startswith('P'):
		xwbitem = wbi.property.get(entity_id=itemdata['qid'])
		print('Will write to existing property '+itemdata['qid'], end="")
	else:
		print('No Qid given.')
		return False
	if clear:
		xwbitem.claims = Claims()
	# 	r = xwbitem.write(is_bot=1, clear=clear)

	# labels
	if 'labels' in itemdata:
		langstrings = itemdata['labels']
		for langstring in langstrings:
			if 'lang' not in langstring and 'language' in langstring:
				langstring['lang'] = langstring['language']
			lang = langstring['lang']
			stringval = langstring['value']
			#print('Found wikidata label: ',lang,stringval)
			xwbitem.labels.set(lang,stringval)
	# altlabels
	if 'aliases' in itemdata:
		langstrings = itemdata['aliases']
		for langstring in langstrings:
			if 'lang' not in langstring and 'language' in langstring:
				langstring['lang'] = langstring['language']
			lang = langstring['lang']
			stringval = langstring['value']
			#print('Found wikidata altlabel: ',lang,stringval)
			xwbitem.aliases.set(lang,stringval, action_if_exists=ActionIfExists.REPLACE_ALL)
	# descriptions
	if 'descriptions' in itemdata:
		langstrings = itemdata['descriptions']
		for langstring in langstrings:
			if 'lang' not in langstring and 'language' in langstring:
				langstring['lang'] = langstring['language']
			lang = langstring['lang']
			stringval = langstring['value']
			#print('Found wikidata description: ',lang,stringval)
			xwbitem.descriptions.set(lang,stringval)

	# statements
	for statement in itemdata['statements']:
		xwbitem = packstatements([statement], wbitem=xwbitem)

	d = False
	while d == False:
		try:
			print(f"...now writing to {config.wikibase_name}...", end="")
			r = xwbitem.write(clear=clear)
			d = True
			print('successfully written to entity: '+xwbitem.id)
		except Exception:
			ex = traceback.format_exc()
			print(ex)
			if "wikibase-validator-label-with-description-conflict" in str(ex):
				print('\nFound an ambiguous item label: same description conflict.')
			presskey = input('Enter 0 for skipping and continue without writing statements, else retry writing.')
			if presskey == "0":
				d = True
				return False
			# 	xwbitem.descriptions.set(language="eu", value="Beste pertsona bat")
	return xwbitem.id

def basque_lexeme_write(itemdata, clear=False):
	if itemdata['lid']:
		lexeme = wbi.lexeme.get(entity_id=itemdata['lid'])
	else:
		lexeme = xwbi.wbi.lexeme.new(lexical_category='Q16', language='Q207')  # POS undef, Basque
	if 'lemma' in itemdata:
		lexeme.lemmas.set(language=itemdata['lemma']['lang'], value=itemdata['lemma']['lemma'])
	if 'statements' in itemdata:
		for statement in itemdata['statements']:
			lexeme = packstatements([statement], wbitem=lexeme)
	if 'senses' in itemdata:
		for sensedata in itemdata['senses']:
			sense = Sense()
			if 'statements' in sensedata:
				for statement in sensedata['statements']:
					sense = packstatements([statement], wbitem=sense)
			sense.glosses.set(language=sensedata['lang'], value=sensedata['definition'])
			lexeme.senses.add(sense)
	attempts = 0
	while attempts < 7:
		attempts += 1
		try:
			lexeme.write()
			print('successfully written to '+lexeme.id)
			time.sleep(0.2)
			return lexeme.id
		except Exception as ex:
			print(str(ex))
			print('Will try again in 3 sec...')
			time.sleep(3)
	print('\nExit after 7 failed writing attempts.')
	sys.exit()



def importitem(wdqid, wbqid=False, process_claims=True, classqid=None):
	languages_to_consider = "eu es en de fr".split(" ")
	
	print('Will get ' + wdqid + ' from wikidata...')
	
	apiurl = 'https://www.wikidata.org/w/api.php?action=wbgetentities&ids=' + wdqid + '&format=json'
	# print(apiurl)
	wdjsonsource = requests.get(url=apiurl)
	if wdqid in wdjsonsource.json()['entities']:
		importitemjson = wdjsonsource.json()['entities'][wdqid]
	else:
		print('Error: Recieved no valid item JSON from Wikidata.')
		return False

	wbitemjson = {'labels': [], 'aliases': [], 'descriptions': [],
				  'statements': [{'prop_nr': 'P2', 'type': 'externalid', 'value': wdqid}]}

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
					statement['references'] = [{'prop_nr': 'P2', 'type': 'externalid', 'value': wdqid}]
				wbitemjson['statements'].append(statement)
	# process sitelinks
	if 'sitelinks' in importitemjson:
		for site in importitemjson['sitelinks']:
			if site.replace('wiki', '') in languages_to_consider:
				wpurl = "https://"+site.replace('wiki', '')+".wikipedia.org/wiki/"+importitemjson['sitelinks'][site]['title']
				print(wpurl)
				wbitemjson['statements'].append({'prop_nr':config.wd_sitelinks_prop,'type':'url','value':wpurl})

	wbitemjson['qid'] = wbqid  # if False, then create new item. If wbqid given, prop-values are transferred to that item using action 'keep' [existing values]
	result_qid = itemwrite(wbitemjson)
	print('Wikidata item import successful.')
	return result_qid


print('\nxwbi engine loaded.\n')
