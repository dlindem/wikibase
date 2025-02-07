import re, json, time, sys
import urllib.request
from nltk.tokenize import word_tokenize

# get pdf index from https://eu.wikisource.org/wiki/Azkoitiko_Sermoia?action=raw

project_name = "Larramendi_1737_Azkoitiko_Sermoia"
wikisource_source_name = "Orrialde:Larramendi_1737_Azkoitiko_Sermoia.pdf/"
wikisource_pages = list(range(22))
print(f"{wikisource_pages}")

text = '<span lang="eu">'
for page in wikisource_pages:
    url = f"http://eu.wikisource.org/wiki/{wikisource_source_name}{page+1}?action=raw"
    req = urllib.request.urlopen(url)
    print(f"Got page {page+1} from {url}")
    time.sleep(1.1)
    wikitext = req.read().decode()
    # wikitext = re.sub(r"[\[\]]", "", wikitext)
    # wikitext = re.sub(r"<[^>]+>", "", wikitext)
    wikitext = re.sub(r" ''([^']+)''", r'</span><span lang="la">\1</span><span lang="eu">', wikitext)
    with open(f'data/Azkoitiko_Sermoia_{page+1}.wikitext', 'w') as txtfile:
        txtfile.write(wikitext)
    text += wikitext + " "

text += "</span>"
print(text)

# with open('data/LAZK.wikitext', 'w') as file:
#     file.write(text)
sys.exit()


text = re.sub('  +', ' ',text.replace('\n',' '))
paragrafoak = re.findall(r"\{\{aingura\|[0-9]+\}\}[^\{]+", text)
print(str(paragrafoak))

number = 0
numbered_tokens = {}
index = 0
while index < len(paragrafoak):
    parag_re = re.search(r"\{\{aingura\|([0-9]+)\}\}([^\{]+)", paragrafoak[index])
    parag = parag_re.group(1)
    parag_text = parag_re.group(2)
    tokens = word_tokenize(parag_text)
    for token in tokens:
        number += 1
        numbered_tokens[str(number)] = {'parag':parag, 'token': token}
    index += 1

print(str(numbered_tokens))

with open(f"data/{project_name}_tokens.json", "w", encoding="utf-8") as jsonfile:
    json.dump(numbered_tokens, jsonfile, indent=2)
