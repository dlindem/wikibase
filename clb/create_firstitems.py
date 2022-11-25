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
with open('data/Q_1_200.csv', 'r', encoding="utf-8") as file:
	propsdict = csv.DictReader(file)
	newitems = {}
	for row in propsdict:
		plannedqid = row['wikibase_item'].strip()
		print('\nWill process data for '+plannedqid+'...')
		enlabel = row['label'].strip()
		classqid = row['P5'].strip()

		newitem = clbwbi.wbi.item.new()
		newitem.labels.set('en',enlabel)
		print('enlabel set: '+enlabel)
		if classqid.startswith("Q"):
			newitem.claims.add(clbwbi.Item(value=classqid,prop_nr='P5'))
			print('P5 set: '+classqid)

		d = False
		while d == False:
			try:
				print('Writing to clb wikibase...')
				r = newitem.write(is_bot=1, clear=False)
				d = True
				print('Successfully written data planned for '+plannedqid+' to item: '+newitem.id)
			except Exception:
				ex = traceback.format_exc()
				print(ex)
				presskey = input('Press key for retry.')
