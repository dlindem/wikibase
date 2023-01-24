# This imports WikibaseIntegrator and customizes it for Wikidata
# WBI version 0.12 is used, see https://github.com/LeMyst/WikibaseIntegrator

#import traceback, time, re, os
from config_private import wb_bot_user, wb_bot_pwd
from wikibaseintegrator import wbi_login, WikibaseIntegrator
# from wikibaseintegrator.datatypes.string import String
from wikibaseintegrator.datatypes.externalid import ExternalID
# from wikibaseintegrator.datatypes.item import Item
# from wikibaseintegrator.datatypes.monolingualtext import MonolingualText
# from wikibaseintegrator.datatypes.time import Time
# from wikibaseintegrator.datatypes.globecoordinate import GlobeCoordinate
# from wikibaseintegrator.datatypes.url import URL
from wikibaseintegrator.wbi_config import config as wbi_config
# from wikibaseintegrator import wbi_helpers
# from wikibaseintegrator.wbi_enums import ActionIfExists, WikibaseSnakType
from wikibaseintegrator.models.claims import Claims


# setup wbi for wikidata as wdi
wbi_config['MEDIAWIKI_API_URL'] = 'https://www.wikidata.org/w/api.php'
wbi_config['SPARQL_ENDPOINT_URL'] = 'https://www.wikidata.org/sparql'
wbi_config['WIKIBASE_URL'] = 'https://www.wikidata.org'
wbi_config['USER_AGENT']= "User DL2204 david.lindemann@ehu.eus"


login_instance = wbi_login.Login(user=wb_bot_user, password=wb_bot_pwd)
wbi = WikibaseIntegrator(login=login_instance)

# sparql_prefixes = """
# PREFIX wb: <http://www.wikidata.org/entity/>
# PREFIX wdt: <http://www.wikidata.org/prop/direct/>
# PREFIX wp: <http://www.wikidata.org/prop/>
# PREFIX wps: <http://www.wikidata.org/prop/statement/>
# PREFIX wpq: <http://www.wikidata.org/prop/qualifier/>
# PREFIX wpr: <http://www.wikidata.org/prop/reference/>
# PREFIX wno: <http://www.wikidata.org/prop/novalue/>
# """
#
# entity_prefix = 'https://www.wikidata.org/entity/'

# # functions for interaction with wbi
# def packstatements(statements, wbitem=None, qualifiers=False, references=False):
# 	packed_statements = []
# 	for statement in statements:
# 		packed_statement = None
# 		# print(str(statement))
# 		if "qualifiers" in statement:
# 			packed_qualifiers = packstatements(statement['qualifiers'], qualifiers=True)
# 		else:
# 			packed_qualifiers = []
# 		if "references" in statement:
# 			packed_references = packstatements(statement['references'], references=True)
# 			# print('FOUND REF',statement['references'])
# 		else:
# 			packed_references = []
# 		if statement['value'] == False: # novalue statement
# 			statement['value'] == None
# 			snaktype = WikibaseSnakType.NO_VALUE
# 		else:
# 			snaktype = WikibaseSnakType.KNOWN_VALUE
# 		actions = {
# 		'append': ActionIfExists.APPEND_OR_REPLACE,
# 		'replace': ActionIfExists.REPLACE_ALL,
# 		'force': ActionIfExists.FORCE_APPEND,
# 		'keep': ActionIfExists.KEEP
# 		}
# 		if 'action' in statement:
# 			action = actions[statement['action']]
# 		else:
# 			action = ActionIfExists.APPEND_OR_REPLACE
# 		if statement['type'].lower() == "string":
# 			packed_statement = String(value=statement['value'],prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
# 		elif statement['type'].lower() == "item" or statement['type'].lower() == "wikibaseitem":
# 			packed_statement = Item(value=statement['value'], prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
# 		elif statement['type'].lower() == "externalid":
# 			packed_statement = ExternalID(value=statement['value'],prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
# 		elif statement['type'].lower() == "time":
# 			packed_statement = Time(time=statement['value'], precision=int(statement['precision']), prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
# 			#print('Time statement: '+str(packed_statement))
# 		elif statement['type'].lower() == "monolingualtext":
# 			packed_statement = MonolingualText(text=statement['value'], language=statement['lang'], prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
# 		elif statement['type'].lower() == "url":
# 			packed_statement = URL(value=statement['value'], prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
# 		if not packed_statement:
# 			print('***ERROR: Unknown datatype in '+str(statement))
# 		# print(str(packed_statement))
# 		if qualifiers or references:
# 			packed_statements.append(packed_statement)
# 		else:
# 			packed_statement.mainsnak.snaktype = snaktype
# 			wbitem.claims.add([packed_statement], action_if_exists=action)
# 	if qualifiers or references:
# 		return packed_statements
# 	return wbitem
#
# def itemwrite(itemdata, clear=False): # statements = {'append':[],'replace':[]}
# 	if itemdata['qid'] == False:
# 		iwbitem = wbi.item.new()
# 		print('Will write to new Q-item')
# 	elif itemdata['qid'].startswith('Q'):
# 		iwbitem = wbi.item.get(entity_id=itemdata['qid'])
# 		print('Will write to existing item '+itemdata['qid'])
# 	else:
# 		print('No Qid given.')
# 		return False
# 	if clear:
# 		iwbitem.claims = Claims()
# 	# 	r = iwbitem.write(is_bot=1, clear=clear)
#
# 	# labels
# 	if 'labels' in itemdata:
# 		langstrings = itemdata['labels']
# 		for langstring in langstrings:
# 			lang = langstring['lang']
# 			stringval = langstring['value']
# 			#print('Found wikidata label: ',lang,stringval)
# 			iwbitem.labels.set(lang,stringval)
# 	# altlabels
# 	if 'aliases' in itemdata:
# 		langstrings = itemdata['aliases']
# 		for langstring in langstrings:
# 			lang = langstring['lang']
# 			stringval = langstring['value']
# 			#print('Found wikidata altlabel: ',lang,stringval)
# 			iwbitem.aliases.set(lang,stringval)
# 	# descriptions
# 	if 'descriptions' in itemdata:
# 		langstrings = itemdata['descriptions']
# 		for langstring in langstrings:
# 			lang = langstring['lang']
# 			stringval = langstring['value']
# 			#print('Found wikidata description: ',lang,stringval)
# 			iwbitem.descriptions.set(lang,stringval)
#
# 	# statements
# 	for statement in itemdata['statements']:
# 		iwbitem = packstatements([statement], wbitem=iwbitem)
#
# 	d = False
# 	while d == False:
# 		try:
# 			print('Writing to inguma wikibase...')
# 			r = iwbitem.write(clear=clear)
# 			d = True
# 			print('Successfully written to item: '+iwbitem.id)
# 		except Exception:
# 			ex = traceback.format_exc()
# 			print(ex)
# 			if "wikibase-validator-label-with-description-conflict" in str(ex):
# 				print('\nFound an ambiguous item label: same description conflict.')
# 			presskey = input('Enter 0 for skipping and continue without writing statements, else retry writing.')
# 			if presskey == "0":
# 				d = True
# 				return False
# 			# 	iwbitem.descriptions.set(language="eu", value="Beste pertsona bat")
#
#
# 	return iwbitem.id
#
print('\niwbi engine loaded.\n')
