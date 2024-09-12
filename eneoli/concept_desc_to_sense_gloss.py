import csv, time, sys, xwb, xwbi

# This updates sense glosses according to what is found in their corresponding concept's "description" for that language

with open('data/languages_table.csv') as csvfile:
    language_table = csv.DictReader(csvfile, delimiter=",")
    # language_name,iso-639-1,iso-639-3,wiki_languagecode,wikibase_item,wikidata_item
    for row in language_table:
        # if row['iso-639-1'] != "fr":
        #     continue
        print(f"\nNow processing language {row['language_name']}...\n")
        query = """
        PREFIX enwb: <https://eneoli.wikibase.cloud/entity/>
        PREFIX endp: <https://eneoli.wikibase.cloud/prop/direct/>
        
        select ?lexical_entry (lang(?lemma) as ?lang) ?lemma ?sense ?sense_gloss ?concept ?concept_desc
               
        where { 
          ?lexical_entry endp:P5 enwb:Q13; wikibase:lemma ?lemma; ontolex:sense ?sense.
          ?sense skos:definition ?sense_gloss. filter(lang(?sense_gloss)='""" + row['wiki_languagecode'] + """')
          ?sense endp:P12 ?concept.
          ?concept schema:description ?concept_desc. filter(lang(?concept_desc)='""" + row['wiki_languagecode'] + """')
        }
    
		"""
        bindings = xwbi.wbi_helpers.execute_sparql_query(query=query)['results']['bindings']
        print('Found ' + str(
            len(bindings)) + ' results for the query for sense glosses and linked concept descriptions.\n')
        time.sleep(1)
        count = 0
        for binding in bindings:
            count += 1
            print(f"\n[{count}]")
            sense_id = binding['sense']['value']
            sense_gloss = binding['sense_gloss']['value']
            concept_id = binding['concept']['value']
            concept_desc = binding['concept_desc']['value']
            if sense_gloss == concept_desc:
                print(f"Found identical text for {sense_id} and {concept_id}")
            else:
                print(f"Found DIFFERENT text for {sense_id} and {concept_id}. Will copy concept description to sense gloss: {concept_desc}")
                glossdict = {"glosses": {row['wiki_languagecode']: {"language": row['wiki_languagecode'], "value": concept_desc}}}
                xwb.editsense(sense_id=sense_id.replace("https://eneoli.wikibase.cloud/entity/", ""), glossdict=glossdict)
                time.sleep(0.5)

