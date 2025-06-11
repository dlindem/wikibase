import xwbi, csv, re, time


with open('data/lexonomy_data/datasheet.csv') as file:
    rows = csv.DictReader(file, delimiter="\t")

    for row in rows:
        time.sleep(1)
        # print(f"\nNow processing row: {row}")

        new_lexeme = xwbi.wbi.lexeme.new(language=row['lang'], lexical_category=row['POS'])
        new_lexeme.lemmas.set(language=row['langcode'], value=row['lemma'].strip())
        new_lexeme.write()
        print(f"{new_lexeme.id},{row['lemma']}\n")