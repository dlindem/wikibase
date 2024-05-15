import os, csv

# PREFIX enwb: <https://eneoli.wikibase.cloud/entity/>
# PREFIX endp: <https://eneoli.wikibase.cloud/prop/direct/>
# PREFIX enp: <https://eneoli.wikibase.cloud/prop/>
# PREFIX enps: <https://eneoli.wikibase.cloud/prop/statement/>
# PREFIX enpq: <https://eneoli.wikibase.cloud/prop/qualifier/>
#
# select ?item_id ?parent_id ?pdf_id ?iso
#
# where {
#   ?item endp:P5 enwb:Q2; enp:P17 ?zotst. ?zotst enps:P17 ?parent_id; enpq:P20 ?pdf_id.
#   ?item endp:P7 ?lang. ?lang endp:P50 ?iso. filter(?iso="fra") # lang fr
#   ?item endp:P6 enwb:Q9. # type journal article
#   bind(strafter(str(?item),str(enwb:)) as ?item_id)
#
# } order by ?iso

with open('data/fulltext_items.csv') as file:
    rows = csv.DictReader(file)
    for row in rows:

        parent_id = row['parent_id']
        pdf_id = row['pdf_id']
        bibitem_qid = row['item_id']
        lang_iso = row['iso']
        try:
            os.system(f"cp /home/david/Zotero/storage/{pdf_id}/*.pdf /media/david/FATdisk/ENEOLI/eneoli_fulltext_{bibitem_qid}.pdf")
            print(f"Successfully copied {pdf_id}.")
        except:
            print(f"There is something wrong with {row}...")


