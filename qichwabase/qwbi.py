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
from wikibaseintegrator.models import Sense


wbi_config['MEDIAWIKI_API_URL'] = 'https://qichwa.wikibase.cloud/w/api.php'
wbi_config['SPARQL_ENDPOINT_URL'] = 'https://qichwa.wikibase.cloud/query/sparql'
wbi_config['WIKIBASE_URL'] = 'https://qichwa.wikibase.cloud'
wbi_config['DEFAULT_LEXEME_LANGUAGE'] = "Q1"

login_instance = wbi_login.Login(user=wb_bot_user, password=wb_bot_pwd)

wbi = WikibaseIntegrator(login=login_instance)

sparql_prefixes = """
PREFIX qwb: <https://qichwa.wikibase.cloud/entity/>
PREFIX qdp: <https://qichwa.wikibase.cloud/prop/direct/>
PREFIX qp: <https://qichwa.wikibase.cloud/prop/>
PREFIX qps: <https://qichwa.wikibase.cloud/prop/statement/>
PREFIX qpq: <https://qichwa.wikibase.cloud/prop/qualifier/>
PREFIX qpr: <https://qichwa.wikibase.cloud/prop/reference/>
PREFIX qno: <https://qichwa.wikibase.cloud/prop/novalue/>
"""

wd_user_agent = "https://qichwa.wikibase.cloud user DL2204bot david.lindemann@ehu.eus"

def itemwrite(qwbitem, statements, clear=False, retry_after=10): # statements = {'append':[],'replace':[]}
	if clear:
		qwbitem.claims = Claims()
	# 	r = qwbitem.write(is_bot=1, clear=clear)
	if len(statements['replace']) > 0:
		qwbitem.claims.add(statements['replace'])
	if len(statements['append']) > 0:
		qwbitem.claims.add(statements['append'], action_if_exists=ActionIfExists.APPEND)
	d = False
	while d == False:
		try:
			print('Writing to qichwabase...')
			r = qwbitem.write(is_bot=1, clear=clear)
			d = True
		except Exception:
			ex = traceback.format_exc()
			print(ex)
			if "wikibase-validator-label-with-description-conflict" in str(ex):
				print('\nFound an ambiguous item label: same description conflict.')
			presskey = input('Enter 0 for skipping and continue without writing statements, else retry writing.')
			if presskey == "0":
				d = True
			# 	qwbitem.descriptions.set(language="eu", value="Beste pertsona bat")
		print('Successfully written to item: '+qwbitem.id)

	return qwbitem.id

print('\nqwbi engine loaded.\n')
