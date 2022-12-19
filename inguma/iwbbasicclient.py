import mwclient, re, json, time
from config_private import wb_bot_user, wb_bot_pwd

# Inguma wikibase auth for mwclient
site = mwclient.Site('wikibase.inguma.eus')
def get_token():
	global site
	global wb_bot_pwd
	global wb_bot_user
	# lwb login via mwclient
	while True:
		try:
			login = site.login(username=wb_bot_user, password=wb_bot_pwd)
			break
		except Exception as ex:
			print('lwb login via mwclient raised error: '+str(ex))
			time.sleep(60)
	# get token
	csrfquery = site.api('query', meta='tokens')
	token = csrfquery['query']['tokens']['csrftoken']
	print("Got fresh CSRF token for lexbib.elex.is.")
	return token
token = get_token()

# set a claim value
def setclaimvalue(guid, value, dtype):
	global token
	guidfix = re.compile(r'^(Q\d+)\-')
	guid = re.sub(guidfix, r'\1$', guid)
	print('Will now set value "'+value+'" to guid '+guid)
	if dtype == "item" or dtype =="wikibase-entityid":
		value = json.dumps({"entity-type":"item","numeric-id":int(value.replace("Q",""))})
	else:
		print('This item type is still not implemented in "lwb.setclaimvalue": '+dtype)
		sys.exit()
	results = None
	attempts = 0
	while attempts < 5:
		attempts += 1
		try:
			results = site.post('wbsetclaimvalue', token=token, claim=guid, snaktype="value", value=value)
			if results['success'] == 1:
				print('Claim update for '+value+' (dtype: '+dtype+'): success.')
				break
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print(str(ex))
				print('Claim update failed... Will try again. Result was: '+str(results))
				time.sleep(4)

print('IWB basic client (mwclient) loaded.')
