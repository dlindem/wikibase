import re, json
from nltk.tokenize import word_tokenize

def lexicon_build(textname=None, doclink=None):
    with open(f'data/{textname}.wikitext') as file:
        wikitext = file.read()
        wikitext = wikitext.replace("\n","")

    spans = wikitext.split('<span lang="')
    print("Wikitestua kargatuta. Goiburua hau da:\n"+spans.pop(0))
    lexicon = {"eu": {}, "es": {}, "la": {}}
    actual_aingura = ""
    for span in spans:
        lang = span[0:2]
        print(f"Atal honen hizkuntza: {lang}")

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
                continue # aingura is right at the begin
            try:
                actual_aingura = re.search(r'^([^\}]+)\}\}', paragraph).group(1)
            except:
                pass # actual_aingura stays the same
            paragraph = re.sub('  +', ' ',paragraph.replace('\n',' '))
            tokens = word_tokenize(paragraph)
            for token in tokens:
                if re.search(r"[^\w]", token) or re.search(r"\d", token):
                    continue
                aingura_link = doclink + actual_aingura
                context_re = re.compile(r' ?[^\.\}]*'+token+'[^\.\}]*\.?')
                contexts = re.findall(context_re, paragraph)
                if len(contexts) == 0:
                    contexts = [" *** ERROR: Testuingurua ez dut topatu *** "]
                for context in contexts:
                    if token.lower() not in lexicon[lang]:
                        lexicon[lang][token.lower()] = [(aingura_link, context.replace("'","").strip())]
                    else:
                        lexicon[lang][token.lower()].append((aingura_link, context.replace("'","").strip()))
    return lexicon

lexicon = {"eu": {}, "es": {}, "la": {}}
documents = [("HHHT", "https://eu.wikisource.org/wiki/Hiztegi_Hirukoitzeko_hitzaurreko_testuak#"),
             ("LAZK", "https://eu.wikisource.org/wiki/Azkoitiko_Sermoia#")]
for document, baselink in documents:
    doc_lexicon = lexicon_build(textname=document, doclink=baselink)
    with open(f'data/{document}_lexicon.json', 'w') as file:
        json.dump(doc_lexicon, file, indent=2)
    for lang in ["eu", "es", "la"]:
        for word in doc_lexicon[lang]:
            if word not in lexicon[lang]:
                lexicon[lang][word] = doc_lexicon[lang][word]
            else:
                lexicon[lang][word] += doc_lexicon[lang][word]

sorted_lexicon = {"eu": dict(sorted(lexicon['eu'].items())),
                  "es": dict(sorted(lexicon['es'].items())),
                  "la": dict(sorted(lexicon['la'].items()))}


with open('data/Larramendi_lexicon.json', 'w') as file:
    json.dump(sorted_lexicon, file, indent=2)

header = "testu_hitza\tlemma\tparagrafoa\ttestuingurua\n"
taulak = {"eu": header, "es": header, "la": header}
for lang in ["eu", "es", "la"]:
    for word in lexicon[lang]:
        for link, context in lexicon[lang][word]:
            taulak[lang] += f"{word}\t\t{link}\t{context}\n"
for lang in ["eu", "es", "la"]:
    with open(f'data/Larramendi_lexicon_{lang}.csv', 'w') as file:
        file.write(taulak[lang])
