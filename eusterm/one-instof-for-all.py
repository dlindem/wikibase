import import_wikidata
import csv

with open('data/has-no-instanceof.csv') as csvfile:
    items = csv.DictReader(csvfile)
    for row in items:
        import_wikidata.importitem(row['wikidata'], wbqid=row['eusterm'], process_claims=['P5'], process_labels=False, process_aliases=False, process_defs=False)
