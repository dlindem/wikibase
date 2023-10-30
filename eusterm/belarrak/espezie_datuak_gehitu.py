import sys, os, json, csv, time, re

sys.path.insert(1, os.path.realpath(os.path.pardir))
os.chdir(os.path.realpath(os.path.pardir))
import euswbi

with open('belarrak/belarrak_literalak_entitateak.csv', 'r', encoding="utf-8") as csvfile:
    csvrows = csv.reader(csvfile)
    lit_ent = {}
    for row in csvrows:
        lit_ent[row[0]] = row[1]

obj_props = {
    "Ordena": "P46",
    "Familia": "P47",
    "Generoa": "P48",
}
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
        good_result = False
        for obj_prop in obj_props:
            regex = re.search(rf"\+ \*\*{obj_prop}\*\*[^\[]*\[\[([^\]]+)\]\]", content)
            if regex:
                good_result = True
                print(f"{landarea}: {obj_prop}: {regex.group(1)}")
                lresult[obj_prop] = {'prop_nr': obj_props[obj_prop], 'literal': regex.group(1),
                                     'object': lit_ent[regex.group(1)]}
        regex = re.search(rf"\+ \*\*Espeziea\*\*([^\n]*)\n", content)
        if regex:
            good_result = True
            literal = re.sub(r':? *_ *', '', regex.group(1))
            if len(literal) > 0:
                print(f"{landarea}: Espeziea: {literal}")
                lresult['Espeziea'] = {'prop_nr': "P49", 'literal': literal}
        if good_result:
            lresult['subject'] = lit_ent[landarea]
            result[landarea] = lresult

with open('belarrak/espezie_datuak.json', 'w', encoding="utf-8") as jsonfile:
    json.dump(result, jsonfile, indent=2)

for entry in result:
    print(f"Orain prozesatzen: {str(result[entry])}")
    statements = [{'type':'item', 'prop_nr':'P5', 'value': 'Q3746'}] # instance of landare
    for relation in result[entry]:
        print(relation)
        if relation in ['Ordena', 'Familia', 'Generoa']:
            statements.append({'type':'item', 'prop_nr':result[entry][relation]['prop_nr'], 'value': result[entry][relation]['object']})
        elif relation == "Espeziea":
            statements.append({'type': 'string', 'prop_nr': result[entry][relation]['prop_nr'],
                               'value': result[entry][relation]['literal']})
    euswbi.itemwrite({'qid':result[entry]['subject'], 'statements':statements})
