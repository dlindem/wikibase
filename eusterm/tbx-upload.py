import os, time, re, json, csv, sys, requests
from xml.etree import ElementTree
import euswbi

subjectfields = {}
doublettes = []

def create_hiztegi_item(hiztegi_title):
    wbitem = euswbi.wbi.item.new()
    wbitem.claims.add(euswbi.Item(value="Q20876", prop_nr="P5"), action_if_exists=euswbi.ActionIfExists.MERGE_REFS_OR_APPEND)
    wbitem.labels.set("eu", hiztegi_title)
    wbitem.write()
    with open('TBX/hiztegiak.csv', 'a') as file:
        file.write(f"{hiztegi_title}\t{wbitem.id}\n")
    return wbitem.id

def get_minus_one_item(termentry=None, hiztegi_id=None):
    for langset in termentry.findall("langSet"):
        lang = langset.attrib['{http://www.w3.org/XML/1998/namespace}lang']
        if lang == "eu":
            for tig in langset.findall("tig"):
                for term in tig.findall("term"):
                    label = term.text.strip()
    query = """PREFIX euswb: <https://eusterm.wikibase.cloud/entity/>
    PREFIX eusdp: <https://eusterm.wikibase.cloud/prop/direct/>
    
    select (strafter(str(?concept),str(euswb:)) as ?qid)
    where {
      ?concept eusdp:P17 euswb:"""+hiztegi_id+"""; eusdp:P8 ?term.
      filter(str(?term)='"""+label+"""')
    } order by ?concept"""
    bindings = euswbi.wbi_helpers.execute_sparql_query(query=query)['results']['bindings']
    if len(bindings) > 1:
        print(f"Ambiguous label {label} in {hiztegi_id}. Taking older item")
    time.sleep(2)
    if len(bindings) == 0:
        return None
    return bindings[0]['qid']['value']

def process_term(termentry=None, wbitem=None, hiztegi_title=None, count=0):
    references = [euswbi.Item(value=hiztegi_id, prop_nr="P17")]
    term_id = termentry.attrib['id']
    if term_id == "-1":  # entries with undefined ID
        term_id = f"@{count}"
    wbitem.descriptions.set("eu", f"{re.sub(r'Hiztegia', 'Hiztegiko kontzeptua', hiztegi_title)} (#{term_id})")
    wbitem.descriptions.set("en", f"{hiztegi_title} concept entry #{term_id}")
    wbitem.descriptions.set("es", f"Concepto #{term_id} en {hiztegi_title}")
    wbitem.descriptions.set("fr", f"Concept #{term_id} dans {hiztegi_title}")
    wbitem.claims.add(euswbi.Item(value=hiztegi_id, prop_nr="P17"), action_if_exists=euswbi.ActionIfExists.MERGE_REFS_OR_APPEND)
    wbitem.claims.add(euswbi.String(value=f"{hiztegi_title} TBX: {term_id}", prop_nr="P15"), euswbi.ActionIfExists.REPLACE_ALL)
    setlabellangs = []

    # subjectField
    for descrip in termentry.findall("descrip"):
        if descrip.attrib['type'] == "subjectField":
            if descrip.text.strip() not in subjectfields[hiztegi_title]:
                print(f"Error: Found unknown subject field: {descrip.text}")
                sys.exit()
            wbitem.claims.add(euswbi.Item(value=subjectfields[hiztegi_title][descrip.text.strip()], prop_nr="P166"))

    # terms
    for langset in termentry.findall("langSet"):
        lang = langset.attrib['{http://www.w3.org/XML/1998/namespace}lang']
        for descripgrp in langset.findall("descripGrp"):
            for descrip in descripgrp.findall("descrip"):
                if descrip.attrib['type'] == "definition":
                    if lang == "eu":
                        wbitem.claims.add(euswbi.String(value=descrip.text[:999].strip(), prop_nr="P13", references=references), action_if_exists=euswbi.ActionIfExists.REPLACE_ALL)
                    else:
                        wbitem.claims.add(
                            euswbi.MonolingualText(language=lang, text=descrip.text[:999].strip(), prop_nr="P183", references=references), action_if_exists=euswbi.ActionIfExists.MERGE_REFS_OR_APPEND)

        for tig in langset.findall("tig"):
            qualifiers = []
            for termnote in tig.findall("termNote"):
                if termnote.attrib['type'] == "normativeAuthorization":
                    qualifiers = [euswbi.String(value=termnote.text.strip(), prop_nr="P18")]
            for term in tig.findall("term"):
                if lang not in setlabellangs:
                    wbitem.labels.set(lang, term.text.strip())
                    setlabellangs.append(lang)
                else:
                    wbitem.aliases.set(lang, term.text.strip())

                if lang == "eu":
                    print(f"Processing term: {term.text} ({hiztegi_title})")
                    wbitem.claims.add(
                        euswbi.String(value=term.text.strip(), prop_nr="P8", qualifiers=qualifiers, references=references), action_if_exists=euswbi.ActionIfExists.MERGE_REFS_OR_APPEND)
                else:
                    wbitem.claims.add(euswbi.MonolingualText(language=lang, text=term.text.strip(), prop_nr="P184",
                                                             references=references), action_if_exists=euswbi.ActionIfExists.MERGE_REFS_OR_APPEND)
    return wbitem

