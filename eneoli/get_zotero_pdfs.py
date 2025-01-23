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

import requests

print("Getting data from Wikibase...")
r = requests.get("https://eneoli.wikibase.cloud/query/sparql?format=json&query=PREFIX%20enwb%3A%20%3Chttps%3A%2F%2Feneoli.wikibase.cloud%2Fentity%2F%3E%0APREFIX%20endp%3A%20%3Chttps%3A%2F%2Feneoli.wikibase.cloud%2Fprop%2Fdirect%2F%3E%0APREFIX%20enp%3A%20%3Chttps%3A%2F%2Feneoli.wikibase.cloud%2Fprop%2F%3E%0APREFIX%20enps%3A%20%3Chttps%3A%2F%2Feneoli.wikibase.cloud%2Fprop%2Fstatement%2F%3E%0APREFIX%20enpq%3A%20%3Chttps%3A%2F%2Feneoli.wikibase.cloud%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20%3Fitem_id%20%3Fparent_id%20%3Fpdf_id%20%3Fiso%20(sample(%3Fdesc)%20as%20%3Fdescription)%0A%0Awhere%20%7B%0A%20%20%3Fitem%20endp%3AP5%20enwb%3AQ2%3B%20enp%3AP17%20%3Fzotst.%20%3Fzotst%20enps%3AP17%20%3Fparent_id%3B%20enpq%3AP20%20%3Fpdf_id.%0A%20%20%3Fitem%20endp%3AP7%20%3Flang.%20%3Flang%20endp%3AP50%20%3Fiso.%20%23%20filter(%3Fiso%3D%22fra%22)%20%23%20lang%20fr%0A%20%20%23%20%3Fitem%20endp%3AP6%20enwb%3AQ9.%20%23%20type%20journal%20article%0A%20%20%3Fitem%20schema%3Adescription%20%3Fdesc.%0A%20%20bind(strafter(str(%3Fitem)%2Cstr(enwb%3A))%20as%20%3Fitem_id)%0A%0A%7D%20group%20by%20%3Fitem_id%20%3Fparent_id%20%3Fpdf_id%20%3Fiso%20%3Fdescription%20order%20by%20%3Fiso")
fulltext_items = r.json()['results']['bindings']

# with open('data/fulltext_items.csv') as file:
#     rows = csv.DictReader(file, delimiter=",")

for row in fulltext_items:
    parent_id = row['parent_id']['value']
    pdf_id = row['pdf_id']['value']
    bibitem_qid = row['item_id']['value']
    lang_iso = row['iso']['value']
    try:
        source = f"/home/david/Zotero/storage/{pdf_id}"
        if not os.path.exists(source):
            zotitem = pyzot.item(parent_id)
            zotitem = pyzot.add_tags(zotitem, 'wikibase-export')
            print(f"Tagged item {parent_id} with 'wikibase-export', there seems to be an orphaned PDF ID qualifier in the zotitem ID statement.")
        else:
            target = f"/media/david/FATdisk/ENEOLI/eneoli_fulltext_{bibitem_qid}.pdf"
            if os.path.exists(target):
                print(f"Item {pdf_id} is already in target folder.")
            else:
                os.system(f"cp {source}/*.pdf {target}")
                print(f"Successfully copied {pdf_id}.")
    except:
        print(f"There is something wrong with {row}...")


