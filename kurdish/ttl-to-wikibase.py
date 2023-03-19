from rdflib import Graph, URIRef

# load existing lexemes lookup table
with open('data/lexeme-mapping.csv') as mappingcsv:
	mappingrows = mappingcsv.read().split('\n')
	lexeme_map = {}
	for row in mappingrows:
		mapping = row.split('\t')
		if len(mapping) == 2:
			lexeme_map[mapping[0]] = mapping[1]

ontology_map = {
    "http://www.lexinfo.net/ontology/2.0/lexinfo#noun": "Q6",
    "http://www.lexinfo.net/ontology/2.0/lexinfo#verb": "Q7",
    "http://www.lexinfo.net/ontology/2.0/lexinfo#adjective": "Q8",
    "http://www.lexinfo.net/ontology/2.0/lexinfo#adverb": "Q9",
    "http://www.lexinfo.net/ontology/2.0/lexinfo#preposition": "Q10",
    "http://www.lexinfo.net/ontology/2.0/lexinfo#conjunction": "Q11",
    "http://www.lexinfo.net/ontology/2.0/lexinfo#singular": "Q12",
    "http://www.lexinfo.net/ontology/2.0/lexinfo#plural": "Q13"
}

isolang_map = {
    "www.lexvo.org/page/iso639-3/kmr": "Q14"
}

wikilang_map = {
    "kmr-latn": "ku-latn",
    "en": "en"
}

g = Graph()
g.parse("kurdish/data/Kurmanji_new.ttl")

namespaces = {} # build the ns prefix object for rdflib sparql initNs
for ns_prefix, namespace in g.namespaces():
    namespaces[ns_prefix] = URIRef(namespace)

# dct:language <www.lexvo.org/page/iso639-3/kmr> ;
#  ontolex:writtenRep "gav"@kmr-latn ;
#  lexinfo:partOfSpeech lexinfo:noun ;
#  lexinfo:gender lexinfo:feminine ;

# get entry level information
entry_query = """
SELECT DISTINCT ?entryuri (lang(?lemma) as ?lemlang) ?lemma ?language ?gender (group_concat(?sense) as ?senses) (group_concat(?form) as ?forms) 
WHERE {
    ?entry a ontolex:LexicalEntry ; rdfs:label ?lemma ;
            dct:language ?language ;
            lexinfo:partOfSpeech ?pos . 
            optional { ?entryuri lexinfo:gender ?gender . }
            optional { ?entryuri ontolex:sense ?sense . }
            optional { ?entryuri ontolex:canonicalForm|ontolex:form ?form . }
} group by ?entryuri ?lemlang ?lemma ?language ?gender ?senses ?forms"""

entries = g.query(entry_query, initNs=namespaces)
entrycount = 0

for entry in entries:
    entrycount += 1
    entryuri = str(entry.entryuri)
    lemma = entry.lemma
    language = isolang_map[entry.language]
    pos = ontology_map[entry.pos]
    print(f'[{str(entrycount)}] Now processing entry with original URI {entryuri}, lemma {lemma}, pos {pos}.')
    if entryuri in lexeme_map:
        lexeme = kwbi.lexeme.get(entity_id=lexeme_map[entryuri])
    else:
        lexeme = kwbi.lexeme.new(language=language, lexical_category=pos)

    sensecount = 0
    for senseuri in entry.senses.split(' '):
        if not senseuri.startswith('http'):
            continue
        print('  Processing sense: '+senseuri)
        sensecount += 1
        # get sense level information
        sense_query = """
        SELECT DISTINCT ?senseuri
                        (group_concat(concat(?def,"@",lang(?def));SEPARATOR="|") as ?definitions)
                        (group_concat(concat(?usage,"@",lang(?usage));SEPARATOR="|") as ?usages)
        WHERE {
            BIND(<""" + senseuri + """> as ?senseuri)
            ?senseuri skos:definition ?def.
             optional { ?senseuri ontolex:usage [rdf:value ?usage] . }
        } group by ?senseuri ?lemma ?definitions"""

        senses = g.query(sense_query, initNs=namespaces)

        senseuri = senses[0].senseuri
        newsense = kwbi.Sense()
        newsense.claims.add(kwbi.URI(prop_nr='P11', value=senseuri))
        definitions = senses[0].definitions.split("|")
        for definition in definitions:
            deftext = definition.split('@')[0]
            deflang = definition.split('@')[1]
            newsense.glosses.set(language=wikilang_map[deflang], value=deftext)
        for usage in usages:
            usgtext = usage.split('@')[0]
            usglang = usage.split('@')[1]
            newsense.claims.add(kwbi.MonolingualText(prop_nr="P12", language=wikilang_map[usglang], value=usgtext))
    print(f'    Added {str(sensecount)} senses to the lexeme.')

    formcount = 0
    for formuri in entry.forms.split(' '):
        if not formuri.startswith('http'):
            continue
        print('  Processing form: '+formuri)
        formcount += 1
        # get form level information
        form_query = """
          SELECT DISTINCT ?formuri (lang(?wrep) as ?wreplang) ?number ?gender WHERE {
          BIND(<""" + formuri + """> as ?formuri)
             ?formuri ontolex:writtenRep ?wrep.
             optional { ?formuri lexinfo:number ?number . }
             optional { ?formuri lexinfo:gender ?gender . }
             # case, etc. should go here
          } group by ?formuri ?wreplang ?number ?gender"""

        forms = g.query(form_query, initNs=namespaces)

        formuri = forms[0].formuri
        grammatical_features = []
        if form.number.startswith('http'):
            grammatical_features.append(ontology_map[forms[0].number])
        if form.gender.startswith('http'):
            grammatical_features.append(ontology_map[forms[0].gender])
        newform = kwbi.Form()
        newform.grammatical_features = grammatical_features
        newform.representations.set(language=wikilang_map[form.wreplang], value=forms[0].wrep) # we assume here cardinality 1 for ontolex:writtenRep
        newform.claims.add(kwbi.URI(prop_nr='P11', value=formuri))
        lexeme.forms.add(newform)
    print(f'    Added {str(formcount)} forms to the lexeme.')



    done = False
    while not done:
        try:
            lexeme.write()
            done = True
        except Exception as ex:
            if "404 Client Error" in str(ex):
                print('Got 404 response from wikibase, will wait and try again...')
                time.sleep(10)
            else:
                print('Unexpected error:\n' + str(ex))
                sys.exit()

    with open('data/lexeme-mapping.csv', 'a') as mappingcsv:
        mappingcsv.write(entryuri + '\t' + lexeme.id + '\n')
    print('Finished processing ' + lexeme.id)
