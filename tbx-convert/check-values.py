import time, json, re, sys, os
from xml.etree import ElementTree
from mappings import *

found_values = {}
def save_value(sec=None, entry=None, tbx_prop=None):
    global found_values
    if not entry.text:
        return
    if entry.text.strip() == '':
        return
    value = entry.text.strip()
    fieldname = f"{sec}/{tbx_prop}"
    print(f"Found field '{fieldname}' with value '{value}'")
    if fieldname not in found_values:
        found_values[fieldname] = {value: 1}
    elif entry.text.strip() not in found_values[fieldname]:
        found_values[fieldname][value] = 1
    else:
        found_values[fieldname][value] += 1

tbx_filename = "FAIRterm20_export-6"
tbx_path = f"source_data/{tbx_filename}.tbx"
dataset_item = "" # the item that describes the source dataset
hiztegi_name = "" # the name of the source dataset

tree = ElementTree.parse(tbx_path)
tbx_tree = tree.getroot()
for text in tbx_tree.findall("text"):
    for body in text.findall("body"):
        entrycount = 0
        for concept_entry in body.findall("conceptEntry"):
            entrycount += 1
            print(f"[{entrycount}] Now looking at entry {concept_entry.attrib['id']}")
            # if entrycount > 2:
            #     break
            for tbx_prop in properties['conceptEntry']:
                # print(f"Checking for {tbx_prop}...")
                for entry in concept_entry.findall(tbx_prop, namespaces):
                    save_value(sec="conceptEntry", entry=entry, tbx_prop=tbx_prop)
            for lang_sec in concept_entry.findall("langSec"):
                lang_sec_lang = lang_sec.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                print(f"Found Language Section for language {lang_sec_lang}")
                for desc_grp in lang_sec.findall('descripGrp'):
                    for tbx_prop in properties['descripGrp']:
                        # print(f"Checking for {tbx_prop}...")
                        for entry in desc_grp.findall(tbx_prop, namespaces):
                            save_value(sec="descripGrp", entry=entry, tbx_prop=tbx_prop)
                for term_sec in lang_sec.findall("termSec"):
                    for tbx_prop in properties['termSec']:
                        # print(f"Checking for {tbx_prop}...")
                        for entry in term_sec.findall(tbx_prop, namespaces):
                            save_value(sec="termSec", entry=entry, tbx_prop=tbx_prop)




with open(f'logs/{tbx_filename}_values.json', 'w') as outfile:
    json.dump(found_values, outfile, indent=2)