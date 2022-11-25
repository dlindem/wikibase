import clbwbi
import csv, traceback

datatype = {
    'http://wikiba.se/ontology#ExternalId' : 'external-id',
    'http://wikiba.se/ontology#WikibaseForm' : 'wikibase-form',
    'http://wikiba.se/ontology#GeoShape' : 'geo-shape',
    'http://wikiba.se/ontology#GlobeCoordinate' : 'globe-coordinate',
    'http://wikiba.se/ontology#WikibaseItem' : 'wikibase-item',
    'http://wikiba.se/ontology#WikibaseLexeme' : 'wikibase-lexeme',
    'http://wikiba.se/ontology#Math' : 'math',
    'http://wikiba.se/ontology#Monolingualtext' : 'monolingualtext',
    'http://wikiba.se/ontology#MusicalNotation' : 'musical-notation',
    'http://wikiba.se/ontology#WikibaseProperty' : 'wikibase-property',
    'http://wikiba.se/ontology#Quantity' : 'quantity',
    'http://wikiba.se/ontology#WikibaseSense' : 'wikibase-sense',
    'http://wikiba.se/ontology#String' : 'string',
    'http://wikiba.se/ontology#TabularData' : 'tabular-data',
    'http://wikiba.se/ontology#Time' : 'time',
    'http://wikiba.se/ontology#Url' : 'url'}

# load props.csv
# P! has to be 'wikidata entity', externalID; P2 has to be 'formatterUrl', string
with open('data/creatorprops.csv', 'r', encoding="utf-8") as file:
	propsdict = csv.DictReader(file)
	newprops = {}
	for row in propsdict:
		dtype = datatype[row['datatype']]
		if row['prop'].startswith("P"):
			plannedqid = row['prop'].strip()
			newprop = clbwbi.wbi.property.get(entity_id=plannedqid)
		else:
			newprop = clbwbi.wbi.property.new(datatype=dtype)

		enlabel = row['propLabel'].strip()
		print('\nWill process data for '+enlabel+'...')
		newprop.labels.set('en',enlabel)
		print('enlabel is: '+newprop.labels.get('en').value)
		marc = row['marc'].strip()
		newprop.claims.add(clbwbi.String(value=marc,prop_nr='P59'))

		# if formatterUrl.startswith('http'):
		# 	newprop.claims.add(clbwbi.String(value=formatterUrl,prop_nr='P2'))
		# 	print('P2 set: '+formatterUrl)
		# presskey = input('Press Enter for writing data for '+plannedqid)
		d = False
		while d == False:
			try:
				print('Writing to clb wikibase...')
				r = newprop.write(is_bot=1, clear=False)
				d = True
				print('Successfully written data to item: '+newprop.id)
			except Exception:
				ex = traceback.format_exc()
				print(ex)
				presskey = input('Press key for retry.')