def create_subjects(hiztegi_title=None, hiztegi_id=None, body=None):
    global subjectfields
    with open('TBX/subjectfield_mapping.csv', 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if row[2] not in subjectfields:
                subjectfields[row[2]] = {}
            subjectfields[row[2]][row[0]] = row[1]
    if hiztegi_title not in subjectfields:
        subjectfields[hiztegi_title] = {}
    for termentry in body.findall("termEntry"):
        # subjectField
        for descrip in termentry.findall("descrip"):
            if descrip.attrib['type'] == "subjectField":
                if descrip.text.strip() not in subjectfields[hiztegi_title]:
                    print(f"Will create item for subject field: {descrip.text}")
                    wbitem = euswbi.wbi.item.new()
                    wbitem.labels.set('eu', descrip.text.strip())
                    wbitem.claims.add(euswbi.Item(value="Q10531", prop_nr="P5"))  # instance of UZEI arlo-adierazle
                    wbitem.claims.add(euswbi.Item(value=hiztegi_id, prop_nr="P17"))  # iturburua: Hiztegia
                    wbitem.write()
                    print(f"Successfully created {wbitem.id}!")
                    subjectfields[hiztegi_title][descrip.text.strip()] = wbitem.id
                    with open('TBX/subjectfield_mapping.csv', 'a') as csvfile:
                        csvfile.write(f"{descrip.text.strip()}\t{wbitem.id}\t{hiztegi_title}\n")
                        print(f"Stored mapping to file: {descrip.text.strip()} > {wbitem.id}")
                    time.sleep(1)
                # else:
                #     print(f"Item for subject field already existing: {descrip.text.strip()} - {subjectfields[hiztegi_title][descrip.text.strip()]}")

def create_terms(hiztegi_title=None, hiztegi_id=None, body=None):
    global subjectfields
    global existing_concepts
    global doublettes
    count = 0
    
    for termentry in body.findall("termEntry"):
        doublette = False
        count += 1
        if termentry.attrib['id'] == "-1":
            term_id = f"{hiztegi_title}_@{count}"
            term_id_new = f"{hiztegi_title} TBX: @{count}"
        else:
            term_id = f"{hiztegi_title}_{termentry.attrib['id']}"
            term_id_new = f"{hiztegi_title} TBX: @{termentry.attrib['id']}"
        if term_id in existing_concepts:
            print(f"Will review item for term {term_id}: {existing_concepts[term_id]}")
            wbi_item = process_term(count=count, hiztegi_title=hiztegi_title, termentry=termentry, wbitem=euswbi.wbi.item.get(entity_id=existing_concepts[term_id]))
        elif term_id_new in existing_concepts:
            print(f"Will review item for term {term_id_new}: {existing_concepts[term_id_new]}")
            wbi_item = process_term(count=count, hiztegi_title=hiztegi_title, termentry=termentry, wbitem=euswbi.wbi.item.get(entity_id=existing_concepts[term_id_new]))
        elif termentry.attrib['id'] == "-1":
            wbi_item_id = get_minus_one_item(termentry=termentry, hiztegi_id=hiztegi_id)
            if wbi_item_id:
                wbi_item = process_term(count=count, hiztegi_title=hiztegi_title, termentry=termentry,
                                    wbitem=euswbi.wbi.item.get(entity_id=wbi_item_id))
                print(f"Will use existing item for term {term_id}: {wbi_item_id}")
            else:
                print(f"Will create item for term {term_id}")

                wbi_item = process_term(count=count, hiztegi_title=hiztegi_title, termentry=termentry,
                                        wbitem=euswbi.wbi.item.new())
        else:
            print(f"Will create item for term {term_id}")
            wbi_item = process_term(count=count, hiztegi_title=hiztegi_title, termentry=termentry, wbitem=euswbi.wbi.item.new())
        try:
            wbi_item.write()
            print(f"{count}: Successfully created or modified https://eusterm.wikibase.cloud/wiki/Item:{wbi_item.id}!")
        except Exception as ex:
            existing_item_re = re.search(r'Item \[\[Item:(Q\d+)\|Q\d+\]\] already has label', str(ex))
            if existing_item_re:
                with open('TBX/doublettes.txt', "a") as f:
                    f.write(f"{wbi_item.id}\t{existing_item_re.group(1)}\n")
                existing_item = process_term(count=count, hiztegi_title=hiztegi_title, termentry=termentry, wbitem=euswbi.wbi.item.get(entity_id=existing_item_re.group(1)))
                existing_item.write()
                print(f"{count}: RE-USED EXISTING ITEM https://eusterm.wikibase.cloud/wiki/Item:{existing_item.id}!")
            else:
                input("Unknown error (press enter for skip and continue):", str(ex))
        time.sleep(1)


with open('TBX/hiztegiak.csv','r') as f:
    reader = csv.reader(f, delimiter='\t')
    hiztegiak = {}
    for row in reader:
        hiztegiak[row[0]] = row[1]

with open('TBX/euskalterm_concepts.csv','r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    existing_concepts = {}
    for row in reader:
        id = row['id']
        if id != "-1":
            existing_concepts[id] = row['concept']
            id = re.sub(r'_(\d+)',' Hiztegia_\1',id)
            existing_concepts[id] = row['concept']

for path, dir, files in os.walk('TBX'):
    tbx_list = files

for file in files:
    if not file.endswith('.tbx'):
        continue
    print(f"Processing {file}")
    with open('TBX/'+file,'r') as f:
        filetxt = re.sub('&','&amp;',f.read())
    tree = ElementTree.ElementTree(ElementTree.fromstring(filetxt))
    martif = tree.getroot()
    for title in martif.iter("title"):
        hiztegi_title = title.text.strip()
    if hiztegi_title in hiztegiak:
        hiztegi_id = hiztegiak[hiztegi_title]
        if hiztegi_id not in ["Q10544", "Q20878", "Q21642", "Q21947", "Q22682", "Q23001", "Q23110", "Q26406", "Q26782", "Q27139", "Q27231", "Q27598", "Q27885"]:
            continue
        # key = input(f"Skip {hiztegi_title}, already there as {hiztegi_id}? Y for processing, else for skipping.")
        # time.sleep(1)
        # if key != "Y":
        #     continue

    else:
        hiztegi_id = create_hiztegi_item(hiztegi_title)
        hiztegiak[hiztegi_title] = hiztegi_id

    for text in martif.findall("text"):
        for body in text.findall("body"):
            create_subjects(hiztegi_title=hiztegi_title, hiztegi_id=hiztegi_id, body=body)
            create_terms(hiztegi_title=hiztegi_title, hiztegi_id=hiztegi_id, body=body)






