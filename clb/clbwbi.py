# This imports WikibaseIntegrator and customizes it for Inguma wikibase
# WBI version 0.12 is used, see https://github.com/LeMyst/WikibaseIntegrator/tree/rewrite-wbi

import traceback, time, re, os
from pathlib import Path
from config_private import wb_bot_user
from config_private import wb_bot_pwd
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
from wikibaseintegrator.wbi_enums import ActionIfExists
from wikibaseintegrator.models.claims import Claims


wbi_config['MEDIAWIKI_API_URL'] = 'https://czechlitbib.wikibase.cloud/w/api.php'
wbi_config['SPARQL_ENDPOINT_URL'] = 'https://czechlitbib.wikibase.cloud/query/sparql'
wbi_config['WIKIBASE_URL'] = 'https://czechlitbib.wikibase.cloud'

login_instance = wbi_login.Login(user=wb_bot_user, password=wb_bot_pwd)

wbi = WikibaseIntegrator(login=login_instance)

sparql_prefixes = """
PREFIX clbwb: <https://czechlitbib.wikibase.cloud/entity/>
PREFIX clbdp: <https://czechlitbib.wikibase.cloud/prop/direct/>
PREFIX clbp: <https://czechlitbib.wikibase.cloud/prop/>
PREFIX clbps: <https://czechlitbib.wikibase.cloud/prop/statement/>
PREFIX clbpq: <https://czechlitbib.wikibase.cloud/prop/qualifier/>
PREFIX clbpr: <https://czechlitbib.wikibase.cloud/prop/reference/>
PREFIX clbno: <https://czechlitbib.wikibase.cloud/prop/novalue/>
"""

wd_user_agent = "https://czechlitbib.wikibase.cloud user DL2204bot david.lindemann@ehu.eus"

def packstatements(claims):
	statements = []
	for claim in claims:
		if statement['type'] == "String":
			statements.append(String(value=claim['value'],prop_nr=claim['prop_nr']))
		elif statement['type'] == "Item":
			statements.append(Item(value=claim['value'], prop_nr=claim['prop_nr']))
		elif statement['type'] == "ExternalID":
			statements.append(ExternalID(value=claim['value'],prop_nr=claim['prop_nr']))
		elif statement['type'] == "Time":
			statements.append(Time(time=claim['time'], precision=claim['precision'], prop_nr=claim['prop_nr']))


def itemwrite(itemdata, clear=False): # statements = {'append':[],'replace':[]}
	if itemdata['qid'] = False:
		iwbitem = wbi.item.new()
		print('Will write to new Q-item')
	elif itemdata['qid'].startswith('Q'):
		iwbitem = clbwbi.wbi.item.get(entity_id=itemdata['qid'])
		print('Will write to existing item '+itemdata['qid'])
	if clear:
		iwbitem.claims = Claims()
	# 	r = iwbitem.write(is_bot=1, clear=clear)
	statements['replace'] = packstatements(itemdata['statements']['replace'])
	statements['append'] = packstatements(itemdata['statements']['append'])

	if statements['replace']:
		iwbitem.claims.add(statements['replace'])
	if statements['append']:
		iwbitem.claims.add(statements['append'], action_if_exists=ActionIfExists.APPEND)
	d = False
	while d == False:
		try:
			print('Writing to clb wikibase...')
			r = iwbitem.write(is_bot=1, clear=clear)
			d = True
			print('Successfully written to item: '+iwbitem.id)
		except Exception:
			ex = traceback.format_exc()
			print(ex)
			if "wikibase-validator-label-with-description-conflict" in str(ex):
				print('\nFound an ambiguous item label: same description conflict.')
			presskey = input('Enter 0 for skipping and continue without writing statements, else retry writing.')
			if presskey == "0":
				d = True
				return False
			# 	iwbitem.descriptions.set(language="eu", value="Beste pertsona bat")


	return iwbitem.id

print('\nclbwbi engine loaded.\n')
