# Categoria:!Entrada_(Mirandês)

import requests, time, json


r = requests.get("https://pt.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Categoria:!Entrada_(Mirand%C3%AAs)&format=json&cmlimit=50").json()
result = r['query']['categorymembers']
print(f"Got {len(r['query']['categorymembers'])} entries.")
while "continue" in r:
    time.sleep(0.2)
    cont = r['continue']['cmcontinue']
    r = requests.get(f"https://pt.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Categoria:!Entrada_(Mirand%C3%AAs)&format=json&cmlimit=50&cmcontinue={cont}").json()
    print(f"Got {len(r['query']['categorymembers'])} entries.")
    result += r['query']['categorymembers']
    print(f"Now the result counts {len(result)} entries.")

with open('data/pt-wikt-mirandese-pages.json', 'w') as jsonfile:
    json.dump(result, jsonfile, indent=2)