import json, csv, re

with open('data/indice_de_conceptos_vasco_manually_corrected_wikilinks.txt') as file:
    entries = file.read().split('\n')

with open('data/oocc_index.json') as file:
    index = json.load(file)

result = {"Euskera / Vasco": []}
letter = "Euskera / Vasco"
for entry in entries:
    print(entry)
    if entry.startswith("@"):
        letter = entry[1]
        result[letter] = []
        continue
    entrysplit = entry.split('@')
    entity = entrysplit.pop(0)
    level_re = re.search(r'^#+', entity)
    level_stars = level_re.group(0)
    level = len(level_stars)
    entity = re.sub(rf'{level_stars}', '', entity)

    if len(entrysplit) > 0:
        entryresult = {}
        for refblock in entrysplit:
            refsplit = re.findall(r'\d+', refblock)
            bolumen = re.search(r'^[IXV]+', refblock).group(0)
            for ref in refsplit:

                for bibitem in index[bolumen]:

                    try:
                        if bibitem['startp'] <= int(ref) and bibitem['endp'] >= int(ref):
                            print(f"Found {bibitem['item']}")
                            if bibitem['item'] not in entryresult:
                                entryresult[bibitem['item']] = {"vol": bolumen, "pp": [ref]}
                            elif ref not in entryresult[bibitem['item']]['pp']:
                                entryresult[bibitem['item']]['pp'].append(ref)
                    except:
                        pass
        result[letter].append({'concept': entity, 'level':level, 'data': entryresult})
    elif "[" in entity:
        result[letter].append({'redirect': entity})
    else:
        result[letter].append({'concept': entity, 'level':level})

with open('data/oocc_concept_index_vasco_map.json', 'w') as file:
    json.dump(result, file, indent=2)