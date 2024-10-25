import os, csv
import config_private
from pyzotero import zotero
pyzot = zotero.Zotero(config_private.zotero_group_nr, 'group', config_private.zotero_api_key)

# PREFIX enwb: <https://eneoli.wikibase.cloud/entity/>
# PREFIX endp: <https://eneoli.wikibase.cloud/prop/direct/>
# PREFIX enp: <https://eneoli.wikibase.cloud/prop/>
# PREFIX enps: <https://eneoli.wikibase.cloud/prop/statement/>
# PREFIX enpq: <https://eneoli.wikibase.cloud/prop/qualifier/>
#
# select ?item_id ?parent_id ?pdf_id ?iso (sample(?desc) as ?description)
#
# where {
#   ?item endp:P5 enwb:Q2; enp:P17 ?zotst. ?zotst enps:P17 ?parent_id; enpq:P20 ?pdf_id.
#   ?item endp:P7 ?lang. ?lang endp:P50 ?iso. filter(?iso="fra") # lang fr
#   # ?item endp:P6 enwb:Q9. # type journal article
#   ?item schema:description ?desc.
#   bind(strafter(str(?item),str(enwb:)) as ?item_id)
#
# } group by ?item_id ?parent_id ?pdf_id ?iso ?description order by ?iso

with open('data/fulltext_items.csv') as file:
    rows = csv.DictReader(file, delimiter="\t")
    for row in rows:

        parent_id = row['parent_id']
        pdf_id = row['pdf_id']
        bibitem_qid = row['item_id']
        lang_iso = row['iso']
        try:
            source = f"/home/david/Zotero/storage/{pdf_id}"
            if not os.path.exists(source):
                zotitem = pyzot.item(parent_id)
                zotitem = pyzot.add_tags(zotitem, 'wikibase-export')
                print(f"Tagged item {parent_id} with 'wikibase-export', there seems to be an orphaned PDF ID qualifier in the zotitem ID statement.")
            else:
                os.system(f"cp {source}/*.pdf /media/david/FATdisk/ENEOLI/eneoli_fulltext_{bibitem_qid}.pdf")
                print(f"Successfully copied {pdf_id}.")
        except:
            print(f"There is something wrong with {row}...")


