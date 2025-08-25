import csv, time, sys, xwbi, xwb, json

# This creates lexical entries for those concept equivalents that have no warning but do have a "validated by" statement

duplicates = []
with open('data/languages_table.csv') as csvfile:
	language_table = csv.DictReader(csvfile, delimiter=",")
	#language_name,iso-639-1,iso-639-3,wiki_languagecode,wikibase_item,wikidata_item
	for row in language_table:
		do_not_check = []
		if row['iso-639-1'] in do_not_check:
			continue
		print(f"\nNow processing language {row['language_name']}...\n")
		query = """
		PREFIX enwb: <https://eneoli.wikibase.cloud/entity/>
		PREFIX endp: <https://eneoli.wikibase.cloud/prop/direct/>
		PREFIX enp: <https://eneoli.wikibase.cloud/prop/>
		PREFIX enps: <https://eneoli.wikibase.cloud/prop/statement/>
		PREFIX enpq: <https://eneoli.wikibase.cloud/prop/qualifier/>
		
		select distinct ?concept ?collection ?termpos ?equiv_st ?equiv_mylang ?descript_mylang (iri(concat(str(wd:),?wd)) as ?wikidata) ?sense
		
		where {
		# ?concept endp:P5 enwb:Q12. # instances of "NeoVoc Concept"
		# ?concept endp:P82 enwb:Q51. # part of "Gender" collection
		?concept endp:P82 ?collection. # part of any collection
		optional {?concept endp:P1 ?wd.}
		optional {?concept endp:P92 ?termpos.}
		?concept enp:P57 ?equiv_st. ?equiv_st enps:P57 ?equiv_mylang. filter(lang(?equiv_mylang)='"""+row['wiki_languagecode']+"""')
			   filter not exists {?equiv_st enpq:P58 ?warning.} # no warning
			   ?equiv_st enpq:P64 ?validator. # has been validated.
		   filter not exists {?no_lexeme dct:language enwb:"""+row['wikibase_item']+"""; ontolex:sense [endp:P12 ?concept].} # no lexeme sense already linked to this
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
			collectionqid = concept_binding['collection']['value'].replace("https://eneoli.wikibase.cloud/entity/","")
			conceptqid = concept_binding['concept']['value'].replace("https://eneoli.wikibase.cloud/entity/","")
			if conceptqid.startswith("L"): # somebody added an equivalent to a lexeme, not a concept
				input(f"https//eneoli.wikibase.cloud/entity/{conceptqid} is a lexeme, not a concept. Enter to resume.\n")
				continue
			sense_to_concept_link = None
			if 'termpos' in concept_binding:
				termpos = concept_binding['termpos']['value'].replace("https://eneoli.wikibase.cloud/entity/","")
			else:
				termpos = "Q20" # noun is default
			print(f"\n[{count}] Found validated term: '{equiv}'@{row['wiki_languagecode']} (https://eneoli.wikibase.cloud/entity/{conceptqid})")

			# check if entry with this equiv as lemma exists

			query = """
			PREFIX enwb: <https://eneoli.wikibase.cloud/entity/>
			PREFIX endp: <https://eneoli.wikibase.cloud/prop/direct/>
			
			select ?lexical_entry ?sense ?sense_gloss ?concept ?conceptLabel (iri(concat(str(wd:),?wd)) as ?wikidata)
			
			where {
			  ?lexical_entry endp:P82 ?collection; dct:language enwb:"""+row['wikibase_item']+"""; wikibase:lemma """+'"'+equiv+'"@'+row['wiki_languagecode']+"""; wikibase:lexicalCategory enwb:"""+termpos+""". 
			  ?lexical_entry ontolex:sense ?sense.
			  optional {?sense endp:P12 ?concept.}
			  optional {?sense skos:definition ?sense_gloss. filter(lang(?sense_gloss)='"""+row['wiki_languagecode']+"""')}
			  optional {?concept endp:P1 ?wd.}
			  }
			"""
			#print(query)
			lex_bindings = xwbi.wbi_helpers.execute_sparql_query(query=query)['results']['bindings']
			lex_bindings2 = lex_bindings
			print('Found ' + str(len(lex_bindings)) + ' senses in the results for the query for lemmata matching to "'+ equiv +'".\n')
			time.sleep(0.5)

			created_lexemes = {}
			existing = []
			for lex_binding in lex_bindings:
				lid = lex_binding['lexical_entry']['value'].replace("https://eneoli.wikibase.cloud/entity/", "")
				if lid not in existing and lid not in ["L1527", "L1528", "L1529", "L1530", "L1531", "L1532", "L1533", "L1534", "L1535", "L1536", "L1537", "L1538", "L1539", "L1540", "L1541", "L1542", "L1543", "L1544", "L1549", "L1550", "L1551", "L1552", "L1557", "L1558", "L1559", "L1560", "L1561", "L1562", "L1563", "L1564", "L1569", "L1570", "L1571", "L1572", "L1573", "L1574", "L1575", "L1576", "L1579", "L1580", "L1581", "L1582", "L1583", "L1584", "L1585", "L1586", "L1587", "L1588", "L1589", "L1590", "L1595", "L1596", "L1599", "L1600", "L1601", "L1602", "L1603", "L1604", "L1605", "L1606", "L1607", "L1608", "L1609", "L1610", "L1613", "L1614", "L1615", "L1616", "L1617", "L1618", "L1619", "L1620", "L1621", "L1622", "L1623", "L1624", "L1625", "L1626", "L1627", "L1628", "L1629", "L1630", "L1631", "L1632", "L1635", "L1636", "L1637", "L1638", "L1641", "L1642", "L1643", "L1644", "L1647", "L1648", "L1649", "L1650", "L1651", "L1652", "L1653", "L1654", "L1657", "L1658", "L1659", "L1660", "L1661", "L1662", "L1665", "L1666", "L1667", "L1668", "L1669", "L1670", "L1673", "L1674", "L1675", "L1676", "L1677", "L1678", "L1679", "L1680", "L1681", "L1682", "L1683", "L1684", "L1685", "L1686", "L1687", "L1688", "L1689", "L1690", "L1691", "L1692", "L1693", "L1694", "L1697", "L1698", "L1699", "L1700", "L1701", "L1702", "L1703", "L1704", "L1705", "L1706", "L1707", "L1708", "L1709", "L1710", "L1711", "L1712", "L1713", "L1714", "L1716", "L1717", "L1718", "L1719", "L1720", "L1721", "L1722", "L1723", "L1724", "L1725", "L1726", "L1727", "L1728", "L1729", "L1730", "L1731", "L1732", "L1733", "L1736", "L1737", "L1738", "L1739", "L1740", "L1741", "L1742", "L1743", "L1744", "L1745", "L1746", "L1747", "L1748", "L1749", "L1750", "L1751", "L1752", "L1753", "L1754", "L1755"]:
					existing.append(lid)
			if len(existing) > 1:
				print(f'ERROR: There is more than one {termpos} entry for "{equiv}"... Fix that manually! We skip this equiv in this run of the script.')
				duplicates.append((f"<https://eneoli.wikibase.cloud/entity/{existing[0]}>",f"<https://eneoli.wikibase.cloud/entity/{existing[1]}>"))
				continue # skip this equiv in this run
			elif len(existing) == 0: # check if created in this run; create new lexeme
				if equiv in created_lexemes:
					print(f"Re-using an entry created in this run for lemma '{equiv}': {created_lexemes[equiv]}.")
					lexeme = xwbi.lexeme.get(entity_id=created_lexemes[equiv])
				else:
					print(f"Going to create a new {collectionqid} collection (POS={termpos}) entry for lemma '{equiv}'.")
					lexeme = xwbi.wbi.lexeme.new(language=row['wikibase_item'], lexical_category=termpos)
					lexeme.lemmas.set(language=row['wiki_languagecode'], value=equiv)
					lexeme.claims.add(xwbi.Item(prop_nr='P82', value=collectionqid)) # part of same collection as concept
				concept_to_sense_link = None
			elif len(existing) == 1: # this is the lexeme
				print(f"Lexeme {existing[0]} {termpos} entry has lemma '{equiv}'. We'll check that.")
				existing_conceptlinks = {}
				for lex_binding2 in lex_bindings2: # iterate senses
					print(lex_binding2)
					if 'concept' in lex_binding2:
						existing_conceptlinks[lex_binding2['concept']['value'].replace("https://eneoli.wikibase.cloud/entity/","")] = lex_binding2['sense']['value'].replace("https://eneoli.wikibase.cloud/entity/","")
				if conceptqid in existing_conceptlinks:
					print(f"Concept {conceptqid} is already linked from sense {existing_conceptlinks[conceptqid]}. Finished {conceptqid}.")
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
						created_lexemes[equiv] = lexeme.id
						done = True
						print(f"Successfully written to {lexeme.id} '{equiv}' on ENEOLI Wikibase.")
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

print(f"\nFinished. The following duplicates were found, that has to be fixed!!\n\n{duplicates}")