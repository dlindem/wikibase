import csv, time, xwbi, traceback

with open('tbx_mappings/tbx_propvalues_lider.csv', 'r', encoding="utf-8") as file:
	valsdict = csv.DictReader(file, delimiter=",")

	for row in valsdict:
		print(f'\nWill process {row}...')
		enlabel = row['label'].strip()
		liderUri = row['liderURI'].strip().replace("<","").replace(">","")
		newitem = xwbi.wbi.item.new()
		newitem.labels.set('en',enlabel)
		print('enlabel set: '+enlabel)
		newitem.claims.add(xwbi.Item(value="Q3", prop_nr='P5'))
		print("P5 Q3 set.")
		if liderUri.startswith("http"):
			newitem.claims.add(xwbi.URL(value=liderUri,prop_nr='P6'))
			print('P6 set: '+liderUri)
		d = False
		while d == False:
			try:
				print('Writing to wikibase...')
				r = newitem.write(is_bot=1, clear=False)
				d = True
				print('Successfully written data to item: '+newitem.id)
				with open('tbx_mappings/tbx_propvalues_wikibase.csv', 'a') as file:
					file.write(f"{newitem.id}\t{enlabel}\t{liderUri}\n")
					time.sleep(1)
			except Exception:
				ex = traceback.format_exc()
				print(ex)
				presskey = input('Press key for retry.')