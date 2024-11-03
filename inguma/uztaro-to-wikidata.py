# All creators must be already on Wikidata, and all article alignments have to be there (find with zotwb DOI finder)
# Then this query gets the article info necessary for Wikidata:
# PREFIX iwb: <https://wikibase.inguma.eus/entity/>
# PREFIX idp: <https://wikibase.inguma.eus/prop/direct/>
# PREFIX ip: <https://wikibase.inguma.eus/prop/>
# PREFIX ips: <https://wikibase.inguma.eus/prop/statement/>
# PREFIX ipq: <https://wikibase.inguma.eus/prop/qualifier/>
#
# select distinct ?artikulua ?wd ?inguma ?title ?data (group_concat(distinct concat('"',?sordinal,'": "',?wd_egilea,'"'); SEPARATOR=", ") as ?wd_egileak)
# ?issue ?sp ?ep ?doi ?ojs_landing ?update
# where {
#
#
#   ?artikulua idp:P37 iwb:Q13091.# ; idp:P59 iwb:Q13367.
#
#   ?artikulua idp:P19 ?data; ip:P17 [ips:P17 ?egilea; ipq:P36 ?sordinal]; idp:P10 ?title. filter(lang(?title)="eu")
#   optional {?artikulua idp:P20 ?doi.}
#   ?egilea idp:P1 ?wd_egilea.
#   optional {?artikulua idp:P1 ?wd. bind(iri(concat(str(wd:),?wd)) as ?wikidata_item)
#            SERVICE <https://query.wikidata.org/sparql> {
#            select ?wikidata_item ?update where {?wikidata_item p:P31 [ps:P31 wd:Q13442814; prov:wasDerivedFrom [pr:P248 wd:Q12259621; pr:P813 ?update]].}
#     }
#            }
#   optional {?artikulua idp:P12 ?inguma.}
#   ?artikulua idp:P26 ?issue.
#   optional {?artikulua idp:P27 ?sp.}
#   optional {?artikulua idp:P28 ?ep.}
#   ?artikulua idp:P24 ?ojs_landing.
#
#
#
#
#
# }
# group by ?artikulua ?wd ?inguma ?title ?data ?wd_egileak ?issue ?sp ?ep ?doi ?ojs_landing ?update

import csv, re, sys, time, json, wdwbi, iwb

