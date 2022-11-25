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
with open('data/props.csv', 'r', encoding="utf-8") as file:
	propsdict = csv.DictReader(file)
	newprops = {}
	for row in propsdict:
		plannedqid = row['prop'].strip()
		print('\nWill process data for '+plannedqid+'...')
		enlabel = row['propLabel'].strip()
		dtype = datatype[row['datatype']]
		wdpid = row['wd'].strip()
		formatterUrl = row['formatterUrl'].strip()
		newprop = clbwbi.wbi.property.new(datatype=dtype)
		newprop.labels.set('en',enlabel)
		print('enlabel set: '+enlabel)
		if wdpid.startswith("P"):
			newprop.claims.add(clbwbi.ExternalID(value=wdpid,prop_nr='P1'))
			print('P1 set: '+wdpid)
		if formatterUrl.startswith('http'):
			newprop.claims.add(clbwbi.String(value=formatterUrl,prop_nr='P2'))
			print('P2 set: '+formatterUrl)
		presskey = input('Press Enter for writing data for '+plannedqid)
		d = False
		while d == False:
			try:
				print('Writing to clb wikibase...')
				r = newprop.write(is_bot=1, clear=False)
				d = True
				print('Successfully written data planned for '+plannedqid+' to item: '+newprop.id)
			except Exception:
				ex = traceback.format_exc()
				print(ex)
				presskey = input('Press key for retry.')
