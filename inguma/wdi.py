import mwclient, re, json, time
from config_private import wd_bot_user as wb_bot_user
from config_private import wd_bot_pwd as wb_bot_pwd

# Inguma wikibase auth for mwclient
site = mwclient.Site('www.wikidata.org')
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
	print("Got fresh CSRF token for Wikidata.")
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
	elif dtype == "url" or dtype == "externalid" or dtype == "string":
		value = '"' + value.replace('"', '\\"') + '"'
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

def setqualifier(qid, prop, claimid, qualiprop, qualio, dtype):
	global token
	guidfix = re.compile(r'^([QLP]\d+)\-')
	claimid = re.sub(guidfix, r'\1$', claimid)
	print(claimid)
	if dtype == "string" or dtype == "url" or dtype=="externalid":
		qualivalue = '"'+qualio.replace('"', '\\"')+'"'
	elif dtype == "item" or dtype =="wikibase-entityid":
		qualivalue = json.dumps({"entity-type":"item","numeric-id":int(qualio.replace("Q",""))})
	elif dtype == "time":
		qualivalue = json.dumps({
		"entity-type":"time",
		"time": qualio['time'],
		"timezone": 0,
		"before": 0,
		"after": 0,
		"precision": qualio['precision'],
		"calendarmodel": "http://www.wikidata.org/entity/Q1985727"})
	elif dtype == "monolingualtext":
		qualivalue = json.dumps(qualio)
	if qualiprop in ['P65']:
		print(f"{qualiprop} is a max1prop as qualifier.")
		existingclaims = getclaims(qid,prop)
		#print(str(existingclaims))
		qid = existingclaims[0]
		existingclaims = existingclaims[1]
		if prop in existingclaims:
			for claim in existingclaims[prop]:
				if claim['id'] != claimid:
					continue # skip other claims
				if "qualifiers" in claim:
					if qualiprop in claim['qualifiers']:
						existingqualihashes = {}
						for quali in claim['qualifiers'][qualiprop]:
							existingqualihash = quali['hash']
							existingqualivalue = quali['datavalue']['value']
							if isinstance(existingqualivalue, dict):
								if "time" in existingqualivalue:
									existingqualivalue = {"time":existingqualivalue['time'],"precision":existingqualivalue['precision']}
								if "text" in existingqualivalue and "language" in existingqualivalue:
									existingqualivalue = json.dumps(existingqualivalue)
							existingqualihashes[existingqualihash] = existingqualivalue
						#print('Found an existing '+qualiprop+' type card1 qualifier: '+str(list(existingqualihashes.values())[0]))
						allhashes = list(existingqualihashes.keys())
						done = False
						while (not done):
							if len(existingqualihashes) > 1:
								print('Found several qualis, but cardinality is 1; will delete all but the newest.')
								for delqualihash in allhashes:
									if delqualihash == allhashes[len(allhashes)-1]: # leave the last one intact
										print('Will leave intact this quali: '+existingqualihashes[delqualihash])
										existingqualihash = existingqualihashes[delqualihash]
									else:
										removequali(claimid,delqualihash)
										del existingqualihashes[delqualihash]
							elif len(existingqualihashes) == 1:
								done = True

						if str(list(existingqualihashes.values())[0]) in qualivalue:
							print('Found duplicate value for card1 quali. Skipped.')
							return True
						if dtype == "time":
							if list(existingqualihashes.values())[0]['time'] == qualio['time'] and list(existingqualihashes.values())[0]['precision'] == qualio['precision']:
								#print('Found duplicate value for '+qualiprop+' type time card1 quali. Skipped.')
								return True

						print('New value to be written to existing card1 quali.')
						try:
							while True:
								setqualifier = site.post('wbsetqualifier', token=token, claim=claimid, snakhash=existingqualihash, property=qualiprop, snaktype="value", value=qualivalue, bot=1)
								# always set!!
								if setqualifier['success'] == 1:
									print('Qualifier set ('+qualiprop+') '+qualivalue+': success.')
									return True
								print('Qualifier set failed, will try again...')
								logging.error('Qualifier set failed for '+prop+' ('+qualiprop+') '+qualivalue+': '+str(ex))
								time.sleep(3)

						except Exception as ex:
							if 'The statement has already a qualifier' in str(ex):
								print('The statement already has that object as ('+qualiprop+') qualifier: skipped writing duplicate qualifier')
								return False
	# not a max1quali >> write new quali in case value is different to existing value
	while True:
		try:
			setqualifier = site.post('wbsetqualifier', token=token, claim=claimid, property=qualiprop, snaktype="value", value=qualivalue, bot=1)
			# always set!!
			if setqualifier['success'] == 1:
				print('Qualifier set ('+qualiprop+') '+qualivalue+': success.')
				return True
		except Exception as ex:
			if 'The statement has already a qualifier' in str(ex):
				print('The statement already has a ('+qualiprop+') '+qualivalue+': skipped writing duplicate qualifier')
				return False
			else:
				print('Qualifier set failed, will try again...')
				#logging.error('Qualifier set failed for ' + prop + ' (' + qualiprop + ') ' + qualivalue + ': ' + str(ex))

				print('Error: '+str(ex))
				time.sleep(5)

