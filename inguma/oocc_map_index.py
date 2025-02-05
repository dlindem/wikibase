import json, csv, re

with open('data/Indice_de_nombres.txt') as file:
    entries = file.read().split('\n')

with open('data/oocc_index.json') as file:
    index = json.load(file)

result = []
for entry in entries:
    print(entry)
    entrysplit = entry.split('|')
    entity = entrysplit.pop(0)
    # print(entity)
    if len(entrysplit) > 0:
        entryresult = {}
        for refblock in entrysplit:
            refsplit = refblock.strip().split(' ')
            bolumen = refsplit.pop(0)
            for ref in refsplit:

                for bibitem in index[bolumen]:
                    newbibitem = True
                    try:
                        pure_ref = int(re.sub(r'[@\-].*', '', ref))
                        if newbibitem:
                            write_ref = bolumen + ": " + ref.replace("@", " ")
                            newbibitem = False
                        else:
                            write_ref = ref.replace("@", " ")
                        if bibitem['startp'] <= pure_ref and bibitem['endp'] >= pure_ref:
                            print(f"Found {bibitem['item']}")
                            if bibitem['item'] not in entryresult:
                                entryresult[bibitem['item']] = [write_ref]
                            elif write_ref not in entryresult[bibitem['item']]:
                                entryresult[bibitem['item']].append(write_ref)
                    except:
                        pass
        result.append({'entity': entity, 'data': entryresult})

with open('data/oocc_index_map.json', 'w') as file:
    json.dump(result, file, indent=2)