import re, json
from nltk.tokenize import word_tokenize

def lexicon_build(textname=None, doclink=None):
    with open(f'data/{textname}.wikitext') as file:
        wikitext = file.read()
        wikitext = wikitext.replace("\n","")

    spans = wikitext.split('<span lang="')
    print("Wikitestua kargatuta. Goiburua hau da:\n"+spans.pop(0))
    lexicon = {}
    actual_aingura = ""
    for span in spans:
        lang = span[0:2]
        print(f"Atal honen hizkuntza: {lang}")
        if lang != "eu":
            continue
        span_content = re.search(rf'{lang}">(.*)</span>', re.sub(r'</ ?br>', ' ', span)).group(1)
        print(span_content)
        # find aingurak
        aingurak_re = re.compile(r'\{\{aingura\|([^\}]+)\}\}')
        aingurak = aingurak_re.findall(span_content)
        print(aingurak)
        if len(aingurak) == 0: # hartu aurreko aingura
            span_content = "{{aingura|" + actual_aingura + "}}" + span_content
        for paragraph in span_content.split('{{aingura|'):
            if len(paragraph.strip()) == 0:
                continue
            actual_aingura = re.search(r'^([^\}]+)\}\}', paragraph).group(1)
            paragraph = re.sub('  +', ' ',paragraph.replace('\n',' '))
            tokens = word_tokenize(paragraph)
            for token in tokens:
                if re.search(r"[^\w]", token) or re.search(r"\d", token):
                    continue
                aingura_link = doclink + actual_aingura
                if token.lower() not in lexicon:
                    lexicon[token.lower()] = [aingura_link]
                elif aingura_link not in lexicon[token.lower()]:
                    lexicon[token.lower()].append(aingura_link)
    return lexicon

lexicon = {}
documents = [("HHHT", "https://eu.wikisource.org/wiki/Hiztegi_Hirukoitzeko_hitzaurreko_testuak#"),
             ("LAZK", "https://eu.wikisource.org/wiki/Azkoitiko_Sermoia#")]
for document, baselink in documents:
    doc_lexicon = lexicon_build(textname=document, doclink=baselink)
    with open(f'data/{document}_lexicon.json', 'w') as file:
        json.dump(doc_lexicon, file, indent=2)
    for word in doc_lexicon:
        if word not in lexicon:
            lexicon[word] = doc_lexicon[word]
        else:
            lexicon[word] += doc_lexicon[word]


with open('data/Larramendi_lexicon.json', 'w') as file:
    json.dump(dict(sorted(lexicon.items())), file, indent=2)