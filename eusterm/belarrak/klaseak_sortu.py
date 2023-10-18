import sys, os, json, csv

sys.path.insert(1, os.path.realpath(os.path.pardir))
os.chdir(os.path.realpath(os.path.pardir))
import euswb

with open('belarrak/belarrak_literalak_entitateak.csv', 'r', encoding="utf-8") as csvfile:
    csvrows = csv.reader(csvfile)
    lit_ent = {}
    for row in csvrows:
        lit_ent[row[0]] = row[1]

with open('belarrak/klaseak_kontzeptuak.json', 'r', encoding="utf-8") as jsonfile:
    klaseak = json.load(jsonfile)['klaseak']
    for klasea in klaseak:
        print(f"{klasea}: entitatea sortzen...")
        classitem = euswb.newitemwithlabel(['Q3742'], 'eu', klasea)  # Belarrak Ontologia Klase bat
        lit_ent[klasea] = classitem
        euswb.itemclaim(classitem, 'P6', 'Q3741') # in scheme "Belarrak"

with open('belarrak/belarrak_literalak_entitateak.csv', 'w', encoding="utf-8") as csvfile:
    for literal in lit_ent:
        csvfile.write(literal + ',' + lit_ent[literal] + '\n')
