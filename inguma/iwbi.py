import traceback, time, re
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


wbi_config['MEDIAWIKI_API_URL'] = 'https://wikibase.inguma.eus/w/api.php'
wbi_config['SPARQL_ENDPOINT_URL'] = 'https://wikibase.inguma.eus/query/sparql'
wbi_config['WIKIBASE_URL'] = 'https://wikibase.inguma.eus'

login_instance = wbi_login.Login(user=wb_bot_user, password=wb_bot_pwd)

wbi = WikibaseIntegrator(login=login_instance)

sparql_prefixes = """
PREFIX iwb: <http://wikibase.inguma.eus/entity/>
PREFIX idp: <http://wikibase.inguma.eus/prop/direct/>
PREFIX ip: <http://wikibase.inguma.eus/prop/>
PREFIX ips: <http://wikibase.inguma.eus/prop/statement/>
PREFIX ipq: <http://wikibase.inguma.eus/prop/qualifier/>
PREFIX ipr: <http://wikibase.inguma.eus/prop/reference/>
PREFIX ino: <http://wikibase.inguma.eus/prop/novalue/>
"""

wd_user_agent = "http://wikibase.inguma.eus user DL2204bot david.lindemann@ehu.eus"

def itemwrite(iwbitem, statements, clear=False): # statements = {'append':[],'replace':[]}
	if clear == True:
		r = iwbitem.write(is_bot=1, clear=clear)
	if len(statements['replace']) > 0:
		iwbitem.claims.add(statements['replace'])
	if len(statements['append']) > 0:
		iwbitem.claims.add(statements['append'], action_if_exists=ActionIfExists.APPEND)
	d = False
	while d == False:
		try:
			r = iwbitem.write(is_bot=1)
			d = True
		except Exception:
			ex = traceback.format_exc()
			print(ex)
			if "wikibase-validator-label-with-description-conflict" in str(ex):
				print('\nFound an ambiguous item label: same description conflict.')
			presskey = input('Press 1 for retry, 0 for skip and continue without writing statements.')
			if presskey == "0":
				d = True
			# 	iwbitem.descriptions.set(language="eu", value="Beste pertsona bat")
		try:
			print('Successfully written to item: '+iwbitem.id)
		except:
			pass
	return iwbitem.id
