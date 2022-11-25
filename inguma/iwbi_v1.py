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


wbi_config['MEDIAWIKI_API_URL'] = 'https://wikibase.inguma.eus/w/api.php'
wbi_config['SPARQL_ENDPOINT_URL'] = 'https://wikibase.inguma.eus/query/sparql'
wbi_config['WIKIBASE_URL'] = 'https://wikibase.inguma.eus'

login_instance = wbi_login.Login(user=wb_bot_user, password=wb_bot_pwd)

wbi = WikibaseIntegrator(login=login_instance)

sparql_prefixes = """
PREFIX iwb: <https://wikibase.inguma.eus/entity/>
PREFIX idp: <https://wikibase.inguma.eus/prop/direct/>
PREFIX ip: <https://wikibase.inguma.eus/prop/>
PREFIX ips: <https://wikibase.inguma.eus/prop/statement/>
PREFIX ipq: <https://wikibase.inguma.eus/prop/qualifier/>
PREFIX ipr: <https://wikibase.inguma.eus/prop/reference/>
PREFIX ino: <https://wikibase.inguma.eus/prop/novalue/>
"""

wd_user_agent = "https://wikibase.inguma.eus user DL2204bot david.lindemann@ehu.eus"

def itemwrite(iwbitem, statements, clear=False): # statements = {'append':[],'replace':[]}
	if clear:
		iwbitem.claims = Claims()
	# 	r = iwbitem.write(is_bot=1, clear=clear)
	if len(statements['replace']) > 0:
		iwbitem.claims.add(statements['replace'])
	if len(statements['append']) > 0:
		iwbitem.claims.add(statements['append'], action_if_exists=ActionIfExists.APPEND)
	d = False
	while d == False:
		try:
			print('Writing to inguma wikibase...')
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

print('\niwbi engine loaded.\n')
