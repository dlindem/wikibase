import qwbi
import csv, time

with open('data/done-sense-descriptions.csv', 'r', encoding="utf-8") as donefile:
    done_csv = donefile.read().split('\n')
    done_items = {}
    for item in done_csv:
        try:
            done_items[item.split('\t')[0]] = item.split('\t')[1]
        except:
            pass
    # print(str(done_items))
    print('\nThere are '+str(len(done_items))+' existing sense descriptions.')
    time.sleep(2)

with open('data/MASTER_french_italian_upload.csv', encoding="utf-8") as csvfile: # source file
    rows = csv.DictReader(csvfile, delimiter="\t")

    for row in rows:
        id = row['ID']



        if id not in done_items:
            print('Trying to write to a lexeme that is not polysemous. Skipped.\n')
            continue

        print('\nWill now process polysemous item', str(row))
        # print(str(row))

        try:
            lexeme = qwbi.wbi.lexeme.get(entity_id=done_items[id])
        except Exception as ex:
            input('Could not get lexeme from qichwabase. Press any key to skip.')
            continue

