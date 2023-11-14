import re, json
import urllib.request
from nltk.tokenize import word_tokenize

project_name = "Larramendi_1737_Azkoitiko_Sermoia"

wikisource_pages = ["Orrialde:Larramendi_1737_Azkoitiko_Sermoia.pdf/1", "Orrialde:Larramendi_1737_Azkoitiko_Sermoia.pdf/2"]

text = ""
for page in wikisource_pages:
    req = urllib.request.urlopen(f"http://eu.wikisource.org/wiki/{page}?action=raw")
    wikitext = req.read().decode()
    wikitext = re.sub(r"['\[\]]", "", wikitext)
    wikitext = re.sub(r"<[^>]+>", "", wikitext)
    text += wikitext + " "

print(text)
paragrafoak = re.findall(r"\{\{aingura\|[0-9]+\}\}[^\{]+", text.replace('\n',''))
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