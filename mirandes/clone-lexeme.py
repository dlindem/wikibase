import requests, re, time, sys, csv, wdwbi, xwb

# get wikidata alignment
r = requests.get("https://lhenguabase.wikibase.cloud/query/sparql?format=json&query=%23title%3A%20All%20wikidata%20alignments%0A%0APREFIX%20lwb%3A%20%3Chttps%3A%2F%2Flhenguabase.wikibase.cloud%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttps%3A%2F%2Flhenguabase.wikibase.cloud%2Fprop%2Fdirect%2F%3E%0A%0Aselect%20%3Flh%20%3Flh_id%20%3Fwd%20%3Fwd_id%20where%20%7B%0A%20%20%3Flh%20ldp%3AP1%20%3Fwd_id.%0A%20%20bind(iri(concat(str(wd%3A)%2C%3Fwd_id))%20as%20%3Fwd)%0A%20%20bind(strafter(str(%3Flh)%2Cstr(lwb%3A))%20as%20%3Flh_id)%0A%20%20%7D")
wd_alignment = {}
for binding in r.json()['results']['bindings']:
    wd_alignment[binding['lh_id']['value']] = binding['wd_id']['value']
print(str(wd_alignment) + "\nwd alignment loaded.")

def buildclaim(datatype=None, prop_nr=None, value=None):
    global wd_alignment
    if datatype == "string":
        return wdwbi.String(prop_nr=prop_nr, value=value)
    elif datatype == "wikibase-item":
        obj_qid = value['id']
        if obj_qid not in wd_alignment:
            return None
        return wdwbi.Item(prop_nr=prop_nr, value=wd_alignment[obj_qid])

    else:
        return None

def write_mapping(lexeme_mapping):
    xwb.stringclaim(lexeme_mapping['lexeme']['wb'], "P1", lexeme_mapping['lexeme']['wd'])
    for sense in lexeme_mapping['senses']:
        xwb.stringclaim(sense['wb'], "P1", sense['wd'])
    for form in lexeme_mapping['forms']:
        xwb.stringclaim(form['wb'], "P1", form['wd'])
    print(f"Mappings to new wd lexeme written to wb lexeme: {lexeme_mapping}")


