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
			print('Writing to iwbi...')
			r = iwbitem.write(is_bot=1, clear=clear)
			d = True
		except Exception:
			ex = traceback.format_exc()
			print(ex)
			if "wikibase-validator-label-with-description-conflict" in str(ex):
				print('\nFound an ambiguous item label: same description conflict.')
			presskey = input('Enter 0 for skipping and continue without writing statements, else retry writing.')
			if presskey == "0":
				d = True
			# 	iwbitem.descriptions.set(language="eu", value="Beste pertsona bat")
		print('Successfully written to item: '+iwbitem.id)

	return iwbitem.id

def update_mapping(groupname):
	print('\nWill now update Inguma database ID to Inguma Wikiase Qid mapping for group: '+groupname)
	groupmappingfile = Path('D:/Inguma/content/'+groupname+'_qidmapping.csv')
	groupmappingoldfile = Path('D:/Inguma/content/'+groupname+'_qidmapping_old.csv')
	query = 'select ?id ?wikibase_item where {?wikibase_item idp:P49 ?id. filter regex (?id, "^'+groupname+':")}'
	bindings = wbi_helpers.execute_sparql_query(query=query, prefix=sparql_prefixes)['results']['bindings']
	if len(bindings) > 0:
		os.rename(groupmappingfile, groupmappingoldfile)
		with open(groupmappingfile, 'w', encoding="utf-8") as txtfile:
			for binding in bindings:
				txtfile.write(binding['id']['value'].replace(groupname+":","")+'\t'+binding['wikibase_item']['value'].replace("http://wikibase.inguma.eus/entity/","")+'\n')
	return "Mapping for "+groupname+" updated and saved to file."