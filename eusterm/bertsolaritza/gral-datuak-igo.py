import sys, os, time, csv, re

sys.path.insert(1, os.path.realpath(os.path.pardir))
os.chdir(os.path.realpath(os.path.pardir))
import euswbi

lexlangprops = {'eu':'P8','es':'P93', 'en': 'P94', 'fr': 'P109'}
desclangprops = {'eu': 'P13', 'es':'P95', 'en': 'P96', 'fr':'P173'}
schemeqid = 'Q8144'

with open('bertsolaritza/gral_datuak.csv', 'r', encoding="utf-8") as csvfile:
    csvrows = csv.DictReader(csvfile, delimiter=",")

    for row in csvrows:
        statements = []
        wbqid = row['eusterm']
        print(f'\nNow processing {wbqid}')

        if row['wikidata'].startswith('Q'):
            wdqid = row['wikidata'].strip()
            statements.append({'prop_nr': 'P1', 'type': 'externalid', 'value': wdqid})
            print('Found Wikidata Qid')

        statements.append({'prop_nr': 'P6', 'type': 'item', 'value': schemeqid})
        statements.append({'prop_nr': 'P110', 'type': 'item', 'value': row['pos']})

        labels = []
        aliases = []
        descriptions = []

        for lang in ['eu','es','en','fr']:

            labels.append({'lang': lang, 'value': row[f'L{lang}'].strip()})
            jatorria = row[f'J{lang}']
            statements.append({'prop_nr': lexlangprops[lang], 'type':'string', 'value':row[f'L{lang}'].strip(), 'qualifiers':
                               [{'prop_nr': 'P17', 'type':'item', 'value':jatorria}]})
            print(f'Found label for {lang} with source {jatorria}')

            descriptions.append({'lang': lang, 'value': row[f'D{lang}'].strip().replace("\n"," ")})
            jatorria = row[f'J{lang}']
            statements.append({'prop_nr': desclangprops[lang], 'type': 'string', 'value': row[f'D{lang}'].strip().replace("\n"," "), 'qualifiers':
                               [{'prop_nr': 'P17', 'type':'item', 'value':jatorria}]})
            print(f'Found description for {lang} with source {jatorria}')

            if f'A{lang}' in row:
                if len(row[f'A{lang}']) > 1:
                    for alias in row[f'A{lang}'].split("|"):
                        print(f'Found alias for {lang}')
                        aliases.append({'lang':lang,'value':alias.strip()})
                        statements.append({'prop_nr': 'P8', 'type': 'string', 'value': alias})


        wbqid = euswbi.itemwrite(
            {'qid': wbqid, 'statements': statements, 'labels': labels, 'aliases': aliases, 'descriptions': descriptions}, clear=True)
        time.sleep(1)