import traceback, time, re, os
from pathlib import Path
from config_private import wb_bot_user
from config_private import wb_bot_pwd
from wikibaseintegrator import wbi_login, WikibaseIntegrator
# from wikibaseintegrator.datatypes.string import String
# from wikibaseintegrator.datatypes.externalid import ExternalID
# from wikibaseintegrator.datatypes.item import Item
# from wikibaseintegrator.datatypes.monolingualtext import MonolingualText
# from wikibaseintegrator.datatypes.time import Time
# from wikibaseintegrator.datatypes.globecoordinate import GlobeCoordinate
from wikibaseintegrator.datatypes.url import URL
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator import wbi_helpers
# from wikibaseintegrator.wbi_enums import ActionIfExists
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

def itemwrite(lwbitem, statements, clear=False): # statements = {'append':[],'replace':[]}
	if clear:
		lwbitem.claims = Claims()
	# 	r = lwbitem.write(is_bot=1, clear=clear)
	if len(statements['replace']) > 0:
		lwbitem.claims.add(statements['replace'])
	if len(statements['append']) > 0:
		lwbitem.claims.add(statements['append'], action_if_exists=ActionIfExists.APPEND)
	d = False
	while d == False:
		try:
			print('Writing to lwbi...')
			r = lwbitem.write(is_bot=1, clear=clear)
			d = True
		except Exception:
			ex = traceback.format_exc()
			print(ex)
			if "wikibase-validator-label-with-description-conflict" in str(ex):
				print('\nFound an ambiguous item label: same description conflict.')
			presskey = input('Enter 0 for skipping and continue without writing statements, else retry writing.')
			if presskey == "0":
				d = True
			# 	lwbitem.descriptions.set(language="eu", value="Beste pertsona bat")
		print('Successfully written to item: '+lwbitem.id)

	return lwbitem.id
