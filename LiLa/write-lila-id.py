import wdwbi
import csv, time

with open('wikidata_lila_alignment_1st_batch.csv', 'r', encoding="utf-8") as csvfile:
	mappings = csv.DictReader(csvfile, delimiter=",")
	count = 0
	for mapping in mappings:
		count +=1
		wdlexeme = wdwbi.wbi.lexeme.get(entity_id=mapping['wiki_id'])
		newclaim = wdwbi.ExternalID(prop_nr='P11033', value=mapping['lila_id'])
		wdlexeme.claims.add(newclaim)
		wdlexeme.write(is_bot=True, summary="LiLa Lemma Bank mapping batch #1")
		print('['+str(count)+'] Successfully processed',str(mapping))
		time.sleep(0.1)
