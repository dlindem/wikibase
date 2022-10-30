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


wbi_config['MEDIAWIKI_API_URL'] = 'https://datuak.ahotsak.eus/w/api.php'
wbi_config['SPARQL_ENDPOINT_URL'] = 'https://datuak.ahotsak.eus/query/sparql'
wbi_config['WIKIBASE_URL'] = 'https://datuak.ahotsak.eus'

login_instance = wbi_login.Login(user=wb_bot_user, password=wb_bot_pwd)

wbi = WikibaseIntegrator(login=login_instance)

sparql_prefixes = """
PREFIX awb: <https://datuak.ahotsak.eus/entity/>
PREFIX adp: <https://datuak.ahotsak.eus/prop/direct/>
PREFIX ap: <https://datuak.ahotsak.eus/prop/>
PREFIX aps: <https://datuak.ahotsak.eus/prop/statement/>
PREFIX apq: <https://datuak.ahotsak.eus/prop/qualifier/>
PREFIX apr: <https://datuak.ahotsak.eus/prop/reference/>
PREFIX ano: <https://datuak.ahotsak.eus/prop/novalue/>
"""

wd_user_agent = "https://datuak.ahotsak.eus user DL2204bot david.lindemann@ehu.eus"

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
			print('Writing to ahtosak wikibase...')
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

print('\nawbi engine loaded.\n')
