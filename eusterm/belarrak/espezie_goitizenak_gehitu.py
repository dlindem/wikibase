import sys, os, json, csv, time, re

sys.path.insert(1, os.path.realpath(os.path.pardir))
os.chdir(os.path.realpath(os.path.pardir))
import euswbi

with open('belarrak/belarrak_literalak_entitateak.csv', 'r', encoding="utf-8") as csvfile:
    csvrows = csv.reader(csvfile)
    lit_ent = {}
    for row in csvrows:
        lit_ent[row[0]] = row[1]

langs = ['eu', 'en', 'es']
result = {}
fitxategiak = os.listdir('belarrak/pages')
for mdfile in fitxategiak:
    if not mdfile.endswith('.md'):
        continue
    # print(f"Orain prozesatzen: {mdfile}")
    with (open('belarrak/pages/' + mdfile, 'r', encoding="utf-8") as file):
        content = file.read()
        landarea = mdfile.replace('.md', '')
        lresult = {}
        for lang in langs:
            regex = re.search(rf"> \*\*({lang})\.\*\*(.[^\n]+)", content)
            if regex:
                lang = regex.group(1)
                names = re.sub(r'[:_\*]','', regex.group(2)).strip().split(',')

                print(f"{landarea}: {lang}: {names}")
                lresult[lang] = names
        if len(lresult) > 0:
            result[lit_ent[landarea]] = lresult


with open('belarrak/espezie_izenak.json', 'w', encoding="utf-8") as jsonfile:
    json.dump(result, jsonfile, indent=2)

for qid in result:
    labels = []
    aliases = []
    print(f"Orain prozesatzen: {str(result[qid])}")
    if 'eu' in result[qid]:
        for label in result[qid]['eu']:
            aliases.append({'lang':'eu', 'value':label.strip()})
    if 'es' in result[qid]:
        labels.append({'lang': 'es', 'value': result[qid]['es'].pop(0).strip()})
        for label in result[qid]['es']:
            aliases.append({'lang': 'es', 'value': label.strip()})
    if 'en' in result[qid]:
        labels.append({'lang': 'en', 'value': result[qid]['en'].pop(0).strip()})
        for label in result[qid]['en']:
            aliases.append({'lang': 'en', 'value': label.strip()})



    euswbi.itemwrite({'qid':qid, 'labels':labels, 'aliases':aliases, 'statements': []})
