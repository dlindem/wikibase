import csv, time, re, json, nlp, config_private
from pyzotero import zotero
pyzot = zotero.Zotero(config_private.zotero_group_nr, 'group', config_private.zotero_api_key)

with open('data/OOCC_zotero_ziterauzi.csv','r', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile, delimiter="\t")
    for row in reader:
        print(row)
        with open(row['TXT'], 'r', encoding="utf-8-sig") as txtfile:
            text = txtfile.read()
            text = re.sub(r'\n+', '\n', text) # removes double eol
            text = re.sub(r'[]\ufeff', '', text) # strange characters from PDF
            text = re.sub(r'\n[^a-z]+\n', '\n', text) # remove running titles, page numbers, section headings
            print(text)
            if row['Language'] == "es":
                processed_text = nlp.lemmatize_clean(text, lang="spa")
                print(processed_text)
                print(len(processed_text["tokenized"]))
                print(len(processed_text["lemmatized"]))
                jsonfilepath = row['TXT'].replace(".zotero-ft-cache", "processed.json")
                with open(jsonfilepath, "w", encoding="utf-8") as outfile:
                    json.dump(processed_text, outfile, indent=2, ensure_ascii=False)
                pyzot.attachment_simple([jsonfilepath], parentid=row['zotid'])
                print(f"Success attaching {jsonfilepath} to Zotero {row['zotid']}...")
                time.sleep(1)





