import lxml
from xml.etree import ElementTree
import re
import os
import sys
import euswbi
import time

tbx_file = "TBX/Musika Hiztegia_HH64.tbx"
hiztegi_item = "Q6377"
hiztegi_name = "Musika"
kontzeptu_eskema = "Q17413"

subjectfields = {}
with open('TBX/subjectfield_mapping.csv', 'r') as csvfile:
    mappings = csvfile.read().split("\n")
    for mapping in mappings:
        if "\t" in mapping:
            map = mapping.split("\t")
            subjectfields[map[0]] = map[1]
    print(f"{len(subjectfields)} subject fields loaded: {subjectfields}")

tree = ElementTree.parse(tbx_file)
martif = tree.getroot()
for text in martif.findall("text"):
    for body in text.findall("body"):
        count = 0
        for termentry in body.findall("termEntry"):
            count += 1
            term_id = termentry.attrib['id']
            wbitem = euswbi.wbi.item.new()
            wbitem.claims.add(euswbi.Item(value=hiztegi_item, prop_nr="P17"))
            wbitem.claims.add(euswbi.Item(value=kontzeptu_eskema, prop_nr="P6"))
            wbitem.claims.add(euswbi.String(value=f"{hiztegi_name}_{term_id}", prop_nr="P15"))
            setlabellangs = []

            # subjectField
            for descrip in termentry.findall("descrip"):
                if descrip.attrib['type'] == "subjectField":
                    if descrip.text not in subjectfields:
                        print(f"Error: Found unknown subject field: {descrip.text}")
                        sys.exit()
                    wbitem.claims.add(euswbi.Item(value=subjectfields[descrip.text], prop_nr="P166"))

            # terms
            for langset in termentry.findall("langSet"):
                lang = langset.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                for descripgrp in langset.findall("descripGrp"):
                    for descrip in descripgrp.findall("descrip"):
                        if descrip.attrib['type'] == "definition":
                            wbitem.descriptions.set(lang, descrip.text)
                            references = [euswbi.Item(value=hiztegi_item, prop_nr="P17")]
                            wbitem.claims.add(euswbi.String(value=descrip.text, prop_nr="P8", references=references))

                for tig in langset.findall("tig"):
                    qualifiers = []
                    for termnote in tig.findall("termNote"):
                        if termnote.attrib['type'] == "normativeAuthorization":
                            qualifiers = [euswbi.String(value=termnote.text, prop_nr="P18")]
                    for term in tig.findall("term"):
                        if lang not in setlabellangs:
                            wbitem.labels.set(lang, term.text)
                            setlabellangs.append(lang)
                        else:
                            wbitem.aliases.set(lang, term.text)
                        if lang != "eu":
                            continue # P8 statement for Basque (other langs only labels/aliases/descs)
                        references = [euswbi.Item(value=hiztegi_item, prop_nr="P17")]
                        wbitem.claims.add(euswbi.String(value=term.text, prop_nr="P8", qualifiers=qualifiers, references=references))
            try:
                wbitem.write()
                print(f"Successfully created {wbitem.id}!")
            except Exception as ex:
                doblete_re = re.search(r'Item \[\[Item:(Q\d+)\|Q\d+\]\] already has label', str(ex))
                if doblete_re:
                    doblete = euswbi.wbi.item.get(entity_id=doblete_re.group(1))
                    doblete.claims.add(euswbi.Item(value=kontzeptu_eskema, prop_nr="P6"))
                    doblete.claims.add(euswbi.Item(value=hiztegi_item, prop_nr="P17"))
                    doblete.claims.add(euswbi.String(value=f"{hiztegi_name}_{term_id}", prop_nr="P15"))
                    doblete.write()
                    print(f"RE-USED EXISTING ITEM {doblete.id}!")
                else:
                    print("Unknown error:",str(ex))



            time.sleep(1)




print("Finished.")
