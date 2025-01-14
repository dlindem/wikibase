import json, re, sys, os

result = []
pos_stat = {}
posmap = {
    'Substantivo': 'Q6',
    # 'Verbo': 'Q7',
    'Adjetivo': 'Q8'
    # 'Advérbio': 'Q9',
    # 'Numeral': 'Q10'
}

gendermap = {
    'm': 'Q14',
    'f': 'Q15'
}

flexmap = {
    'ms': ['Q12', 'Q14'],
    'mp': ['Q13', 'Q14'],
    'fs': ['Q12', 'Q15'],
    'fp': ['Q13', 'Q15'],
    's': ['Q12'],
    'p': ['Q13']
}

for filename in os.listdir('data/wikt'):
    try:
        with (open(f'data/wikt/{filename}') as jsonfile):
            entries = json.load(jsonfile)
    except:
        pass
    for entrytext in entries:
        print(entrytext)


        poslist = re.findall(r'==[\w ]+==', entrytext)
        for posblock in poslist:
            pos = posblock.replace("=", "")
            if pos not in pos_stat:
                pos_stat[pos] = 1
            else:
                pos_stat[pos] += 1
            if pos in posmap:
                lemma = filename.replace("_"," ").replace(".json", "")
                reference = f"https://pt.wiktionary.org/wiki/{lemma.replace(" ","_")}#mwl"
                lexeme = {'wikitext': entrytext, 'lemma': lemma, 'reference':reference, 'forms': [], 'pos': posmap[pos]}
            else:
                print(f"unknown POS: {pos}")
                continue

            flex_re = re.search(r'=='+pos+r'==¶\{\{flex.mwl\|([^\}]*)', entrytext)
            if flex_re:
                flex = flex_re.group(1).split("|")
                for grp in flex:
                    try:
                        gram = grp.split("=")[0]
                        form = grp.split("=")[1]
                        if gram in flexmap:
                            lexeme['forms'].append({'form': form, 'gram': flexmap[gram]})
                        else:
                            print(f"unknown gram: {gram}")
                    except:
                        print(f"Problems parsing inflected forms.")


            hyphen_re = re.search(r'\{\{?p?r?o?p?a?r?oxítona\|([^=]+)\|\w+=mwl\}\}', entrytext)
            if hyphen_re:
                lexeme['hyphen'] = hyphen_re.group(1)

            gender_re = re.search(r'{{([mf])}}', entrytext)
            if gender_re:
                lexeme['gender'] = gendermap[gender_re.group(1)]

            senseblock = re.search(r'¶(#[^¶]+)', entrytext).group(1)
            senses = re.findall(r'# [^#]+', senseblock)
            print(senses)
            lexeme['senses'] = senses

            result.append(lexeme)
with open('data/pos-stat-wikt.json', 'w') as file:
    json.dump(pos_stat, file, indent=2)
with open('data/parsed-wikt.json', 'w') as file:
    json.dump(result, file, indent=2)
print(result)