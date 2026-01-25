import csv, time, sys

with open('bertsolaritza/gral_wikidatara_labels_descs.csv') as file:
    rows = csv.DictReader(file, delimiter="\t")
    count = 0
    qstext = ""
    for row in rows:
        count += 1
        print(f"[{count}] Now processing row {row}")
        if row['wikidata'].startswith("Q"):
            qstext += f"{row['wikidata']}\t"
            qid = row['wikidata']
        else:
            qstext += "CREATE\nLAST\t"
            qid = "LAST"
        qstext += "P361\tQ136611356\n" # part of bertsolaritza terminology
        for lang in ["eu", "en", "es", "fr"]:
            if row[lang+"Label"] != "":
                qstext += f'{qid}\tL{lang}\t"{row[lang+"Label"]}"\n'
            if row[lang+"AltLabels"] != "":
                qstext += f'{qid}\tA{lang}\t"{row[lang + "AltLabels"]}"\n'
            if row[lang+"Def"] != "":
                qstext += f'{qid}\tD{lang}\t"{row[lang + "Def"]}"\n'
                
with open('bertsolaritza/terms_qs.csv', 'w') as outfile:
    outfile.write(qstext)








