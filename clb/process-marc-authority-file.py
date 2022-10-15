# import lxml
from xml.etree import ElementTree as ET

import re
import os
import csv
import sys
import json
import time
from data.marcmapping import mapping as marcmapping

def get_subfields(datafield):
    fields = {}
    for field in datafield.findall("subfield"):
        fields[field.attrib['code']] = field.text
    #print(str(fields))
    return fields

with open('data/autconcepts_wikidata.csv', 'r') as csvfile:
    autconceptsmapping = csv.DictReader(csvfile)
    autconcepts = {}
    for row in autconceptsmapping:
        autconcepts[row['nkcr']] = row['wd']

xml_file = '/home/d3d/Downloads/aut.xml'
# xml_file = 'data/aut_xmpl.xml'
# with open(extractxml_file, 'w') as outfile:
#     outfile.write('<collection>\n')
xmlns = "{http://www.loc.gov/MARC21/slim}"
recordcount = 0
conceptcount = 0
allowed_recordtypes = {'ph', 'fd', 'ge', 'xx'}
for event, element in ET.iterparse(xml_file, events=["start"]):
    if element.tag == xmlns+"record":
        #print(ET.tostring(element, encoding="utf-8"))
        recordcount+=1
        conceptid = None
        for controlfield in element.findall(xmlns+"controlfield"):
            tag = controlfield.attrib['tag']
            text = controlfield.text
            #print ("Controlfield", tag, text)
            if tag == "001":
                conceptid = text
                if not text:
                    print('Error: MARC record without controlfield 001 text value.')
                    #print(ET.tostring(element).decode("utf-8"))
                    #time.sleep(1)
                    break

                recordtype = re.search(r'^[a-z]+',conceptid).group(0)
                if recordtype not in allowed_recordtypes:
                    conceptid = None

        if conceptid:
            conceptcount+=1
            print(conceptid)
            recordjson = {}
        else:
            continue

        if conceptid in autconcepts:
            recordjson['wikidata'] = autconcepts[conceptid]

        for datafield in element.findall(xmlns+"datafield"):
            tag = datafield.attrib['tag']
            ind1 = datafield.attrib['ind1']
            ind2 = datafield.attrib['ind2']
            #print('Datafield',tag,ind1,ind2)
            subfields = get_subfields(datafield)
            if tag in marcmapping:
                #print('Will try to process '+tag)
                for action in marcmapping[tag]:
                    if action['value']['sub'] not in subfields:
                        #print('Failed to locate value for '+action['target']+' from datafield '+tag)
                        continue
                    if action['value']['ind1'] != ind1:
                        #print('Found non-matching ind1, skip this '+tag)
                        continue
                    if action['value']['ind2'] != ind2:
                        #print('Found non-matching ind2, skip this '+tag)
                        continue
                    if 'condition' in action:
                        if 'sub' in action['condition'] and action['condition']['sub'] in subfields:
                            if subfields[action['condition']['sub']] != action['condition']['value']:
                                continue
                        if 'nosub' in action['condition']:
                            if action['condition']['nosub'] in subfields:
                                continue
                    if action['target'] not in recordjson:
                        recordjson[action['target']] = [subfields[action['value']['sub']]]
                    else:
                        recordjson[action['target']].append(subfields[action['value']['sub']])
        if len(recordjson) == 0:
            continue
        with open('data/autconcepts.jsonl', 'a', encoding="utf-8") as jsonlfile:
            jsonlfile.write(conceptid+'@'+json.dumps(recordjson)+'\n')
            #time.sleep(1)
    element.clear()

print('Finished. Processed '+str(recordcount)+' records, found '+str(conceptcount)+' concepts.')
print('Found recordtypes: '+str(recordtypes))
