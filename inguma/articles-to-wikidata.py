# All creators must be already on Wikidata, and all article alignments have to be there (find with zotwb DOI finder)
# Then this query gets the article info necessary for Wikidata:
# PREFIX iwb: <https://wikibase.inguma.eus/entity/>
# PREFIX idp: <https://wikibase.inguma.eus/prop/direct/>
# PREFIX ip: <https://wikibase.inguma.eus/prop/>
# PREFIX ips: <https://wikibase.inguma.eus/prop/statement/>
# PREFIX ipq: <https://wikibase.inguma.eus/prop/qualifier/>
#
# select distinct ?aipatzen_duena ?wd ?inguma ?title ?data (group_concat(distinct concat('"',?sordinal,'": "',?wd_egilea,'"'); SEPARATOR=", ") as ?wd_egileak)
# ?issue ?sp ?ep ?doi
# where {
#   ?oocc_item ip:P89 ?oocc_st.
#
#   ?aipatzen_duena idp:P37 iwb:Q13228; idp:P62 [idp:P88* ?oocc_item].
#
#   ?aipatzen_duena idp:P19 ?data; ip:P17 [ips:P17 ?egilea; ipq:P36 ?sordinal]; idp:P10 ?title. filter(lang(?title)="eu")
#   ?aipatzen_duena idp:P20 ?doi.
#   ?egilea idp:P1 ?wd_egilea.
#   optional {?aipatzen_duena idp:P1 ?wd.}
#   optional {?aipatzen_duena idp:P12 ?inguma.}
#   optional {?aipatzen_duena idp:P26 ?issue.}
#   optional {?aipatzen_duena idp:P27 ?sp.}
#   optional {?aipatzen_duena idp:P28 ?ep.}
#
# }
# group by ?aipatzen_duena ?wd ?inguma ?title ?data ?wd_egileak ?issue ?sp ?ep ?doi

import csv, re, sys, time, json, wdwbi

with open ('data/inguma_artikuluak_wd.csv') as csvfile:
    csvrows = csv.DictReader(csvfile)
    for row in csvrows:
        print(f"\n{row}")

        article_year = row['data'][0:4]
        egileak = json.loads("{"+row['wd_egileak']+"}")

        existing_creators = {}

        inguma_references = wdwbi.References()
        inguma_reference = wdwbi.Reference()
        inguma_reference.add(wdwbi.Item(prop_nr="P248", value="Q12259621"))  # stated in: Inguma
        inguma_reference.add(
            wdwbi.URL(prop_nr="P854", value=row['aipatzen_duena']))  # Inguma entity URI on Inguma Wikibase
        inguma_reference.add(wdwbi.Time(prop_nr="P813", time="now"))
        inguma_references.add(inguma_reference)

        if row['wd'].startswith("Q"): # creator has P1 statement
            print("Will re-use WD item!")
            wd_item = wdwbi.wbi.item.get(entity_id=row['wd'])
        else:
            print("Will make new WD item!")
            wd_item = wdwbi.wbi.item.new()
            wd_item.labels.set("eu", row['title'])
            wd_item.labels.set("en", row['title'])
            wd_item.descriptions.set("eu", f"zientzia-artikulu (ASJU {article_year})")
            wd_item.descriptions.set("en", f"scholarly article (ASJU {article_year})")



        wd_itemjson = wd_item.get_json()

        # egileak
        if "P50" in wd_itemjson['claims']:
            print(wd_itemjson['claims']['P50'])

            for egile_claim in wd_itemjson['claims']['P50']:
                existing_creators[egile_claim['qualifiers']['P1545'][0]['datavalue']['value']] = egile_claim['mainsnak']['datavalue']['value']['id']
            print(existing_creators)

        for listpos in egileak:
            if listpos in existing_creators:
                print(f"Creator listpos #{listpos} is already on WD.")
                if egileak[listpos] == existing_creators[listpos]:
                    print(f"Creator WD Qid is the same: {egileak[listpos]}")
                else:
                    print(f"Creator WD Qid is NOT the same: Wikibase {egileak[listpos]} vs. Wikidata {existing_creators[listpos]}.")
                    input("Press enter to re-write P50 statements.")
                    wd_item.claims.add(
                        wdwbi.Item(prop_nr="P50", value=egileak[listpos],
                                   qualifiers=[wdwbi.String(prop_nr='P1545', value=listpos)],
                                   references=inguma_references), action_if_exists=wdwbi.ActionIfExists.REPLACE_ALL)
            else:
                wd_item.claims.add(
                    wdwbi.Item(prop_nr="P50", value=egileak[listpos], qualifiers=[wdwbi.String(prop_nr='P1545', value=listpos)], references=inguma_references), action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)

        # other pub metadata

        # date (crossref dates are wrong, will be replaced)
        wd_item.claims.add(wdwbi.Time(prop_nr="P577", time=f"+{article_year}-01-01T00:00:00Z", precision=9, references=inguma_references),
                           action_if_exists=wdwbi.ActionIfExists.REPLACE_ALL)

        # pages (crossref "pages" are sp only, will be replaced)
        pages = row['sp']
        if len(row['ep']) > 0:
            pages += "-" + row['ep']
        if len(pages) > 0:
            wd_item.claims.add(wdwbi.String(prop_nr="P304", value=pages, references=inguma_references),
                           action_if_exists=wdwbi.ActionIfExists.REPLACE_ALL)

        # liburukia / volume WD P433 WRONG MATCH to Inguma "issue" P26
        if len(row['issue']) > 0:
            wd_item.claims.add(wdwbi.String(prop_nr="P478", value=row['issue'], references=inguma_references), action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)

        # zenbakia / issue

        # DOI, etc

        wd_item.claims.add(wdwbi.ExternalID(prop_nr="P356", value=row['doi'].upper(), references=inguma_references), action_if_exists=wdwbi.ActionIfExists.REPLACE_ALL)  # DOI
        wd_item.claims.add(wdwbi.Item(prop_nr="P31", value="Q13442814", references=inguma_references),
                           action_if_exists=wdwbi.ActionIfExists.KEEP)  # scholarly article
        wd_item.claims.add(wdwbi.Item(prop_nr="P1433", value="Q96702857", references=inguma_references),
                           action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)  # published in ASJU
        wd_item.claims.add(wdwbi.Item(prop_nr="P275", value="Q24082749", references=inguma_references),
                           action_if_exists=wdwbi.ActionIfExists.KEEP)  # CC-BY-NC-ND 4.0 Intl.
        wd_item.claims.add(wdwbi.MonolingualText(prop_nr="P1476", language="eu", text=row['title'], references=inguma_references), action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)

        wd_item.write()
        print(f"Successfully written to http://www.wikidata.org/entity/{wd_item.id}")
        time.sleep(2)


# remember to delete the P2093 "creator name" statements from Wikidata items

