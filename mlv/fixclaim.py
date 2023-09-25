import csv, time, xwb

with open('data/fix.csv', 'r', encoding='utf-8') as file:
    rows = csv.DictReader(file)
    for row in rows:
        if xwb.setqualifier(row['lexeme'], "P6", row['statement'], "P154", row['lemma'], 'string'):
            print('Success for '+row['lexeme'])
        else:
            print('Failed for '+row['lexeme'])
        time.sleep(0.3)