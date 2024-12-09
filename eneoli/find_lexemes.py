import json, re, time
import config_private
import xwbi
from flashtext import KeywordProcessor
keyword_processor = KeywordProcessor()
from pyzotero import zotero
pyzot = zotero.Zotero(config_private.zotero_group_nr, 'group', config_private.zotero_api_key)

query = """
		PREFIX enwb: <https://eneoli.wikibase.cloud/entity/>
PREFIX endp: <https://eneoli.wikibase.cloud/prop/direct/>

select ?lexical_entry (lang(?lemma) as ?lang) ?lemma 
       
where { 
  ?lexical_entry endp:P5 enwb:Q13; wikibase:lemma ?lemma.
 
}
		"""
bindings = xwbi.wbi_helpers.execute_sparql_query(query=query)['results']['bindings']
print('Found ' + str(len(bindings)) + ' ENEOLI lexical entries.\n')
time.sleep(1)

for binding in bindings:
    if binding['lang']['value'] == "fr":
        keyword_processor.add_keywords_from_dict(
            {binding['lexical_entry']['value'].replace("https://eneoli.wikibase.cloud/entity/",""): [binding['lemma']['value']]}
        )
print(f"Fed keyword processor with {len(keyword_processor)} lemmata.")

zotitems = pyzot.everything(pyzot.items(tag="falta"))
count = 0
for zotitem in zotitems:
    count += 1
    children = pyzot.children(zotitem['key'])
    for child in children:
        if 'enclosure' in child['links']:
            if child['links']['enclosure']['type'] == "application/json":
                bibitemqid = re.search(r'Q\d+', child['links']['enclosure']['title']).group(0)
                print(f"\n[{count}/{len(zotitems)}]] For {bibitemqid}, retrieving fulltext json file: {child['key']}")

                fulltext = pyzot.file(child['key'])
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
            xwbi.itemwrite({'qid': bibitemqid, 'statements': statements})
            time.sleep(0.2)
            first_statement = False
        else:
            statements.append({'type': 'lexeme', 'prop_nr': 'P65', 'value': lid, 'qualifiers':[
                {'type': 'string', 'prop_nr': 'P66', 'value': str(found_lexemes[lid])}
            ], 'action': 'append'})
    # print(json.dumps(statements, indent=2))

    xwbi.itemwrite({'qid': bibitemqid, 'statements': statements})
    zotitem['data']['tags'].append({"tag": "term-indexed"})
    pyzot.update_item(zotitem)
    print(f"Added tag 'term-indexed' to {zotitem['key']}")
    print(f"Finished processing <https://eneoli.wikibase.cloud/entity/{bibitemqid}>")

