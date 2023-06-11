# This fixes "wd:Q397" value for dct:language written by mistake instead of "Q397" (see https://phabricator.wikimedia.org/T338255#8909023)

import wdwbi
import csv, time, json, sys

with open('logs/done_fixed_items.txt', 'r', encoding="utf-8") as logfile:
	done_items = logfile.read().split('\n')

with open('data/wd_lexemes_lila_id.csv', 'r', encoding="utf-8") as csvfile:
	data = csv.DictReader(csvfile)
	count = 0
	for item in data:
		count += 1
		# if count > 2:
		# 	print('\n2 items test run finished.')
		# 	break
		if item['lexeme'] in done_items:
			print('Done in previous run, skipped: '+item['lexeme'])
			continue
		lid = item['lexeme'].replace("http://www.wikidata.org/entity/", "")
		wdlexeme = wdwbi.wbi.lexeme.get(entity_id=lid)

		if wdlexeme.language != "wd:Q397":
			with open('logs/done_fixed_items.txt', 'a', encoding="utf-8") as logfile:
				logfile.write(item['lexeme'] + '\n')
				print('[' + str(count) + '] needs no fix: '+lid)
			continue
		print('[' + str(count) + '] Now processing ', lid)
		wdlexeme.language = "Q397"
		# print(wdlexeme.language)

		attempts = 0
		done = False
		while not done:
			attempts += 1
			# print('will try to write.')
			try:
				wdlexeme.write(is_bot=True, summary="Fix value for dct:language")
				with open('logs/done_fixed_items.txt', 'a', encoding="utf-8") as logfile:
					logfile.write(item['lexeme']+'\tfixed'+'\n')
				print('['+str(count)+'] Successfully processed',lid)
				done = True

			except Exception as ex:
				print('Failed to write lexeme with error message:\n'+str(ex))
				print('\nThis was attempt #'+str(attempts)+'\n')
				time.sleep(2)
			time.sleep(0.1)
			if not done:
				print('Will exit the script after five failed lexeme write attempts.')
				if attempts > 4:
					sys.exit()

print('\nFinished.')
