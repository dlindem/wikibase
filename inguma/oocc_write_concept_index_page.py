import json, csv, re

with open('data/oocc_concept_index_map.json', 'r') as f:
    map = json.load(f)

with open('data/OOCC_zotero_ziterauzi_jat_urt.csv', 'r', encoding="utf-8-sig") as f:
    reader = csv.DictReader(f, delimiter='\t')
    oocc = {}
    for row in reader:
        qid = row['oocc_item'].replace("https://wikibase.inguma.eus/entity/","")
        oocc[qid] = f"[[Item:{qid}|{row['oocc_title']}]] <small>({row['lehen_argi']}, {row['language']}) — [{row['zotero_link']} zotero]</small>"

page = """__NOTOC__
'''Koldo Mitxelena, ''Obras Completas'': Índice de Conceptos'''

Este índice fue producido a partir del ''índice de conceptos'' en [[Item:Q40477|Obras Completas, vol. XV]].

Acceso a las secciones de letras iniciales: 

[[#A|A]] [[#B|B]] [[#C|C]] [[#D|D]] [[#E|E]] [[#F|F]] [[#G|G]] [[#H|H]] [[#I|I]] [[#J|J]] [[#K|K]] [[#L|L]] [[#M|M]] [[#N|N]] [[#O|O]] [[#P|P]] [[#Q|Q]] [[#R|R]] [[#S|S]] [[#T|T]] [[#U|U]] [[#V|V]] [[#W|W]] [[#X|X]] [[#Y|Y]] [[#Z|Z]] 

➙ saltar al concepto "Vasco", tratado en una sección especial del índice: [[OOCC índice de conceptos: Vasco]]

"""
concept_name = {}
concept_names = ""
for letter in map:
    print(f" Now processing letter {letter}")
    page += f"={letter}=\n"

    for entry in map[letter]:
        print(entry)
        if 'concept' in entry:
            level = entry['level']
            print(level)
            if level == 1:
                page += f"=={entry['concept'].strip()}==\n"
                concept_name[1] = entry['concept'].strip()
            elif level == 2:
                page += f"==={entry['concept'].strip()}===\n"
                concept_name[2] = entry['concept'].strip()
            elif level == 3:
                page += f"===={entry['concept'].strip()}====\n"
                concept_name[3] = entry['concept'].strip()
            elif level == 4:
                page += f"====={entry['concept'].strip()}=====\n"
                concept_name[4] = entry['concept'].strip()
            elif level == 5:
                page += f"======{entry['concept'].strip()}======\n"
                concept_name[5] = entry['concept'].strip()

            concept_namestr = ""
            for i in range(level):
                print(i)
                concept_namestr += f" - {concept_name[i+1]}"
            concept_namestr = concept_namestr[3:]

            print(concept_namestr)
            concept_names += concept_namestr + "\n"
            if 'data' in entry:
                for qid in entry['data']:
                    page += f"* {entry['data'][qid]['vol']}: {", ".join(entry['data'][qid]['pp'])} — {oocc[qid]}\n"
        if 'redirect' in entry:
            page += f"➙ {entry['redirect'].replace("v. ", "").strip()}\n"


with open('data/oocc_concept_index_page.txt', 'w') as f:
    f.write(page)
with open('data/oocc_concept_index_names.txt', 'w') as f:
    f.write(concept_names)