def stringclaim(s, p, o):
	global token

	done = False
	value = '"'+o.replace('"', '\\"')+'"'
	while (not done):
		try:
			request = site.post('wbcreateclaim', token=token, entity=s, property=p, snaktype="value", value=value, bot=1)
			if request['success'] == 1:
				done = True
				claimId = request['claim']['id']
				print('Claim creation done: '+s+' ('+p+') '+o+'.')
				#time.sleep(1)
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			if 'Must be at least one character long' in str(ex):
				return False
			else:
				print('Claim creation failed, will try again...\n'+str(ex))
				time.sleep(4)
	return claimId

def removeref(guid=None, reference=None):
	global token
	guidfix = re.compile(r'^([QLP]\d+)\-')
	guid = re.sub(guidfix, r'\1$', guid)
	done = None
	while not done:
		try:
			results = site.post('wbremovereferences', statement=guid, references=[reference], token=token, bot=1, summary="Remove obsolete Reference.")
			if results['success'] == 1:
				print(f'Wb remove ref {reference} from claim {guid} success.')
				done = True
		except Exception as ex:
			print('Remove Reference operation failed, will try again...\n'+str(ex))
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			elif 'invalid-guid' in str(ex):
				print('The guid to remove was not found.')
				done = True
			elif 'no-such-reference' in str(ex):
				print("Reference not found.")
				done = True
			else:
				print(str(ex))
			time.sleep(1)

def removeclaim(guid):
	global token
	guidfix = re.compile(r'^(Q\d+)\-')
	guid = re.sub(guidfix, r'\1$', guid)
	done = False
	while (not done):
		try:
			results = site.post('wbremoveclaims', claim=guid, token=token)
			if results['success'] == 1:
				print('Wb remove claim for '+guid+': success.')
				done = True
		except Exception as ex:
			print('Removeclaim operation failed, will try again...\n'+str(ex))
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			if 'invalid-guid' in str(ex):
				print('The guid to remove was not found.')
				done = True
			time.sleep(4)

claimcache = {"item": None, "claims": None}
#get claims from qid
def getclaims(s, p):
	global claimcache
	# returns subject and response to wbgetclaim api query, example:
	# https://lexbib.elex.is/wiki/Special:ApiSandbox#action=wbgetclaims&format=json&entity=Q14680

	if claimcache['item'] != s: # if claims of that item have not just been retrieved before

		# get claims and put in claimcache
		done = False
		count = 0
		while count < 4 and done == False:
			count += 1
			print('Getting existing claims for '+s+'...')
			try:
				request = site.get('wbgetclaims', entity=s)

				if "claims" in request:
					done = True
					#print('Getclaims will return: '+s, request['claims'])
					claimcache['item'] = s
					claimcache['claims'] = request['claims']
			except Exception as ex:
				if 'unresolved-redirect' in str(ex):

					#get redirect target
					url = "https://lexbib.elex.is/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20%28strafter%28str%28%3Fredirect%29%2C%22http%3A%2F%2Flexbib.elex.is%2Fentity%2F%22%29%20as%20%3Frqid%29%20where%0A%7Blwb%3A"+s+"%20owl%3AsameAs%20%3Fredirect.%7D%0A%20%20%0A"
					subdone = False
					while (not subdone):
						try:
							r = requests.get(url)
							bindings = r.json()['results']['bindings']
						except Exception as ex:
							print('Error: SPARQL request for redirects failed: '+str(ex))
							time.sleep(2)
							continue
						subdone = True

					if 'rqid' in bindings[0]:
						print('Found redirect target '+bindings[0]['rqid']['value']+', will use that instead.')
						s = bindings[0]['rqid']['value']
						continue
				print('Getclaims operation for',s,p,' failed, will try again...\n'+str(ex))
				time.sleep(4)
		if not done:
			print('Getclaims operation failed. Item may not exist.')
			return False
	if p == True: # return all claims
		print('Will return all claims.')
		return (s, claimcache['claims'])
	if p in claimcache['claims']:
		return (s, {p: claimcache['claims'][p]})
	return (s, {})


print('Wikidata basic client (mwclient) loaded.')