with open ('data/inguma-uztaro-articles.csv') as csvfile:
    csvrows = csv.DictReader(csvfile, delimiter="\t")
    count = 0
    for row in csvrows:
        count += 1
        print(f"\n[{count}] {row}")
        # if str(row['wd_upload']).startswith("2024-11"):
        #     print("Already updated, skipped.")
        #     continue
        article_wbqid = row['artikulua'].replace("https://wikibase.inguma.eus/entity/","")
        title = row['title']
        p1guid = row['p1guid'].replace("https://wikibase.inguma.eus/entity/statement/","")
        article_year = row['data'][0:4]
        egileak = json.loads("{"+row['wd_egileak']+"}")
        egileak = dict(sorted(egileak.items()))
        print(f"Egileak-dict: {egileak}")
        existing_creators = {}

        inguma_references = wdwbi.References()
        inguma_reference = wdwbi.Reference()
        inguma_reference.add(wdwbi.Item(prop_nr="P248", value="Q12259621"))  # stated in: Inguma
        inguma_reference.add(
            wdwbi.URL(prop_nr="P854", value=row['artikulua']))  # Inguma entity URI on Inguma Wikibase
        inguma_reference.add(wdwbi.Time(prop_nr="P813", time="now"))
        inguma_references.add(inguma_reference)



        if row['wd'].startswith("Q"): # article has P1 statement
            p1link = row['wd']
            wd_item = wdwbi.wbi.item.get(entity_id=p1link)
            wd_eulabel = wd_item.labels.get("eu")
            wd_eualtlabels = wd_item.aliases.get("eu")
            if not wd_eualtlabels:
                wd_eualtlabels = []
            print(f"EU Name on Wikidata is {wd_eulabel}")
            if not wd_eulabel:
                wd_item.labels.set("eu", title)
            elif wd_eulabel != title and title not in wd_eualtlabels:
                wd_item.aliases.set("eu", title)
            wd_enlabel = wd_item.labels.get("en")
            print(f"EN Name on Wikidata is {wd_enlabel}")
            if not wd_enlabel:
                wd_item.labels.set("en", title)

        else:
            print("Will make new WD item!")
            p1link = None
            wd_item = wdwbi.wbi.item.new()
            wd_item.labels.set("eu", title)
            wd_item.labels.set("en", title)
            wd_item.descriptions.set("eu", f"zientzia-artikulu (Uztaro, {article_year})")
            wd_item.descriptions.set("en", f"scholarly article (Uztaro, {article_year})")



        wd_itemjson = wd_item.get_json()

        # egileak
        firstegile = True
        # if "P50" in wd_itemjson['claims']:
        #     print(wd_itemjson['claims']['P50'])
        #
        #     for egile_claim in wd_itemjson['claims']['P50']:
        #         existing_creators[egile_claim['qualifiers']['P1545'][0]['datavalue']['value']] = egile_claim['mainsnak']['datavalue']['value']['id']
        #     print(existing_creators)

        for listpos in egileak:
            # if listpos in existing_creators:
            #     print(f"Creator listpos #{listpos} is already on WD.")
            #     if egileak[listpos] == existing_creators[listpos]:
            #         print(f"Creator WD Qid is the same: {egileak[listpos]}")
            #     else:
            #         print(f"Creator WD Qid is NOT the same: Wikibase {egileak[listpos]} vs. Wikidata {existing_creators[listpos]}.")
            #         input("Press enter to re-write P50 statements.")
            #         wd_item.claims.add(
            #             wdwbi.Item(prop_nr="P50", value=egileak[listpos],
            #                        qualifiers=[wdwbi.String(prop_nr='P1545', value=listpos)],
            #                        references=inguma_references), action_if_exists=wdwbi.ActionIfExists.REPLACE_ALL)
            # else:

            # seriesqualis = [wdwbi.String(prop_nr='P1545', value=listpos)]
            seriesqualis = [] # inguma wikibase series ordinals are not in the right order for Uztaro # TODO: get from crossref
            if firstegile:    # overwrite existing P50 statements
                wd_item.claims.add(
                        wdwbi.Item(prop_nr="P50", value=egileak[listpos], qualifiers=seriesqualis, references=inguma_references), action_if_exists=wdwbi.ActionIfExists.REPLACE_ALL)
                firstegile = False
            else:
                wd_item.claims.add(
                        wdwbi.Item(prop_nr="P50", value=egileak[listpos], qualifiers=seriesqualis, references=inguma_references), action_if_exists=wdwbi.ActionIfExists.FORCE_APPEND)

        # other pub metadata

        ojs_references = wdwbi.References()
        ojs_reference = wdwbi.Reference()
        ojs_reference.add(
            wdwbi.URL(prop_nr="P854", value=row['ojs_landing']))  # OJS landing page
        ojs_references.add(ojs_reference)

        # OJS page
        wd_item.claims.add(wdwbi.URL(prop_nr="P973", value=row['ojs_landing'], references=inguma_references), action_if_exists=wdwbi.ActionIfExists.REPLACE_ALL)
        wd_item.claims.add(wdwbi.URL(prop_nr="P953", value=row['pdf'], references=ojs_references), action_if_exists=wdwbi.ActionIfExists.REPLACE_ALL)  # pdf download link

        # date
        wd_item.claims.add(wdwbi.Time(prop_nr="P577", time=f"+{article_year}-01-01T00:00:00Z", precision=9, references=inguma_references),
                           action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)

        # pages
        pages = row['sp']
        if len(row['ep']) > 0:
            pages += "-" + row['ep']
        if len(pages) > 0:
            wd_item.claims.add(wdwbi.String(prop_nr="P304", value=pages, references=inguma_references),
                           action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)

        # zenbakia / isue wdt:P433 match to Inguma "issue" P26
        if len(row['issue']) > 0:
            wd_item.claims.add(wdwbi.String(prop_nr="P433", value=row['issue'], references=inguma_references), action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)

        # DOI, etc

        if len(row['doi']) > 0:
            wd_item.claims.add(wdwbi.ExternalID(prop_nr="P356", value=row['doi'].upper(), references=inguma_references), action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)  # DOI
        wd_item.claims.add(wdwbi.Item(prop_nr="P31", value="Q13442814", references=inguma_references),
                           action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)  # scholarly article
        wd_item.claims.add(wdwbi.Item(prop_nr="P407", value="Q8752", references=inguma_references),
                           action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)  # language euskara
        wd_item.claims.add(wdwbi.Item(prop_nr="P1433", value="Q12268801", references=inguma_references),
                           action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)  # published in Uztaro
        wd_item.claims.add(wdwbi.Item(prop_nr="P275", value="Q42553662", references=ojs_references),
                           action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)  # CC BY-NC-SA 4.0
        wd_item.claims.add(wdwbi.MonolingualText(prop_nr="P1476", language="eu", text=row['title'], references=inguma_references),
                           action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)

        try:
            wd_item.write()
            print(f"Successfully written to http://www.wikidata.org/entity/{wd_item.id}")
            if not p1link:
                iwb.stringclaim(article_wbqid, "P1", wd_item.id)
            if p1link and p1link != wd_item.id:
                print("Will UPDATE P1!!")
                iwb.setclaimvalue(p1guid, wd_item.id, "string")

        except Exception as ex:
            dup_re = re.search(r'Item \[\[Q\d+\|(Q\d+)\]\] already has label', str(ex))
            if dup_re:
                print("DUPLICATE.")
            else:
                input(str(ex)+ "\n\nPress Enter to skip this item and proceed.")
        time.sleep(2)


# remember to delete the P2093 "creator name" statements from Wikidata items

