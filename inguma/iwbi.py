from config_private import wb_bot_user
from config_private import wb_bot_pwd
from wikibaseintegrator import wbi_login, WikibaseIntegrator
from wikibaseintegrator.datatypes.string import String
from wikibaseintegrator.datatypes.externalid import ExternalID
from wikibaseintegrator.datatypes.item import Item
from wikibaseintegrator.wbi_config import config as wbi_config

wbi_config['MEDIAWIKI_API_URL'] = 'https://wikibase.inguma.eus/w/api.php'
wbi_config['SPARQL_ENDPOINT_URL'] = 'https://wikibase.inguma.eus/query/sparql'
wbi_config['WIKIBASE_URL'] = 'https://wikibase.inguma.eus'

login_instance = wbi_login.Login(user=wb_bot_user, password=wb_bot_pwd)

wbi = WikibaseIntegrator(login=login_instance)
