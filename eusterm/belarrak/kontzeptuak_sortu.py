import sys, os, json, csv, time

sys.path.insert(1, os.path.realpath(os.path.pardir))
os.chdir(os.path.realpath(os.path.pardir))
import euswb

ez_direnak = ['osatzeke']

with open('belarrak/belarrak_literalak_entitateak.csv', 'r', encoding="utf-8") as csvfile:
    csvrows = csv.reader(csvfile)
    lit_ent = {}
    for row in csvrows:
        lit_ent[row[0]] = row[1]

with open('belarrak/klaseak_kontzeptuak.json', 'r', encoding="utf-8") as jsonfile:
    data = json.load(jsonfile)
    klaseak = data['klaseak']
    kontzeptuak = data['kontzeptuak']
    for kontzeptua in kontzeptuak:
        if kontzeptua in ez_direnak:
            continue
        print(f"{kontzeptua}: entitatea sortzear...")
        classqid = []
        for klasea in klaseak:
            if kontzeptua+'.md' in klaseak[klasea]:
                klasearen_qid = lit_ent[klasea]
                print(f"Topatu dut haren klase bat: {klasea} ({klasearen_qid})")
                classqid.append(klasearen_qid)
        item_berria = euswb.newitemwithlabel(classqid, 'eu', kontzeptua)  # Belarrak Ontologia Klase bat
        lit_ent[kontzeptua] = item_berria
        euswb.itemclaim(item_berria, 'P6', 'Q3741') # in scheme "Belarrak"
        euswb.stringclaim(item_berria, 'P42', kontzeptua)  # belarrak.eus-eko etiketa gorde
        time.sleep(1)

with open('belarrak/belarrak_literalak_entitateak.csv', 'w', encoding="utf-8") as csvfile:
    for literal in lit_ent:
        csvfile.write(literal + ',' + lit_ent[literal] + '\n')
