# Asks for creators with P1 statement on Wikibase OR inguma statement on Wikidata
# PREFIX iwb: <https://wikibase.inguma.eus/entity/>
# PREFIX idp: <https://wikibase.inguma.eus/prop/direct/>
# PREFIX ip: <https://wikibase.inguma.eus/prop/>
# PREFIX ips: <https://wikibase.inguma.eus/prop/statement/>
# PREFIX ipq: <https://wikibase.inguma.eus/prop/qualifier/>
#
# select distinct ?egilea ?egilea_label ?wd ?wikidata ?inguma ?ing_wikidata
#
# where {
#   ?oocc_item ip:P89 ?oocc_st.
#
#   ?aipatzen_duena idp:P37 iwb:Q13228; idp:P62 [idp:P88* ?oocc_item].
#
#
#   ?aipatzen_duena idp:P19 ?data; idp:P17 ?egilea; idp:P10 ?title. filter(lang(?title)="eu")
#   ?egilea rdfs:label ?egilea_label. filter(lang(?egilea_label)="en")
#   optional {?egilea idp:P3 ?inguma.}
#   optional {
#
#    SERVICE <https://query.wikidata.org/sparql> {
#            select ?ing_wikidata ?inguma where
#                             {?ing_wikidata wdt:P7558 ?inguma.}
#    } }
#    optional {?egilea idp:P1 ?wd. bind(iri(concat(str(wd:),?wd)) as ?wikidata)}
#
# }
import csv, re, sys, time, wdwbi, requests

prop_map = {}



with open ('data/inguma_egileak_wd.csv') as csvfile:
    csvrows = csv.DictReader(csvfile)
    for row in csvrows:
        print(f"\n{row}")

        inguma_references = wdwbi.References()
        inguma_reference = wdwbi.Reference()
        inguma_reference.add(wdwbi.Item(prop_nr="P248", value="Q12259621"))  # stated in: Inguma
        inguma_reference.add(wdwbi.ExternalID(prop_nr="P7558", value=row['inguma']))  # Inguma ID
        inguma_reference.add(wdwbi.Time(prop_nr="P813", time="now"))
        inguma_references.add(inguma_reference)

        egilea_qid = row['egilea'].replace("https://wikibase.inguma.eus/entity/","")
        egile_izena = re.sub(r'\([^\)]*\)', '', row['egilea_label']).strip()
        print(f"Egilearen izena: {egile_izena}")

       # wb_item = iwbi.wbi.item.get(entity_id=egilea_qid)
        wb_itemjson = requests.get(f"https://wikibase.inguma.eus/wiki/Special:EntityData/{egilea_qid}.json").json()['entities'][egilea_qid]

        if row['wd'].startswith("Q"): # creator has P1 statement
            print("Will re-use WD item!")
            wd_item = wdwbi.wbi.item.get(entity_id=row['wd'])
        else:
            print("Will make new WD item!")
            wd_item = wdwbi.wbi.item.new()
            wd_item.labels.set("eu", egile_izena)
            wd_item.labels.set("en", egile_izena)
            wd_item.descriptions.set("eu", "ikertzailea")
            wd_item.descriptions.set("en", "researcher")
            wd_item.claims.add(wdwbi.Item(prop_nr="P31", value="Q5", references=inguma_references)) # human
            wd_item.claims.add(wdwbi.Item(prop_nr="P106", value="Q1650915", references=inguma_references)) # researcher


        # name in native language
        wd_item.claims.add(wdwbi.MonolingualText(prop_nr="P1559", text=egile_izena, language="eu", references=inguma_references))
        # euskaraz badaki
        wd_item.claims.add(wdwbi.Item(prop_nr="P1412", value="Q8752", references=inguma_references), action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)
        # inguma id
        wd_item.claims.add(wdwbi.ExternalID(prop_nr="P7558", value=row['inguma']), action_if_exists=wdwbi.ActionIfExists.REPLACE_ALL)
        # gender
        if 'P50' in wb_itemjson['claims']:
            if wb_itemjson['claims']['P50'][0]['mainsnak']['datavalue']['value']['id'] == "Q31":
                print("Female person.")
                wd_item.claims.add(wdwbi.Item(prop_nr="P21", value="Q6581072", references=inguma_references),
                                   action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)
            elif wb_itemjson['claims']['P50'][0]['mainsnak']['datavalue']['value']['id'] == "Q32":
                print("Male person.")
                wd_item.claims.add(wdwbi.Item(prop_nr="P21", value="Q6581097", references=inguma_references),
                                action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)
        # ORCID
        if 'P39' in wb_itemjson['claims']:
            orcid_id = wb_itemjson['claims']['P39'][0]['mainsnak']['datavalue']['value']
            print(f"ORCID: {orcid_id}")
            wd_item.claims.add(wdwbi.ExternalID(prop_nr="P496", value=orcid_id),
                               action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)

        # date of birth
        if 'P44' in wb_itemjson['claims']:
            birthdate = wb_itemjson['claims']['P44'][0]['mainsnak']['datavalue']['value']['time']
            precision = wb_itemjson['claims']['P44'][0]['mainsnak']['datavalue']['value']['precision']
            print(f"Birthdate: {birthdate}")
            wd_item.claims.add(wdwbi.Time(prop_nr="P569", time=birthdate, precision=precision),
                               action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)


        wd_item.write()
        print(f"Successful writing operation to {wd_item.id}")
        time.sleep(2)



