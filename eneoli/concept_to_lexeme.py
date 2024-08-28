import csv, time, sys, xwbi, xwb, json

with open('data/languages_table.csv') as csvfile:
	language_table = csv.DictReader(csvfile, delimiter=",")
	#language_name,iso-639-1,iso-639-3,wiki_languagecode,wikibase_item,wikidata_item
	for row in language_table:
		if row['iso-639-1'] == "de":
			continue
		print(f"\nNow processing language {row['language_name']}...\n")
		query = """
		PREFIX enwb: <https://eneoli.wikibase.cloud/entity/>
		PREFIX endp: <https://eneoli.wikibase.cloud/prop/direct/>
		PREFIX enp: <https://eneoli.wikibase.cloud/prop/>
		PREFIX enps: <https://eneoli.wikibase.cloud/prop/statement/>
		PREFIX enpq: <https://eneoli.wikibase.cloud/prop/qualifier/>
		
		select ?concept ?equiv_st ?equiv_mylang ?descript_mylang (iri(concat(str(wd:),?wd)) as ?wikidata) ?sense
		
		where {
		?concept endp:P5 enwb:Q12. # instances of "NeoVoc Concept"
		optional {?concept endp:P1 ?wd.}
		
		?concept enp:P57 ?equiv_st. ?equiv_st enps:P57 ?equiv_mylang. filter(lang(?equiv_mylang)='"""+row['wiki_languagecode']+"""')
			   filter not exists {?equiv_st enpq:P58 ?warning.} # no warning
		#   filter not exists {?no_sense endp:P12 ?concept.} # no lexeme sense already linked to this
			   optional {?equiv_st enpq:P63 ?sense.}
		optional {?concept schema:description ?descript_mylang. filter(lang(?descript_mylang)='"""+row['wiki_languagecode']+"""')}		
		} order by lcase(?equiv_mylang)
		"""
		bindings = xwbi.wbi_helpers.execute_sparql_query(query=query)['results']['bindings']
		# input(json.dumps(bindings, indent=2))
		print('Found ' + str(len(bindings)) + ' results for the query for validated concepts without lexeme sense linked to them.\n')
		time.sleep(1)
		count = 0
		for concept_binding in bindings:
			count += 1
			equiv = concept_binding['equiv_mylang']['value']
			conceptqid = concept_binding['concept']['value'].replace("https://eneoli.wikibase.cloud/entity/","")
			sense_to_concept_link = None
			print(f"\n[{count}] Found validated term: '{equiv}' ({conceptqid})")

			# check if entry with this equiv as lemma exists

			query = """
			PREFIX enwb: <https://eneoli.wikibase.cloud/entity/>
			PREFIX endp: <https://eneoli.wikibase.cloud/prop/direct/>
			
			select ?lexical_entry ?sense ?sense_gloss ?concept ?conceptLabel (iri(concat(str(wd:),?wd)) as ?wikidata)
			
			where {
			  ?lexical_entry a ontolex:LexicalEntry; dct:language enwb:"""+row['wikibase_item']+"""; wikibase:lemma '"""+equiv+"""'@"""+row['wiki_languagecode']+"""; wikibase:lexicalCategory enwb:Q20. 
			  optional {?lexical_entry ontolex:sense ?sense.}
			  optional {?sense endp:P12 ?concept.}
			  optional {?sense skos:definition ?sense_gloss. filter(lang(?sense_gloss)='"""+row['wiki_languagecode']+"""')}
			  optional {?concept endp:P1 ?wd.}
			  }
			"""
			# print(query)
			lex_bindings = xwbi.wbi_helpers.execute_sparql_query(query=query)['results']['bindings']
			lex_bindings2 = lex_bindings
			print('Found ' + str(len(lex_bindings)) + ' senses in the results for the query for lemmata matching to "'+ equiv +'".\n')
			time.sleep(0.5)

			existing = []
			for lex_binding in lex_bindings:
				lid = lex_binding['lexical_entry']['value'].replace("https://eneoli.wikibase.cloud/entity/", "")
				if lid not in existing:
					existing.append(lid)
			if len(existing) > 1:
				print(f'ERROR: There is more than one noun entry for "{equiv}"... Fix that manually.')
				sys.exit()
			elif len(existing) == 0: # create new lexeme
				print(f"Going to create a new noun entry for lemma '{equiv}'.")
				lexeme = xwbi.wbi.lexeme.new(language=row['wikibase_item'], lexical_category="Q20") # noun is default
				lexeme.lemmas.set(language=row['wiki_languagecode'], value=equiv)
				lexeme.claims.add(xwbi.Item(prop_nr='P5', value='Q13')) # instance of NeoVoc Lexical Entry
				concept_to_sense_link = None
			elif len(existing) == 1: # this is the lexeme
				print(f"Lexeme {existing[0]} noun entry has lemma '{equiv}'. We'll check that.")
				existing_conceptlinks = {}
				for lex_binding2 in lex_bindings2: # iterate senses
					print(lex_binding2)
					if 'concept' in lex_binding2:
						existing_conceptlinks[lex_binding2['concept']['value'].replace("https://eneoli.wikibase.cloud/entity/","")] = lex_binding2['sense']['value'].replace("https://eneoli.wikibase.cloud/entity/","")
				if conceptqid in existing_conceptlinks:
					print(f"Concept {conceptqid} is already linked to {existing_conceptlinks[conceptqid]}. Finished {conceptqid}.")
					sense_to_concept_link = existing_conceptlinks[conceptqid]
				else:
					sense_to_concept_link = None
				# get existing lexeme
				lexeme = xwbi.wbi.lexeme.get(entity_id=lex_bindings[0]['lexical_entry']['value'].replace("https://eneoli.wikibase.cloud/entity/",""))

			if not sense_to_concept_link: # create sense
				print(f"Going to create a new sense for lemma '{equiv}', linked to concept {conceptqid}.")
				if 'descript_mylang' in concept_binding:
					gloss = concept_binding['descript_mylang']['value']
				else:
					gloss = f"[Empty gloss; describes concept {conceptqid}]"
				newsense = xwbi.Sense()
				newsense.glosses.set(language=row['wiki_languagecode'], value=gloss)
				newsense.claims.add(xwbi.Item(prop_nr='P12', value=conceptqid))

				lexeme.senses.add(newsense)
				# write entry to wikibase
				done = False
				while not done:
					try:
						lexeme.write()
						done = True
						print(f"Successfully written to {lexeme.id} on ENEOLI Wikibase.")
					except Exception as ex:
						if "404 Client Error" in str(ex):
							print('Got 404 response from wikibase, will wait and try again...')
							time.sleep(10)
						else:
							print('Unexpected error:\n' + str(ex))
				time.sleep(1)


			if 'sense' in concept_binding:
				linked_sense = concept_binding['sense']['value'].replace("https://eneoli.wikibase.cloud/entity/","")
				if linked_sense == sense_to_concept_link:
					print(f"Sense link already there: {equiv} ({conceptqid}) to {linked_sense}.")
					continue

			if not sense_to_concept_link:
				lexemejson = lexeme.get_json()
				for s in lexemejson['senses']:
					if "P12" in s['claims']:
						if s['claims']['P12'][0]['mainsnak']['datavalue']['value']['id'] == conceptqid:
							sense_to_concept_link = s['id']
							break

			equiv_st = concept_binding['equiv_st']['value'].replace("https://eneoli.wikibase.cloud/entity/statement/","")
			print(f"Will try to qualify {equiv_st} with P63 {sense_to_concept_link}...")
			xwb.setqualifier(conceptqid, "P57", equiv_st, "P63", sense_to_concept_link, "string")


# lexeme = xwbi.wbi.lexeme.get(entity_id="L1")
#
# print(lexeme.get_json())