import xwbi, xwb, config
import csv, time, json, sys

with open('data/languages_table.csv') as csvfile:
    language_csv = csv.DictReader(csvfile, delimiter=",")
    languages = {}
    for row in language_csv:
        languages[row['wiki_languagecode']] = {'langname': row['language_name'], 'qid': row['wikibase_item']}

print('Will get concept-equivalent to lexeme-sense mappings via SPARQL...\n')
query = """
PREFIX enwb: <https://eneoli.wikibase.cloud/entity/>
PREFIX endp: <https://eneoli.wikibase.cloud/prop/direct/>
PREFIX enp: <https://eneoli.wikibase.cloud/prop/>
PREFIX enps: <https://eneoli.wikibase.cloud/prop/statement/>
PREFIX enpq: <https://eneoli.wikibase.cloud/prop/qualifier/>

select ?concept ?equiv ?equiv_lang ?equiv_statement ?lexeme_sense ?lemma ?lem_lang ?desc ?en_desc
where {
  ?concept enp:P57 ?equiv_statement.
  ?equiv_statement enps:P57 ?equiv. bind(lang(?equiv) as ?equiv_lang)
  filter not exists {?equiv_statement enpq:P58 ?warning.}
  optional {?concept schema:description ?desc. filter(lang(?desc) = ?equiv_lang)}
  optional {?concept schema:description ?en_desc. filter(lang(?en_desc) = "en")}                                                   
  optional {?lexeme_sense endp:P12 ?concept.
           ?lexeme ontolex:sense ?lexeme_sense; wikibase:lemma ?lemma.
           bind(lang(?lemma) as ?lem_lang)
           filter (?lem_lang = ?equiv_lang)} 
} order by ?lang lcase(?equiv)
"""
print(query)
bindings = xwbi.wbi_helpers.execute_sparql_query(query=query)['results']['bindings']
amount = len(bindings)
print('Found '+str(amount)+' concept equivalents to look at.\n')
time.sleep(1)
count = 0
lastlem = "abréviation"
lastlexeme = "L10"
for row in bindings:
    count += 1
    concept_qid = row['concept']['value'].replace(config.wikibase_entity_ns, "")
    wikilang = row['equiv_lang']['value']
    langqid = languages[wikilang]['qid']
    equiv = row['equiv']['value']
    print(f'\n[{count}] Now looking at concept {concept_qid}, "{equiv}"@{wikilang}.')

    if 'lexeme_sense' in row: # this equiv already is linked to from a sense
        lexeme_sense = row['lexeme_sense']['value'].replace(config.wikibase_entity_ns, "")
        lemma = row['lemma']['value']
        print(f'>>> concept equiv is linked to "{lemma}"@{wikilang} ({lexeme_sense})')
        if lemma != equiv:
            print(f'>>> WARNING: Equivalent and lemma should be equal strings, and they are not!!')
            input("Press ENTER to proceed")
        time.sleep(0.5)
        continue
    lemma = None

    if 'desc' not in row:
        row['desc'] = None
    if 'en_desc' not in row:
        row['en_desc'] = None

    if equiv != lastlem:
        print(f"Will create a new lexeme.")
        lexeme = xwbi.wbi.lexeme.new(language=langqid, lexical_category="Q20") # a new noun
        print(f'Will write lemma "{equiv}"@{wikilang}')
        lexeme.lemmas.set(language=wikilang, value=equiv)
        claim = xwbi.Item(prop_nr='P5', value='Q13')
        lexeme.claims.add(claim)

    else:
        f'The equivalent "{equiv}"@{wikilang} is repeated in this list... will create new sense for {lastlexeme}'
        lexeme = xwbi.wbi.lexeme.get(entity_id=lastlexeme)

    new_sense = xwbi.Sense()
    new_sense.claims.add(xwbi.Item(prop_nr='P12', value=concept_qid)) # link from sense to concept

    if row['desc']:
        new_sense.glosses.set(language=wikilang, value=row['desc']['value'])
    elif row['en_desc']:
        new_sense.glosses.set(language='en', value=row['en_desc']['value'])
    else:
        new_sense.glosses.set(language=wikilang, value=f'[Empty gloss; describes concept {concept_qid}]')

    lexeme.senses.add(new_sense)
    print(lexeme.senses)
    print(lexeme.senses.get_json())
    # if row["desc"]:
    #     glossdata = {"glosses":{wikilang: {"language": wikilang, "value": row["desc"]['value']}}}
    # elif row["en_desc"]:
    #     glossdata = {"glosses":{"en": {"language": "en", "value": row["en_desc"]['value']}}}
    # else:
    #     glossdata = {"glosses":{"en": {"language": "en", "value": "[Empty gloss; describes concept {concept_qid}]"}}}
    #
    # newsense_id = xwb.addsense(lexeme_id, glossdata)

    with open('data/lexeme_before_writing.json', 'w') as jsonfile:
        json.dump(lexeme.get_json(), jsonfile, indent=2)

    done = False
    while not done:
        try:
            lexeme.write()
            done = True
            lexeme_id = lexeme.id
            sense_id = lexeme.get_json()['senses'][-1]['id']
            print(f"Successfully written to lexical entry {lexeme_id}; newest nense is {sense_id}.")
            with open('data/lexeme.json', 'w') as jsonfile:
                json.dump(lexeme.get_json(), jsonfile, indent=2)
            lastlexeme = lexeme_id
            lastlem = equiv
        except Exception as ex:
            if "404 Client Error" in str(ex):
                print('Got 404 response from wikibase, will wait and try again...')
                time.sleep(10)
            else:
                print('Unexpected error:\n' + str(ex))
                sys.exit()



    xwb.setqualifier(concept_qid, "P57", row['equiv_statement']['value'].replace(f"{config.wikibase_entity_ns}statement/",""), "P59", sense_id, "sense")
    sys.exit()




