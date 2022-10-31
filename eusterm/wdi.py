# This imports WikibaseIntegrator and customizes it for Eusterm wikibase
# WBI version 0.12 is used, see https://github.com/LeMyst/WikibaseIntegrator

import traceback, time, re, os
from pathlib import Path
from config_private import wb_bot_user, wb_bot_pwd, wd_user, wd_pwd
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
from wikibaseintegrator.models.claims import Claims

# setup wbi for own wikibase
wbi_config['MEDIAWIKI_API_URL'] = 'https://www.wikidata.org/w/api.php'
wbi_config['SPARQL_ENDPOINT_URL'] = 'https://www.wikidata.org/sparql'
wbi_config['WIKIBASE_URL'] = 'https://www.wikidata.org'

login_instance = wbi_login.Login(user=wd_user, password=wd_pwd)
wdi = WikibaseIntegrator(login=login_instance)

sparql_prefixes = """
PREFIX clbwb: <https://www.wikidata.org/entity/>
PREFIX clbdp: <https://www.wikidata.org/prop/direct/>
PREFIX clbp: <https://www.wikidata.org/prop/>
PREFIX clbps: <https://www.wikidata.org/prop/statement/>
PREFIX clbpq: <https://www.wikidata.org/prop/qualifier/>
PREFIX clbpr: <https://www.wikidata.org/prop/reference/>
PREFIX clbno: <https://www.wikidata.org/prop/novalue/>
"""


wd_user_agent = "https://www.wikidata.org user DL2204bot david.lindemann@ehu.eus"



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
# 		'force': ActionIfExists.FORCE_APPEND
# 		}
# 		if 'action' in statement:
# 			action = actions[statement['action']]
# 		else:
# 			action = ActionIfExists.APPEND_OR_REPLACE
# 		if statement['type'].lower() == "string":
# 			packed_statement = String(value=statement['value'],prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
# 		elif statement['type'].lower() == "item":
# 			packed_statement = Item(value=statement['value'], prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
# 		elif statement['type'].lower() == "externalid":
# 			packed_statement = ExternalID(value=statement['value'],prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
# 		elif statement['type'].lower() == "time":
# 			packed_statement = Time(time=statement['value'], precision=statement['precision'], prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
# 			#print('Time statement: '+str(packed_statement))
# 		elif statement['type'].lower() == "monolingualtext":
# 			packed_statement = MonolingualText(text=statement['value'], language=statement['lang'], prop_nr=statement['prop_nr'],qualifiers=packed_qualifiers,references=packed_references)
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
# 		euswbitem = wbi.item.new()
# 		print('Will write to new Q-item')
# 	elif itemdata['qid'].startswith('Q'):
# 		euswbitem = wbi.item.get(entity_id=itemdata['qid'])
# 		print('Will write to existing item '+itemdata['qid'])
# 	else:
# 		print('No Qid given.')
# 		return False
# 	if clear:
# 		euswbitem.claims = Claims()
# 	# 	r = euswbitem.write(is_bot=1, clear=clear)
#
# 	# labels
# 	if 'labels' in itemdata:
# 		langstrings = itemdata['labels']
# 		for langstring in langstrings:
# 			lang = langstring['lang']
# 			stringval = langstring['value']
# 			#print('Found wikidata label: ',lang,stringval)
# 			euswbitem.labels.set(lang,stringval)
# 	# altlabels
# 	if 'altlabels' in itemdata:
# 		langstrings = itemdata['altlabels']
# 		for langstring in langstrings:
# 			lang = langstring['lang']
# 			stringval = langstring['value']
# 			#print('Found wikidata altlabel: ',lang,stringval)
# 			euswbitem.aliases.set(lang,stringval)
# 	# descriptions
# 	if 'descs' in itemdata:
# 		langstrings = itemdata['descs']
# 		for langstring in langstrings:
# 			lang = langstring['lang']
# 			stringval = langstring['value']
# 			#print('Found wikidata description: ',lang,stringval)
# 			euswbitem.descriptions.set(lang,stringval)
#
# 	# statements
# 	for statement in itemdata['statements']:
# 		euswbitem = packstatements([statement], wbitem=euswbitem)
#
# 	d = False
# 	while d == False:
# 		try:
# 			print('Writing to eusterm wikibase...')
# 			r = euswbitem.write(is_bot=1, clear=clear)
# 			d = True
# 			print('Successfully written to item: '+euswbitem.id)
# 		except Exception:
# 			ex = traceback.format_exc()
# 			print(ex)
# 			if "wikibase-validator-label-with-description-conflict" in str(ex):
# 				print('\nFound an ambiguous item label: same description conflict.')
# 			presskey = input('Enter 0 for skipping and continue without writing statements, else retry writing.')
# 			if presskey == "0":
# 				d = True
# 				return False
# 			# 	euswbitem.descriptions.set(language="eu", value="Beste pertsona bat")
#
#
# 	return euswbitem.id
#
print('\nwdi engine loaded.')
