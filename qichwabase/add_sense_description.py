import qwbi
import csv, time

with open('done-lemma-uploads.csv', 'r', encoding="utf-8") as donefile:
    done_csv = donefile.read().split('\n')
    existing_lexemes = {}
    for item in done_csv:
        try:
            existing_lexemes[item.split('\t')[0]] = item.split('\t')[1]
        except:
            pass
    # print(str(done_items))
    print('\nThere are '+str(len(existing_lexemes))+' already uploaded lexemes.')
    time.sleep(2)

with open('done-sense-descriptions.csv', 'r', encoding="utf-8") as donefile:
    done_csv = donefile.read().split('\n')
    done_items = {}
    for item in done_csv:
        try:
            done_items[item.split('\t')[0]] = item.split('\t')[1]
        except:
            pass
    # print(str(done_items))
    print('\nThere are '+str(len(done_items))+' already uploaded sense descriptions.')
    time.sleep(2)

with open('sense-description-upload.csv', encoding="utf-8") as csvfile: # source file
    rows = csv.DictReader(csvfile, delimiter="\t")

    for row in rows:

        print('\nWill now process',str(row))
        #print(str(row))
        if ";" in row['English'] and ";" in row['Deutsch'] and ";" in row['Español']:
            print('This sense description group contains semicolon(s) in all translation fields: polysemous item, skipped in this run.')
            continue # we assume that if a semicolon appears IN ALL THREE translations, it is a polysemous quechua lexeme; this is skipped in this script!!
        id = row['id']
        if id in done_items:
            continue
        if id not in existing_lexemes:
            print('Trying to write to a lexeme that does not exist so far.')
            continue


        try:
            lexeme = qwbi.wbi.lexeme.get(entity_id=existing_lexemes[id])
        except Exception as ex:
            print('Could not get lexeme from qichwabase.')
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
        with open('done-sense-descriptions.csv', "a", encoding="utf-8") as donefile:
            donefile.write(id+'\t'+lexeme.id+'\n')
        print('Finished writing to '+lexeme.id)
        time.sleep(1)
