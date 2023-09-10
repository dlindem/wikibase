
import csv, time, json, re

with open('data/qichwabase_sparql_lexemes.csv', 'r', encoding="utf-8") as donefile:
    done_csv = csv.DictReader(donefile)
    done_items = {}
    for item in done_csv:
        done_items[item['interimid']] = item['entry']
    print('\nThere are '+str(len(done_items))+' lexemes existing on qichwabase.')
    time.sleep(2)

with open('data/monosemous_worksheet.csv', 'r', encoding="utf-8") as donefile:
    done_csv = csv.DictReader(donefile, delimiter="\t")
    monosemous_items = []
    for item in done_csv:
        monosemous_items.append(re.search('http[^\-]+',item['sense_uri']).group(0))
    print('\nThere are '+str(len(monosemous_items))+' monosemous items (to be skipped by this script) existing on qichwabase.')
    time.sleep(2)

done_descs = {}
with open('data/MASTER_french_italian_upload.csv', encoding="utf-8") as csvfile: # source file
    rows = csv.DictReader(csvfile, delimiter="\t")

    for row in rows:

        id = row['ID']
        if id not in done_items:
            print('Skipping lexeme not found on qichwabase:',id)
            continue
        if id in done_descs:
            print('Skipping previously processed item', id)
            continue

        if id in monosemous_items:
            print('Trying to write to a lexeme that is not polysemous. Skipped:',id)
            continue

        print('\nWill now process polysemous item', str(row))
        input()
        uri = done_items[id]
        try:
            lexeme = qwbi.wbi.lexeme.get(entity_id=uri)
        except Exception as ex:
            input('Could not get lexeme from qichwabase. Press any key to skip.')
            continue



        sense = qwbi.Sense()
        if row['English'] and len(row['English'].strip()) > 0:
            sense.glosses.set(language='en', value=row['English'].strip())
        if row['Deutsch'] and len(row['Deutsch'].strip()) > 0:
            sense.glosses.set(language='de', value=row['Deutsch'].strip())
        if row['Español'] and len(row['Español'].strip()) > 0:
            sense.glosses.set(language='es', value=row['Español'].strip())

        lexeme.senses.add(sense)

        lexeme.write()
        with open('data/done-sense-descriptions.csv', "a", encoding="utf-8") as donefile:
            donefile.write(id + '\t' + lexeme.id + '\n')
        print('Finished writing to ' + lexeme.id)
        time.sleep(1)