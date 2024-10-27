# https://wikibase.inguma.eus/wiki/KM_Wikidata_export#Export_citations_%28for_citation-to-wikidata.py%29

import getcitations
citations = getcitations.get_citations()
amount = len(citations)
import csv, re, sys, time, json, wdwbi
wdns = "http://www.wikidata.org/entity/"
count = 0
for iturri in citations:
    count += 1
    print(f"[{count}/{amount}] {wdns}{iturri}: {len(citations[iturri]['xedeak'])} citations to write.")
    inguma_references = wdwbi.References()
    inguma_reference = wdwbi.Reference()
    inguma_reference.add(wdwbi.Item(prop_nr="P248", value="Q12259621"))  # stated in: Inguma
    inguma_reference.add(
        wdwbi.URL(prop_nr="P854", value=citations[iturri]['wb_iturri']))  # Inguma entity URI on Inguma Wikibase
    inguma_reference.add(wdwbi.Time(prop_nr="P813", time="now"))
    inguma_references.add(inguma_reference)

    wd_item = wdwbi.wbi.item.get(entity_id=iturri)
    for xede in citations[iturri]['xedeak']:
        wd_item.claims.add(wdwbi.Item(prop_nr="P2860", value=xede,
                                  references=inguma_references),
                       action_if_exists=wdwbi.ActionIfExists.MERGE_REFS_OR_APPEND)  # add citation

    wd_item.write()
    print(f"Successfully written to http://www.wikidata.org/entity/{wd_item.id}")
    time.sleep(1)



# remember to delete the P2093 "creator name" statements from Wikidata items

