import re, json, os

anotazioak = {}

files = os.listdir('html_hrefs/html')
for filename in files:
    print(filename)
    participant = re.search(r'^([^_]+)', filename).group(1)
    print(participant)

    with open(f'html_hrefs/html/{filename}') as file:
        content = file.read()

    links = re.findall(r'<a href="([^"]+)"', content)

    print(links)

    anotazioak[participant] = {"wikidata": [], "euskalterm": [], "other": []}
    for link in links:
        if "www.wikidata.org" in link:
            qid_re = re.search(r'/(Q[0-9]+)', link)
            if qid_re:
                if qid_re.group(1) not in anotazioak[participant]["wikidata"]:
                    anotazioak[participant]["wikidata"].append(qid_re.group(1))
        elif "Euskalterm" in link:
            if link not in anotazioak[participant]["euskalterm"]:
                anotazioak[participant]["euskalterm"].append(link)
        else:
            if link not in anotazioak[participant]["other"]:
                anotazioak[participant]["other"].append(link)

with open('html_hrefs/erauzitakoak_ikasleka.json', 'w') as file:
    json.dump(anotazioak, file, indent=2)
