import time

import lxml
from xml.etree import ElementTree
import re
import os
import sys
import euswbi

tbx_file = "TBX/Musika Hiztegia_HH64.tbx"
hiztegi_item = "Q6377"
hiztegi_name = "Musika"

subjectfields = []

tree = ElementTree.parse(tbx_file)
martif = tree.getroot()
for text in martif.findall("text"):
    for body in text.findall("body"):
        for termentry in body.findall("termEntry"):

            # subjectField
            for descrip in termentry.findall("descrip"):
                if descrip.attrib['type'] == "subjectField":
                    if descrip.text not in subjectfields:
                        subjectfields.append(descrip.text)
                        print(f"Will create item for subject field: {descrip.text}")
                        wbitem = euswbi.wbi.item.new()
                        wbitem.labels.set('eu', descrip.text)
                        wbitem.claims.add(euswbi.Item(value="Q10531", prop_nr="P5")) # instance of UZEI arlo-adierazle
                        wbitem.claims.add(euswbi.Item(value=hiztegi_item, prop_nr="P17")) # iturburua: Hiztegia
                        wbitem.write()
                        print(f"Successfully created {wbitem.id}!")
                        with open('TBX/subjectfield_mapping.csv', 'a') as csvfile:
                            csvfile.write(f"{descrip.text}\t{wbitem.id}\n")
                            print(f"Stored mapping to file: {descrip.text} > {wbitem.id}")
                        time.sleep(1)