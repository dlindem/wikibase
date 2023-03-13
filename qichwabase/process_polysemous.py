
import csv, time, json

with open('data/qichwabase_monosemous.json', 'r', encoding="utf-8") as jsonfile:
    source = json.load(jsonfile)['results']['bindings']

with open('data/m.csv', encoding="utf-8") as csvfile: # source file
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

