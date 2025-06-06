import csv, time, sys, xwbi

with open('data/languages_table.csv') as csvfile:
    language_table = csv.DictReader(csvfile, delimiter=",")
    # language_name,iso-639-1,iso-639-3,wiki_languagecode,wikibase_item,wikidata_item
    for row in language_table:
        # if row['iso-639-1'] != "eu":
        #     continue
        print(f"\nNow processing language {row['language_name']}...\n")
        query = """
        PREFIX enwb: <https://eneoli.wikibase.cloud/entity/>
		PREFIX endp: <https://eneoli.wikibase.cloud/prop/direct/>
		PREFIX enp: <https://eneoli.wikibase.cloud/prop/>
		PREFIX enps: <https://eneoli.wikibase.cloud/prop/statement/>
		PREFIX enpq: <https://eneoli.wikibase.cloud/prop/qualifier/>

		select distinct ?concept (group_concat(distinct str(?equiv_mylang);SEPARATOR="|") as ?equivs) ?label_mylang  (group_concat(distinct str(?altlabel_mylang);SEPARATOR="|") as ?altlabels)

		where {
		?concept endp:P82 []. # concepts of some collection.

		?concept enp:P57 ?equiv_st. ?equiv_st enps:P57 ?equiv_mylang. filter(lang(?equiv_mylang)='""" + row[
            'wiki_languagecode'] + """')
            ?equiv_st enpq:P64 ?validator. # has been validated.
			   filter not exists {?equiv_st enpq:P58 ?warning.} # no warning

        optional {?concept rdfs:label ?label_mylang. filter(lang(?label_mylang)='""" + row[
                    'wiki_languagecode'] + """')}
        optional {?concept skos:altLabel ?altlabel_mylang. filter(lang(?altlabel_mylang)='""" + row[
                    'wiki_languagecode'] + """')}


		} group by ?concept ?equivs ?label_mylang ?altlabels order by lcase(?equiv_mylang)    
		"""
        bindings = xwbi.wbi_helpers.execute_sparql_query(query=query)['results']['bindings']
        print('Found ' + str(
            len(bindings)) + ' results for the query concepts without warnings for this language.\n')
        time.sleep(1)
        count = 0
        for concept_binding in bindings:
            count += 1
            equivs = concept_binding['equivs']['value'].split("|")
            if 'label_mylang' in concept_binding:
                preflabel = concept_binding['label_mylang']['value']
            else:
                preflabel = None
            if 'altlabels' in concept_binding:
                altlabels = concept_binding['altlabels']['value'].split("|")
            else:
                altlabels = []
            conceptqid = concept_binding['concept']['value'].replace("https://eneoli.wikibase.cloud/entity/", "")
            print(f"\n[{count}] Now processing {conceptqid} with equivs: {equivs}")

            wb_item = xwbi.wbi.item.get(entity_id=conceptqid)
            # wb_item_json = wb_item.get_json()
            need_to_write = False
            if len(equivs) == 1:
                if equivs[0] != preflabel:
                    wb_item.labels.set(language=row['wiki_languagecode'], value=equivs[0])
                    print(f"Updated prefLabel from {preflabel} to {equivs[0]}")
                    need_to_write = True
                else:
                    if len(altlabels) > 0:
                        wb_item.aliases.set(language=row['wiki_languagecode'], values=[],
                                            action_if_exists=xwbi.ActionIfExists.REPLACE_ALL)
                        need_to_write = True
            else:
                if preflabel not in equivs:
                    equiv = equivs.pop(0)
                    wb_item.labels.set(language=row['wiki_languagecode'], value=equiv)
                    print(f"Updated prefLabel from {preflabel} to {equiv}")
                    need_to_write = True
                else:
                    equivs.remove(preflabel)
                    print(f"PrefLabel '{preflabel}' is OK. Will write to altlabel: {equivs}")
                wb_item.aliases.set(language=row['wiki_languagecode'], values=equivs,
                                    action_if_exists=xwbi.ActionIfExists.REPLACE_ALL)
                print(f"Set altLabels to {equivs}.")
                need_to_write = True
            if need_to_write:
                done = False
                while not done:
                    try:
                        wb_item.write()
                        done = True
                        print(f"Successfully written to {wb_item.id} on ENEOLI Wikibase.")
                    except Exception as ex:
                        if "404 Client Error" in str(ex):
                            print('Got 404 response from wikibase, will wait and try again...')
                            time.sleep(10)
                        else:
                            print('Unexpected error:\n' + str(ex))
                time.sleep(1)
            else:
                print(f"There was no need to change {conceptqid}.")