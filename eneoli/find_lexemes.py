import json, re, time
import config_private
import xwbi
from flashtext import KeywordProcessor

print("Will get Zotero items...")
from pyzotero import zotero
pyzot = zotero.Zotero(config_private.zotero_group_nr, 'group', config_private.zotero_api_key)
zotitems = pyzot.everything(pyzot.items(tag="processed_fulltext"))

print("Getting lexicon...")
query = """
		PREFIX enwb: <https://eneoli.wikibase.cloud/entity/>
PREFIX endp: <https://eneoli.wikibase.cloud/prop/direct/>

select ?lexical_entry (lang(?lemma) as ?lang) ?lemma 
       
where { 
  ?lexical_entry endp:P5 enwb:Q13; wikibase:lemma ?lemma.
 
}
		"""
lexicon = xwbi.wbi_helpers.execute_sparql_query(query=query)['results']['bindings']
print('Found ' + str(len(lexicon)) + ' ENEOLI lexical entries.\n')
time.sleep(1)

def find_lexemes_for_lang(wikilang=None, isolang=None):
    # get bibitems of that language
    query = """
    PREFIX enwb: <https://eneoli.wikibase.cloud/entity/>
    PREFIX endp: <https://eneoli.wikibase.cloud/prop/direct/>

    select *     
    where { """
    query += f'?item endp:P5 enwb:Q2; endp:P17 ?zot; endp:P7 [endp:P50 "{isolang}"]'+ "}"
    bibitems_json = xwbi.wbi_helpers.execute_sparql_query(query=query)['results']['bindings']
    bibitems = []
    for entry in bibitems_json:
        bibitems.append(entry['zot']['value'])
    print(f"For language {isolang}, {len(bibitems)} bibitems will be processed.")

    global lexicon
    global zotitems
    keyword_processor = KeywordProcessor()
    for binding in lexicon:

        if binding['lang']['value'] == wikilang:
            keyword_processor.add_keywords_from_dict(
                {binding['lexical_entry']['value'].replace("https://eneoli.wikibase.cloud/entity/",""): [binding['lemma']['value']]}
            )
    print(f"Fed keyword processor with {len(keyword_processor)} lemmata for language '{wikilang}'.")
    if len(keyword_processor) == 0:
        return None

    count = 0

    for zotitem in zotitems:
        if zotitem['key'] not in bibitems:
            continue
        text = False
        count += 1
        children = pyzot.children(zotitem['key'])
        for child in children:
            if 'enclosure' in child['links']:
                if 'type' in child['links']['enclosure']:
                    if child['links']['enclosure']['type'] == "application/json":
                        bibitemqid = re.search(r'Q\d+', child['links']['enclosure']['title']).group(0)
                        print(f"\n[{count}/{len(bibitems)}, {wikilang}] For {bibitemqid}, retrieving fulltext json file: {child['key']}")
                        try:
                            fulltext = pyzot.file(child['key'])
                        except:
                            print(f"Error retrieving Zotero full text file, skipped.")
                            continue
                        # print(json.dumps(fulltext, indent=2))
                        if 'lemmatized' in fulltext:
                            text = fulltext['lemmatized']
                        elif 'body_lemmatized' in fulltext and 'abstract_lemmatized' in fulltext:
                            text = fulltext['abstract_lemmatized'] + ' ' + fulltext['body_lemmatized']
                        else:
                            text = None
        if not text:
            print(f"Could not load fulltext JSON. Cannot process {zotitem['key']}.")
            time.sleep(1)
            continue
        keywords = keyword_processor.extract_keywords(text)
        uniqkws = set(keywords)
        keydict= {}
        for uniqkw in uniqkws:
            keydict[uniqkw] = keywords.count(uniqkw)
        freq_order = sorted(keydict, key=keydict.get, reverse=True)
        found_lexemes = {}
        for keyw in freq_order:
            found_lexemes[keyw] = keydict[keyw]
        print(f"Found lexemes: {found_lexemes}")

        statements = []
        first_statement = True
        for lid in found_lexemes:
            if first_statement:
                statements.append({'type': 'lexeme', 'prop_nr': 'P65', 'value': lid, 'qualifiers': [
                    {'type': 'string', 'prop_nr': 'P66', 'value': str(found_lexemes[lid])}
                ], 'action': 'replace'})
                print(f"Writing first statement...", end=" ")
                xwbi.itemwrite({'qid': bibitemqid, 'statements': statements})
                time.sleep(0.2)
                first_statement = False
            else:
                statements.append({'type': 'lexeme', 'prop_nr': 'P65', 'value': lid, 'qualifiers':[
                    {'type': 'string', 'prop_nr': 'P66', 'value': str(found_lexemes[lid])}
                ], 'action': 'append'})
        # print(json.dumps(statements, indent=2))
        print(f"Writing additional statements...", end=" ")
        xwbi.itemwrite({'qid': bibitemqid, 'statements': statements})
        if len(found_lexemes) > 0:
            zotitem['data']['tags'].append({"tag": "term-indexed"})
        else:
            zotitem['data']['tags'].append({"tag": "failed_fulltext_processing"})
        pyzot.update_item(zotitem)
        print(f"Added tag 'term-indexed' to {zotitem['key']}")
        print(f"Finished processing <https://eneoli.wikibase.cloud/entity/{bibitemqid}>")

    print(f"\nFinished processing language {wikilang}.\n")

langs = {
         # "ca": "cat",
         # "da": "dan",
        # "de": "deu",
       #  "el": "ell",
      #   "en": "eng",
         "fr": "fra",
         "hr": "hrv",
         "it": "ita",
         "lt": "lit",
         "nl": "nld",
         "pt": "por",
         "uk": "ukr",
         "sv": "slv",
         "es": "spa"}

for lang in langs:
    find_lexemes_for_lang(wikilang = lang, isolang = langs[lang])