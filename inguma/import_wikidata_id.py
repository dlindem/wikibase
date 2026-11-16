import csv, iwbi, time



with open('data/inguma_ids_wikidatan.csv') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		wb_qid = row['wikibase_item'].replace("https://wikibase.inguma.eus/entity/", "")
		wd_qid = row['wd_item'].replace("http://www.wikidata.org/entity/","")
		references = iwbi.References()
		reference1 = iwbi.Reference()
		reference1.add(iwbi.ExternalID(prop_nr="P1", value=wd_qid))
		reference1.add(iwbi.Time(prop_nr="P94", time="now"))
		references.add(reference1)

		wb_item = iwbi.wbi.item.get(wb_qid)
		wb_item.claims.add(iwbi.ExternalID(prop_nr="P1", value=wd_qid, references=references), action_if_exists=iwbi.ActionIfExists.MERGE_REFS_OR_APPEND)
		wb_item.write()
		print(f"Success for https://wikibase.inguma.eus/entity/{wb_qid}")
		time.sleep(.34)

