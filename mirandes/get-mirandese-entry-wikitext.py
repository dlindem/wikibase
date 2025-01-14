import json, requests, re, time

with open('data/pt-wikt-mirandese-pages.json') as file:
    pages = json.load(file)
for entry in pages:
    page = entry['title']
    print(f"Will download {page}...")
    r = requests.get(f"https://pt.wiktionary.org/w/api.php?action=parse&page={page}&prop=wikitext&format=json").json()
    entrytext = r['parse']['wikitext']['*'].replace("\n", "¶")
    print(entrytext)
    mirandes_re = re.findall(r'=\{\{\-mwl\-\}\}=.*\(Mirandês\)\]\]', entrytext)
    if len(mirandes_re) > 0:
        with open(f'data/wikt/{page.replace(" ","_")}.json', 'w') as f:
            json.dump(mirandes_re, f, indent=2)
    else:
        print(f"Failed to find Mirandes in: {page}")
        with open(f'data/wikt/failed/{page.replace(" ","_")}.txt', 'w') as f:
            f.write(entrytext)
    time.sleep(0.15)
