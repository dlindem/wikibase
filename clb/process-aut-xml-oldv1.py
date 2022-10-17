# import lxml
from xml.etree import ElementTree as ET

import re
import os
import csv
import sys
import json
import time

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

xml_file = '/home/d3d/Downloads/aut_extract.xml'
# with open(extractxml_file, 'w') as outfile:
#     outfile.write('<collection>\n')
xmlns = "{http://www.loc.gov/MARC21/slim}"
recordcount = 0
conceptcount = 0
for event, element in ET.iterparse(xml_file, events=["start"]):
    if element.tag == "record":
        #print(ET.tostring(element, encoding="utf-8"))
        recordcount+=1
        conceptid = None
        for controlfield in element.findall("controlfield"):
            tag = controlfield.attrib['tag']
            text = controlfield.text
            #print ("Controlfield", tag, text)
            if tag == "001":
                conceptid = text
                conceptcount+=1
        if not conceptid:
            print('Error: Did not find concept ID in record '+str(recordcount))
            continue
        if conceptid.startswith('ge') or conceptid.startswith('xx'): # geolocation
            recordjson = {'cslex':None, 'enlex':None 'geoloc':None, 'udc':None, 'wikidata':None}

            if conceptid in autconcepts:
                recordjson['wikidata'] = autconcepts[conceptid]

            for datafield in element.findall("datafield"):
                tag = datafield.attrib['tag']
                ind1 = datafield.attrib['ind1']
                ind2 = datafield.attrib['ind2']

                if tag == "151":
                    if 'a' in subfields:
                        recordjson['cslex'] = subfields['a']
                if tag == "751" and ind1 == "0" and ind2 == "7":
                    if 'a' in subfields:
                        recordjson['enlex'] = subfields['a']
                if tag == "034":
                    if 'd' in subfields and 'e' in subfields:
                        recordjson['geoloc'] = (subfield['d'], subfield['e'])
                if tag == "080":
                    if 'a' in subfields:
                        recordjson['udc'] = subfields['a']

        elif conceptid.startswith('fd'): # genre
            recordjson = {'cslex':None, ''}

        elif conceptid.startswith('ph'): # concept
            recordjson = {'cslex':None, 'csaltlex':[], 'enlex':None, 'udc':None, 'narrowers':[], 'broaders':[], 'related':[]}

            for datafield in element.findall("datafield"):
                tag = datafield.attrib['tag']
                ind1 = datafield.attrib['ind1']
                ind2 = datafield.attrib['ind2']
                #print('Datafield',tag,ind1,ind2)
                subfields = get_subfields(datafield)
                if tag == "550":
                    if "w" in subfields:
                        if subfields['w'] == "h" and '7' in subfields:
                            recordjson['narrowers'].append(subfields['7'])
                        elif subfields['w'] == "g" and '7' in subfields:
                            recordjson['broaders'].append(subfields['7'])
                    if 'a' in subfields and '7' in subfields:
                        recordjson['related'].append(subfields['7'])
                if tag == "150":
                    if 'a' in subfields:
                        recordjson['cslex'] = subfields['a']
                if tag == "450":
                    if 'a' in subfields:
                        recordjson['csaltlex'].append(subfields['a'])
                if tag == "750" and ind1 == "0" and ind2 == "7":
                    if 'a' in subfields:
                        recordjson['enlex'] = subfields['a']
                if tag == "080":
                    if 'a' in subfields:
                        recordjson['udc'] = subfields['a']

                if conceptid in autconcepts:
                    recordjson['wikidata'] = autconcepts[conceptid]

        with open('data/autconcepts.jsonl', 'a', encoding="utf-8") as jsonlfile:
            jsonlfile.write(conceptid+'@'+json.dumps(recordjson)+'\n')
            #time.sleep(1)
    element.clear()

print('Finished. Processed '+str(recordcount)+' records, found '+str(conceptcount)+' concepts.')
