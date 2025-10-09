import re, json

with open('html_hrefs/batutako anotazioak Cuba.html') as file:
    content = file.read()

links = re.findall(r'<a href="([^"]+)"', content)

print(links)

classified_links = {"wikidata": [], "euskalterm": [], "other": []}
for link in links:
    if "www.wikidata.org" in link:
        qid_re = re.search(r'/(Q[0-9]+)', link)
        if qid_re:
            if qid_re.group(1) not in classified_links["wikidata"]:
                classified_links["wikidata"].append(qid_re.group(1))
    elif "Euskalterm" in link:
        if link not in classified_links["euskalterm"]:
            classified_links["euskalterm"].append(link)
    else:
        if link not in classified_links["other"]:
            classified_links["other"].append(link)

with open('html_hrefs/erauzitakoak.json', 'w') as file:
    json.dump(classified_links, file, indent=2)
