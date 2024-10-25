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
import csv, sys, wdwbi

with open ('data/inguma_egileak_wd.csv') as csvfile:
    csvrows = csv.DictReader(csvfile)
    for row in csvrows:
        print(f"\n{row}")
        if row['wd'].startswith("Q"): # creator has P1 statement
            wd_item = wdwbi.wbi.item.get(entity_id=row['wd'])
            print(wd_item.get_json())



