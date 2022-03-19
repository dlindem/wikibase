import iwbi, csv

# datatype mapping from wdi config
datatype_mapping = {'commonsMedia': 'http://wikiba.se/ontology#CommonsMedia' ,
                'external-id': 'http://wikiba.se/ontology#ExternalId' ,
                'geo-shape': 'http://wikiba.se/ontology#GeoShape',
                'globe-coordinate': 'http://wikiba.se/ontology#GlobeCoordinate',
                'math': 'http://wikiba.se/ontology#Math',
                'monolingualtext': 'http://wikiba.se/ontology#Monolingualtext',
                'quantity': 'http://wikiba.se/ontology#Quantity',
                'string': 'http://wikiba.se/ontology#String',
                'tabular-data': 'http://wikiba.se/ontology#TabularData',
                'time': 'http://wikiba.se/ontology#Time',
                'edtf': '<http://wikiba.se/ontology#Edtf>',
                'url': 'http://wikiba.se/ontology#Url',
                'wikibase-item': 'http://wikiba.se/ontology#WikibaseItem',
                'wikibase-property': 'http://wikiba.se/ontology#WikibaseProperty',
                'lexeme': 'http://wikiba.se/ontology#WikibaseLexeme',
                'form': 'http://wikiba.se/ontology#WikibaseForm',
                'sense': 'http://wikiba.se/ontology#WikibaseSense',
                'musical-notation': 'http://wikiba.se/ontology#MusicalNotation',
                'schema': 'http://schema.org/'
                }


with open('props.csv', 'r', encoding="utf-8") as csvfile:
	props = csv.DictReader(csvfile)

	for prop in props:
		print("\n"+str(prop))
		for dtype in datatype_mapping:
			if datatype_mapping[dtype] == prop['datatype']:
				datatype = dtype
				break

		data = []

		if prop['wd'].startswith("P"): # if csv has value for Wikidata equivalent
			data.append(iwbi.wbi_datatype.ExternalID(value=prop['wd'], prop_nr="P1"))
		if prop['formUrl'].startswith("http"): # if csv has value for formatter URL
			data.append(iwbi.wbi_datatype.String(value=prop['formUrl'], prop_nr="P2"))


		wb_item = iwbi.wbi_core.ItemEngine(new_item=True,data=data)
		wb_item.set_label(prop['propLabel'], lang="en", if_exists='REPLACE')
		result = wb_item.write(iwbi.login_instance, entity_type="property", property_datatype=datatype)

		print(str(result), "done.")
