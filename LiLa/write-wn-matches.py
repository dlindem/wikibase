import csv, json, mwclient, time, config_private, requests, wdwbi

# load donelog
with open('logs/done_wd_mappings.txt') as logfile:
	done_items = logfile.read().split('\n')

# load wd English labels of wordnet-aligned items
with open('data/wikidata_wordnet.csv') as csvfile:
	csvdict = csv.DictReader(csvfile)
	wd_labels = {}
	for row in csvdict:
		wd_labels[row['wd_item']] = row['wd_itemLabel']

# load mappings (produced by map-lila-wn.py)
with open('data/lilasense_wd_mappings_lexeme.json') as jsonfile:
	lexemes = json.load(jsonfile)

# # set up mwclient
# wikidata = mwclient.Site('www.wikidata.org')
# def get_token():
# 	global wikidata
#
# 	while True:
# 		try:
# 			login = wikidata.login(username=config_private.wb_bot_user, password=config_private.wb_bot_pwd)
# 			break
# 		except Exception as ex:
# 			print('qwb login via mwclient raised error: '+str(ex))
# 			time.sleep(60)
# 	# get token
# 	csrfquery = wikidata.api('query', meta='tokens')
# 	token = csrfquery['query']['tokens']['csrftoken']
# 	print("\nGot fresh CSRF token for Wikidata.\n")
# 	return token
# token = get_token()

count = 0    
for lexeme in lexemes:
	count += 1
	if lexeme in done_items:
		print(f'Lexeme {lexeme} has been done in a previous run.')
		continue
	wd_item_to_link = lexemes[lexeme]['wd_item']
	if not wd_item_to_link.startswith('Q'):
		with open('logs/wnlink_on_lexemes.csv', 'a') as strangelogfile:
			strangelogfile.write(lexeme + '\t' +wd_item_to_link)
		continue
	print(f'\n[{str(count)}] Now processing {lexeme}...')
	r = requests.get('https://www.wikidata.org/w/api.php?action=wbgetentities&ids='+lexeme+'&format=json')
	lexemedata = r.json()['entities'][lexeme]
	if len(lexemedata['senses']) == 0:
		print(f'Lexeme has no senses. Will create one and write lilasense WN mapping.')
		wdlexeme = wdwbi.wbi.lexeme.get(entity_id=lexeme)
		newsense = wdwbi.Sense()
		newsense.glosses.set(language='en', value=wd_labels[wd_item_to_link])
		sense_references = wdwbi.References()
		sense_reference1 = wdwbi.Reference()
		sense_reference1.add(wdwbi.URL(prop_nr='P854', value=lexemes[lexeme]['lilasense']))
		sense_references.add(sense_reference1)
		claim = wdwbi.Item(prop_nr='P5137', value=wd_item_to_link, references=sense_references)
		newsense.claims.add(claim)
		wdlexeme.senses.add(newsense)
		wdlexeme.write(is_bot=True, summary="Create sense, add item-for-this-sense (from LatinWordNet-PrincetonWordNet mapping)")

	else:
		print('Lexeme has senses. Will skip.')
		with open('data/wd_lexemes_with_old_senses.txt', 'a') as skiplog:
			skiplog.write(lexeme+'\n')

	with open('logs/done_wd_mappings.txt', 'a') as logfile:
		logfile.write(lexeme+'\n')

	time.sleep(0.2)




