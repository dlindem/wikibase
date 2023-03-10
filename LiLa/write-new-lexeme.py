# This creates new lexemes, and writes lemma, lexical category, language, and LiLa ID (P11033)

import wdwbi
import csv, time, json, sys

with open('logs/done_new_items.txt', 'r', encoding="utf-8") as logfile:
	done_items = logfile.read().split('\n')

with open('new_latin_lexemes.json', 'r', encoding="utf-8") as jsonfile:
	data = json.load(jsonfile)
	count = 0
	for item in data:
		count +=1
		# if count > 50:
		# 	print('\n50 items test run finished.')
		# 	break
		if item['P11033'] in done_items:
			print('Done in previous run, skipped: '+item['P11033'])
			continue
		wdlexeme = wdwbi.wbi.lexeme.new(language=item['dct:language'], lexical_category=item['wikibase:lexicalCategory'])
		wdlexeme.lemmas.set(language='la', value=item['wikibase:lemma'])
		newclaim = wdwbi.ExternalID(prop_nr='P11033', value=item['P11033'])
		wdlexeme.claims.add(newclaim)
		attempts = 0
		done = False
		while not done:
			attempts += 1
			try:
				wdlexeme.write(is_bot=True, summary="LiLa Lemma Bank mapping batch #2")
				with open('logs/done_new_items.txt', 'a', encoding="utf-8") as logfile:
					logfile.write(item['P11033']+'\n')
					print('['+str(count)+'] Successfully processed',item['P11033'])
					done = True
			except Exception as ex:
				print('Failed to write lexeme with error message:\n'+str(ex))
				print('\nThis was attempt #'+str(attempts)+'\n')
				time.sleep(2)
		time.sleep(0.1)
		if not done:
			print('Will exit the script after five failed lexeme write attempts.')
			sys.exit()

print('\nFinished.')
