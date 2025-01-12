import json, re
import xml.etree.ElementTree as ET

# with open('data/Luxemburgo3.txt/admin.json') as file:
#     content = json.load(file)

result = {'wikidata': {}, 'itzulpenak': {}}
docs = """Luxemburgo_introducción.txt
Luxemburgo1.txt
Luxemburgo2.txt
Luxemburgo3.txt
Luxemburgo4.txt
Luxemburgo5.txt
Luxemburgo6.txt
Luxemburgo7.txt
Luxemburgo8.txt
Luxemburgo9.txt
Luxemburgo10.txt""".split("\n")


for filename in docs:


    with open(f'data/{filename}/admin.xmi', 'rb') as f:
        tree = ET.fromstring(f.read())
    for element in tree:
        print(element)
    for sofa in tree.findall("{http:///uima/cas.ecore}Sofa"):
        sofastring = sofa.attrib['sofaString']
        # print(sofastring)

    for ne in tree.findall("{http:///de/tudarmstadt/ukp/dkpro/core/api/ner/type.ecore}NamedEntity"):
        if "identifier" in ne.attrib:
            wikidata = ne.attrib['identifier']
            begin = int(ne.attrib['begin'])
            end = int(ne.attrib['end'])
            letter = True
            while letter:
                if re.search(r"[a-zA-z\-]", sofastring[end]):
                    end += 1
                else:
                    letter = False
            word = sofastring[begin:end]
            print(f"Found NE: {wikidata} <> {word}")
            if wikidata not in result['wikidata']:
                result['wikidata'][wikidata] = {word: 1}
            elif word not in result['wikidata'][wikidata]:
                result['wikidata'][wikidata][word] = 1
            else:
                result['wikidata'][wikidata][word] += 1
    for itz in tree.findall("{http:///custom.ecore}Span"):
        itzulp = itz.attrib['iztulpenordaina']
        begin = int(itz.attrib['begin'])
        end = int(itz.attrib['end'])
        letter = True
        while letter:
            if re.search(r"[a-zA-z\-]", sofastring[end]):
                end += 1
            else:
                letter = False
        word = sofastring[begin:end]
        print(f"Found itzulpena: {itzulp} <> {word}")
        if itzulp not in result['itzulpenak']:
            result['itzulpenak'][itzulp] = {word: 1}
        elif word not in result['itzulpenak'][itzulp]:
            result['itzulpenak'][itzulp][word] = 1
        else:
            result['itzulpenak'][itzulp][word] += 1
        
        
        

with open('data/annotations.json', 'w') as jsonfile:
    json.dump(result, jsonfile, indent=2)



# for record in content['learning_records']:
#     if record['layer_name'] == "de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity":
#         continue #print(f"{record['text']} > {record['label']}")
#     else:
#         print(record['layer_name'])