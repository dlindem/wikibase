# PREFIX iwb: <https://wikibase.inguma.eus/entity/>
# PREFIX idp: <https://wikibase.inguma.eus/prop/direct/>
# PREFIX ip: <https://wikibase.inguma.eus/prop/>
# PREFIX ips: <https://wikibase.inguma.eus/prop/statement/>
# PREFIX ipq: <https://wikibase.inguma.eus/prop/qualifier/>
#
# select distinct ?artikulua ?wd ?wd_upload ?statement (strafter(str(?ref),"http://www.wikidata.org/reference/") as ?reference)
# where {
#
#
#   ?artikulua idp:P37 iwb:Q13091.# ; idp:P59 iwb:Q13367.
#
#
#   ?artikulua idp:P1 ?wd. bind(iri(concat(str(wd:),?wd)) as ?wikidata_item)
#
#            SERVICE <https://query.wikidata.org/sparql> {
#            select ?wikidata_item ?statement ?wd_upload ?ref where {?wikidata_item ?prop ?statement. ?statement ps:P31 wd:Q13442814; prov:wasDerivedFrom ?ref. ?ref pr:P248 wd:Q12259621; pr:P813 ?wd_upload.
#            filter(regex(str(?wd_upload), "2024-11-02"))}
#           }
# }
# group by ?artikulua ?wd ?wd_upload ?statement ?ref

import csv, wdi, time

with open('data/refs_to_remove.csv') as csvfile:
    csvrows = csv.DictReader(csvfile, delimiter="\t")
    for row in csvrows:
        wdi.removeref(reference=row['reference'], guid=row['statement'].replace("http://www.wikidata.org/entity/statement/",""))
        time.sleep(0.5)
