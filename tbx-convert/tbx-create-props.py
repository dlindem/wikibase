import csv, time, xwbi, traceback

with open('tbx_mappings/tbx_propvalues_wikibase.csv') as file:
	csvrows = csv.DictReader(file, delimiter="\t")
	propvals = {}
	for row in csvrows:
		print(row)
		propvals[row['label']] = row['qid']

with open('tbx_mappings/tbx_properties_lider.csv', 'r', encoding="utf-8") as file:
	propsdict = csv.DictReader(file, delimiter="\t")
	newprops = {}
	for row in propsdict:
		print(f'\nWill process {row}...')
		enlabel = row['attributeValue'].strip()
		dtype = row['dtype']
		liderUri = row['liderURI'].strip().replace("<","").replace(">","")
		values = row['values'].strip().split(",")
		newprop = xwbi.wbi.property.new(datatype=dtype)
		newprop.labels.set('en',enlabel)
		print('enlabel set: '+enlabel)
		newprop.claims.add(xwbi.Item(value="Q106", prop_nr='P5'))
		print("P5 Q106 set.")
		if liderUri.startswith("http"):
			newprop.claims.add(xwbi.URL(value=liderUri,prop_nr='P6'))
			print('P6 set: '+liderUri)
		newprop.claims.add(xwbi.String(value=row['element'], prop_nr='P7', qualifiers=[xwbi.String(value=row['attribute'], prop_nr='P8')]))
		if len(values) > 0 and values[0] != '':
			for value in values:
				valqid = propvals[value]
				newprop.claims.add(xwbi.Item(value=valqid, prop_nr='P9'))
				print(f"Set range value {value} ({valqid}).")
		else:
			print("No range value to set.")
		d = False
		while d == False:
			try:
				print('Writing to wikibase...')
				r = newprop.write(is_bot=1, clear=False)
				d = True
				print('Successfully written data to prop: '+newprop.id)
				time.sleep(1)
			except Exception:
				ex = traceback.format_exc()
				print(ex)
				presskey = input('Press key for retry.')