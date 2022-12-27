import kwb
# import kwbi
import csv, json, sys, time
# from data import langmapping

def get_lemmas(lemmas_from_csv):
	lemmas = {}
	for label in json.loads(lemmas_from_csv):
		languages = []
		labellang = label['lang'].lower()
		if labellang == "sdh-arab":
			continue # sdh-arab is skipped (for the moment)
		if labellang == "sdh-latn":
			labellang = "sdh" # sdh-latn is represented as sdh
		wikilangtowrite = labellang.replace('-arab','').replace('-latn','')
		print('Will write lemma '+label['label']+', variant '+labellang+' (for wikilanguage '+wikilangtowrite+') as gloss')
		lemmas[labellang]= {'language': labellang, 'value': label['label']}
		# lemmas.append({labellang:{'language': labellang, 'value': label['label']}})
	return {'lemmas':lemmas, 'wikilangtowrite':wikilangtowrite}



with open('data/lexeme-mapping.csv') as mappingcsv:
	mappingrows = mappingcsv.read().split('\n')
	lexeme_map = {}
	for row in mappingrows:
		mapping = row.split('\t')
		if len(mapping) == 2:
			lexeme_map[mapping[0]] = mapping[1]

with open('data/sense-mapping.csv') as mappingcsv:
	mappingrows = mappingcsv.read().split('\n')
	sense_map = {}
	for row in mappingrows:
		mapping = row.split('\t')
		if len(mapping) == 2:
			sense_map[mapping[0]] = mapping[1]

with open('data/sense-translations.csv') as incsv:
	entries = csv.DictReader(incsv)

	start = int(input('Enter the csv line number you want to start from:\n'))
	count = 1
	for entry in entries:
		count += 1
		if count < start:
			continue

		print('\nWill process now entry csv line ['+str(count)+']\n')

		sourcelexeme = entry['sourcelexeme'].replace('https://github.com/sinaahmadi/', '')
		sourcesense = entry['sourcesense'].replace('https://github.com/sinaahmadi/', '')
		targetlexeme = entry['targetlexeme'].replace('https://github.com/sinaahmadi/', '')
		targetsense = entry['targetsense'].replace('https://github.com/sinaahmadi/', '')

		if sourcelexeme not in lexeme_map:
			print('Error: Source lexeme not found in Wikibase: '+sourcelexeme)
			sys.exit()
		if targetlexeme not in lexeme_map:
			print('Error: Target lexeme not found in Wikibase: '+targetlexeme)
			sys.exit()

		if targetsense in sense_map:
			targetsense_entity_id = sense_map[targetsense]
			print('This sense exists already: '+targetsense)

		else: # create new sense and save its ID mapping
			print('This sense must be created: '+targetsense)
			lemmas = get_lemmas(entry['sourcelemmas'])
			targetsense_entity_id = kwb.newsense(lexeme_map[targetlexeme], lemmas['lemmas'])
			sinastatement = kwb.stringclaim(targetsense_entity_id, "P6", targetlexeme)
			with open('data/sense-mapping.csv', 'a') as mappingcsv:
				mappingcsv.write(targetsense+'\t'+targetsense_entity_id+'\n')

		if sourcesense in sense_map:
			sourcesense_entity_id = sense_map[sourcesense]
			print('This sense exists already: '+sourcesense+'\n')

		else: # create new sense and save its ID mapping
			print('This sense must be created: '+sourcesense)
			lemmas = get_lemmas(entry['targetlemmas'])
			sourcesense_entity_id = kwb.newsense(lexeme_map[sourcelexeme], lemmas['lemmas'])
			sinastatement = kwb.stringclaim(sourcesense_entity_id, "P6", sourcelexeme)
			with open('data/sense-mapping.csv', 'a') as mappingcsv:
				mappingcsv.write(sourcesense+'\t'+sourcesense_entity_id+'\n')

		# write translation links between senses
		statement1 = kwb.updateclaim(targetsense_entity_id, "P9", sourcesense_entity_id, "sense")
		statement2 = kwb.updateclaim(sourcesense_entity_id, "P9", targetsense_entity_id, "sense")

		print('Finished processing line ['+str(count)+'].')
