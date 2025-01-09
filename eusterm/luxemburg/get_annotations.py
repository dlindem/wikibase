import json
import xml.etree.ElementTree as ET

# with open('data/Luxemburgo3.txt/admin.json') as file:
#     content = json.load(file)

with open('data/Luxemburgo3.txt/admin.xmi', 'rb') as f:
    tree = ET.fromstring(f.read())
for sofa in tree.findall("{http:///uima/cas.ecore}Sofa"):
    sofastring = sofa.attrib['sofaString']






# for record in content['learning_records']:
#     if record['layer_name'] == "de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity":
#         continue #print(f"{record['text']} > {record['label']}")
#     else:
#         print(record['layer_name'])