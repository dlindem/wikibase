import kwbi, csv, json, sys
from data import langmapping

with open('data/lexeme-mapping.csv') as mappingcsv:
	mappingrows = mappingcsv.read().split('\n')
	lexeme_map = {}
	for row in mappingrows:
		mapping = row.split('\t')
		if len(mapping) == 2:
			lexeme_map[mapping[0]] = mapping[1]

with open('data/lexical-entry.csv') as incsv:
	entries = csv.DictReader(incsv)
	with open('data/lexeme-mapping.csv', 'a') as mappingcsv:
		count = 0

		for entry in entries:
			count += 1
			sinaid = entry['entry'].replace('https://github.com/sinaahmadi/', '')
			if sinaid in lexeme_map:
				continue # has been processed in previous run
			print('\nWill process entry file line '+str(count)+': '+sinaid)

			lemmas = {}
			for label in json.loads(entry['labels']):
				languages = []
				labellang = label['lang'].lower()
				if labellang == "sdh-arab":
					continue # sdh-arab is skipped (for the moment)
				if labellang == "sdh-latn":
					labellang = "sdh" # sdh-latn is represented as sdh
				languages.append(labellang.replace('-arab','').replace('-latn',''))
				lemmas[labellang] = label['label']
				if len(list(set(languages))) > 1:
					print('Error: more than one lemma language')
					sys.exit()

			lexeme = kwbi.wbi.lexeme.new(lexical_category="Q3", language=langmapping.wikilang_to_qid[languages[0]])
			for labellang in lemmas:
				lexeme.lemmas.set(language=labellang, value=lemmas[labellang])
			
			claim = kwbi.String(prop_nr='P6', value=sinaid)
			lexeme.claims.add(claim)

			lexeme.write()
			mappingcsv.write(sinaid+'\t'+lexeme.id+'\n')
			print('Finished processing '+lexeme.id)
