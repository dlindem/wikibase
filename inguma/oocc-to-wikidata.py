# https://wikibase.inguma.eus/wiki/KM_Wikidata_export#Export_OOCC_articles_(for_oocc-to-wikidata.py)

import csv, re, sys, time, json, wdwbi, iwb

with open ('data/inguma_oocc_wd.csv') as csvfile:
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
            wdwbi.URL(prop_nr="P854", value=row['oocc_item']))  # Inguma entity URI on Inguma Wikibase
        inguma_reference.add(wdwbi.Time(prop_nr="P813", time="now"))
        inguma_references.add(inguma_reference)

        if row['oocc_wd'].startswith("Q"): # creator has P1 statement
            continue # no chek of existing
            print("Will re-use WD item!")
            wd_item = wdwbi.wbi.item.get(entity_id=row['oocc_wd'])
        else:
            print("Will make new WD item!")
            wd_item = wdwbi.wbi.item.new()
            wd_item.labels.set(row['title_lang'], row['title'])

        wd_itemjson = wd_item.get_json()

        # egileak
        if "P50" in wd_itemjson['claims']:
            print(wd_itemjson['claims']['P50'])

            for egile_claim in wd_itemjson['claims']['P50']:
                try:
                    existing_creators[egile_claim['qualifiers']['P1545'][0]['datavalue']['value']] = egile_claim['mainsnak']['datavalue']['value']['id']
                except:
                    existing_creators["1"] = egile_claim['mainsnak']['datavalue']['value']['id']
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

        # published in an pages
        if len(row['pag']) > 0:
            page_quali = [wdwbi.String(prop_nr="P304", value=row['pag'])]
        else:
            page_quali = []
        wd_item.claims.add(wdwbi.Item(prop_nr="P1433", value=row['wd_container'], qualifiers=page_quali,
                                      references=inguma_references),
                           action_if_exists=wdwbi.ActionIfExists.REPLACE_ALL)  # published in ASJU

        # language
        wd_item.claims.add(wdwbi.Item(prop_nr="P407", value=row['wd_lang'], references=inguma_references),
                           action_if_exists=wdwbi.ActionIfExists.REPLACE_ALL)

        wd_item.claims.add(wdwbi.Item(prop_nr="P31", value="Q13442814", references=inguma_references),
                           action_if_exists=wdwbi.ActionIfExists.KEEP)  # scholarly article

        wd_item.claims.add(wdwbi.MonolingualText(prop_nr="P1476", language="eu", text=row['title'], references=inguma_references), action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)
        wd_item.descriptions.set("eu", f"zientzia-artikulu ({article_year})")
        wd_item.descriptions.set("en", f"scholarly article ({article_year})")
        wd_item.labels.set("en", row['title'])

        wd_item.write()
        print(f"Successfully written to http://www.wikidata.org/entity/{wd_item.id}")
        iwb.stringclaim(row['oocc_item'].replace("https://wikibase.inguma.eus/entity/",""), "P1", wd_item.id)
        time.sleep(2)



# remember to delete the P2093 "creator name" statements from Wikidata items

