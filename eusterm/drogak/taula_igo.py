import sys, os, time, csv, re

sys.path.insert(1, os.path.realpath(os.path.pardir))
os.chdir(os.path.realpath(os.path.pardir))
import euswbi

lexlangprops = {'eu': 'P8', 'es':'P93', 'en': 'P94'}
desclangprops = {'eu': 'P13', 'es':'P95', 'en': 'P96'}
schemeqid = 'Q6285'

with open('drogak/Drogak_Wikidata.csv', 'r', encoding="utf-8") as csvfile:
    csvrows = csv.DictReader(csvfile)

    for row in csvrows:

        label = row['label'].strip()
        if "(" not in label:
            label = label.lower()
        label_lang = row['label_lang'].strip()
        if row['wikidata'].strip().startswith("Q"):
            wdqid = row['wikidata'].strip()
        else:
            wdqid = None
        source_url = row['source_url'].strip()
        desc = row['def'].strip()
        desc = re.sub(r'\.$', '', desc)
        desc_lang = row['def_lang'].strip()

        labels = [{'lang': label_lang, 'value': label}]
        descriptions = [{'lang': desc_lang, 'value': desc}]
        statements = [{'prop_nr': 'P6', 'type': 'item', 'value':schemeqid},
                      {'prop_nr': lexlangprops[label_lang], 'type': 'string', 'value': label,
                       'references': [{'prop_nr': 'P9', 'type': 'url', 'value':source_url}]},
                      {'prop_nr': desclangprops[label_lang], 'type': 'string', 'value': desc,
                       'references': [{'prop_nr': 'P14', 'type': 'url', 'value': source_url}]}]

        if wdqid:
            statements.append({'prop_nr': 'P1', 'type': 'externalid', 'value': wdqid})

        wbqid = euswbi.itemwrite({'qid': False, 'statements': statements, 'labels': labels, 'descriptions': descriptions})
        time.sleep(1)

