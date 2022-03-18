from config_private import wb_bot_user as wb_bot_user
from config_private import wb_bot_pwd as wb_bot_pwd
from wikibaseintegrator import wbi_login as wbi_login
from wikibaseintegrator import wbi_core as wbi_core
from wikibaseintegrator import wbi_datatype as wbi_datatype
from wikibaseintegrator.wbi_config import config as wbi_config

wbi_config['MEDIAWIKI_API_URL'] = 'https://wikibase.inguma.eus/w/api.php'
wbi_config['SPARQL_ENDPOINT_URL'] = 'https://wikibase.inguma.eus/query/sparql'
wbi_config['WIKIBASE_URL'] = 'https://wikibase.inguma.eus'

login_instance = wbi_login.Login(user=wb_bot_user, pwd=wb_bot_pwd)
