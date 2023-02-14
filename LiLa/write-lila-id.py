# This writes LiLa ID to lexemes (P11033)

import wdwbi
import csv, time

with open('logs/done_items.txt', 'r', encoding="utf-8") as logfile:
	done_items = logfile.read().split('\n')

with open('wikidata_lila_alignment_1st_batch.csv', 'r', encoding="utf-8") as csvfile:
	mappings = csv.DictReader(csvfile, delimiter=",")
	count = 0
	for mapping in mappings:
		count +=1
		if count > 55:
			print('\n50 items test run finished.')
			break
		if mapping['wiki_id'] in done_items:
			print('Done in previous run, skipped: '+mapping['wiki_id'])
			continue
		wdlexeme = wdwbi.wbi.lexeme.get(entity_id=mapping['wiki_id'])
		newclaim = wdwbi.ExternalID(prop_nr='P11033', value=mapping['lila_id'])
		wdlexeme.claims.add(newclaim)
		wdlexeme.write(summary="LiLa Lemma Bank mapping batch #1")
		# when getting bot flag, write as bot user and write with bot flag:
		# wdlexeme.write(is_bot=True, maxlag=5, summary="LiLa Lemma Bank mapping batch #1")
		with open('logs/done_items.txt', 'a', encoding="utf-8") as logfile:
			logfile.write(mapping['wiki_id']+'\n')
		print('['+str(count)+'] Successfully processed',str(mapping))
		time.sleep(0.1)

print('\nFinished.')