def clone_lexeme(lexeme_id=None):
    global wd_alignment
    if lexeme_id in wd_alignment:
        print(f"\nERROR: {lexeme_id} lexeme has been exported already as http://www.wikidata.org/entity/{wd_alignment[lexeme_id]}")
        return None
    print(f"Will clone Wikibase lexeme {lexeme_id} on Wikidata.")
    lexeme_json = requests.get(f"https://lhenguabase.wikibase.cloud/wiki/Special:EntityData/{lexeme_id}.json").json()['entities'][lexeme_id]
    print(lexeme_json)
    # new lexeme
    wdlexeme = wdwbi.wbi.lexeme.new(language=wd_alignment[lexeme_json['language']], lexical_category=wd_alignment[lexeme_json['lexicalCategory']])
    wdlexeme.lemmas.set(language='mwl', value=lexeme_json['lemmas']['mwl']['value'])
    # reference to Lhenguabase
    wdlexeme.claims.add(wdwbi.Item(prop_nr="P1343", value="Q131756013", qualifiers=[wdwbi.URL(prop_nr="P973", value="https://lhenguabase.wikibase.cloud/wiki/"+lexeme_json['title'])]))
    # props
    hyphenation = None
    for prop in lexeme_json['claims']:
        if prop in wd_alignment:
            # move hyphenation from lexeme to form
            if prop == "P10":
                hyphenation = buildclaim(datatype="string", prop_nr=wd_alignment[prop], value=lexeme_json['claims'][prop][0]['mainsnak']['datavalue']['value'].replace("|","‧"))
            else:
                print(f"Will clone wb:{prop} to wd:{wd_alignment[prop]}.", end=' ')
                values = []
                for claim in lexeme_json['claims'][prop]:
                    newclaim = buildclaim(datatype=claim['mainsnak']['datatype'], prop_nr=wd_alignment[prop], value=claim['mainsnak']['datavalue']['value'])
                    if newclaim:
                        wdlexeme.claims.add(newclaim)
                        values.append(claim['mainsnak']['datavalue']['value'])
                    print(f"...values added: {values}")

    sensecount = 0
    sense_mapping = []
    for sense in lexeme_json['senses']:
        newsense = wdwbi.Sense()
        sensecount += 1
        sense_mapping.append({'wb': sense['id'], 'wd': f'-S{sensecount}'})
        for gloss in sense['glosses']:
            newsense.glosses.set(language=sense['glosses'][gloss]['language'], value=sense['glosses'][gloss]['value'])
        for prop in sense['claims']:
            if prop not in wd_alignment:
                continue
            print(f"{sense['id']} Will clone wb:{prop} to wd:{wd_alignment[prop]}.", end=' ')
            values = []
            for claim in lexeme_json['claims'][prop]:
                newclaim = buildclaim(datatype=claim['mainsnak']['datatype'], prop_nr=wd_alignment[prop],
                                      value=claim['mainsnak']['datavalue']['value'])
                if newclaim:
                    newsense.claims.add(newclaim)
                    values.append(claim['mainsnak']['datavalue']['value'])
                print(f"...values added: {values}")
        wdlexeme.senses.add(newsense)

    formscount = 0
    forms_mapping = []
    for form in lexeme_json['forms']:
        newform = wdwbi.Form()
        formscount += 1
        forms_mapping.append({'wb': form['id'], 'wd': f'-F{formscount}'})
        for representation in form['representations']:
            if form['representations'][representation]['value'] == lexeme_json['lemmas']['mwl']['value'] and hyphenation:
                newform.claims.add(hyphenation) # makes hyphenation statement to this form
                print(f"Canonical form {form['representations'][representation]['value']} gets hyphenation statement.")
            newform.representations.set(language=form['representations'][representation]['language'], value=form['representations'][representation]['value'])
            wd_gramfeat = []
            for gramfeat in form['grammaticalFeatures']:
                if gramfeat in wd_alignment:
                    wd_gramfeat.append(wd_alignment[gramfeat])
            newform.grammatical_features = wd_gramfeat
            print(f"Grammatical features to write to Wikidata: {wd_gramfeat}")
        for prop in form['claims']:
            if prop not in wd_alignment:
                continue
            print(f"{form['id']}: Will clone wb:{prop} to wd:{wd_alignment[prop]}.", end=' ')
            values = []
            for claim in lexeme_json['claims'][prop]:
                newclaim = buildclaim(datatype=claim['mainsnak']['datatype'], prop_nr=wd_alignment[prop],
                                      value=claim['mainsnak']['datavalue']['value'])
                if newclaim:
                    newform.claims.add(newclaim)
                    values.append(claim['mainsnak']['datavalue']['value'])
                print(f"...values added: {values}")
        wdlexeme.forms.add(newform)

    # write to wikidata
    attempts = 0
    done = False
    while not done and attempts < 5:
        attempts += 1
        try:
            wdlexeme.write(is_bot=True, summary="Mirandese lexeme creation, from {Q|Q131756013} data.")
            lexeme_mapping = {'lexeme': {'wb': lexeme_id, 'wd': wdlexeme.id}, 'senses': [], 'forms': []}
            for sense in sense_mapping:
                lexeme_mapping['senses'].append({'wb': sense['wb'], 'wd': wdlexeme.id+sense['wd']})
            for form in forms_mapping:
                lexeme_mapping['forms'].append({'wb': form['wb'], 'wd': wdlexeme.id+form['wd']})
            print('Successfully processed', wdlexeme.id)
            done = True
        except Exception as ex:
            print('Failed to write lexeme with error message:\n' + str(ex))
            print('\nThis was attempt #' + str(attempts) + '\n')
            time.sleep(2)
        time.sleep(0.5)
    if not done:
        print('Will exit the script after five failed lexeme write attempts.')
        sys.exit()
    write_mapping(lexeme_mapping)

lexemes_to_clone = """L584
L575
L587
L598
L603
L612
L620
L641
L643
L644
L645
L653
L663
L665
L673
L683
L692
L702
L706
L704
L711
L712
L718
L723
L737
L745
L750
L754
L758
L760
L765
L767
L770""".split('\n')

for lexeme in lexemes_to_clone:
    clone_lexeme(lexeme_id=lexeme)
    time.sleep(0.3)