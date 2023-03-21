from rdflib import Graph, URIRef
import kwbi, time, sys # kwbi is the customized wikibaseIntegrator 12.0 engine

# load existing lexemes lookup table
with open('data/lexeme-mapping.csv') as mappingcsv:
	mappingrows = mappingcsv.read().split('\n')
	lexeme_map = {}
	for row in mappingrows:
		print(row)
		mapping = row.split('\t')
		if len(mapping) == 2:
			lexeme_map[mapping[0]] = mapping[1]
print(f'Loaded {str(len(lexeme_map))} existing lexeme mappings.')

# maps source TTL object property value to kurdi.wikibase item
ontology_map = {
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#noun>": "Q6",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#verb>": "Q7",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#adjective>": "Q8",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#adverb>": "Q9",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#preposition>": "Q10",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#conjunction>": "Q11",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#interjection>": "Q24",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#numeral>": "Q25",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#pronoun>": "Q26",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#singular>": "Q12",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#plural>": "Q13",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#feminine>": "Q22",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#masculine>": "Q23",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#circumposition>": "Q27",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#interrogativeParticle>": "Q28",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#cliticness>": "Q29",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#superlative>": "Q30",
	"<http://www.lexinfo.net/ontology/2.0/lexinfo#particle>": "Q31"
}

# maps lexvo language uri to kurdi.wikibase language item
isolang_map = {
	"<http://www.lexvo.org/page/iso639-3/kmr>": "Q14",
	"<http://www.lexvo.org/page/iso639-3/sdh>": "Q33",
}

# maps TTL langstring language to wikilanguage. While proper Kurdish variety language code is not implemented, we use ku-latn / ku-arab for all Kurdish varieties here
wikilang_map = {
	"kmr-latn": "ku-latn",
	"sdh-latn": "ku-latn",
	"sdh-arab": "ku-arab",
	"ku-arab": "ku-arab",
	"fa": "fa",
	"en": "en"
}
ttlfile = "data/Southern_Kurdish_new.ttl"
dictitem = "Q32"


g = Graph()
g.parse(ttlfile)
print('TTL loaded.')
namespaces = {} # build the ns prefix object for rdflib sparql initNs
for ns_prefix, namespace in g.namespaces():
	namespaces[ns_prefix] = URIRef(namespace)

# get entry level information
entry_query = """
SELECT DISTINCT ?entryuri (lang(?lemma) as ?lemlang) (group_concat(distinct concat(?lemma,"@",lang(?lemma));SEPARATOR="|") as ?lemmas) ?pos ?language ?gender 
				(group_concat(distinct ?sense) as ?senses) #(group_concat(distinct ?form) as ?forms) 
WHERE {
	?entryuri a ontolex:LexicalEntry ; rdfs:label ?lemma ;
			dct:language ?language .
			optional { ?entryuri lexinfo:partOfSpeech ?pos .} 
			optional { ?entryuri lexinfo:gender ?gender . }
			optional { ?entryuri ontolex:sense ?sense . }
		#	optional { ?entryuri ontolex:canonicalForm|ontolex:form ?form . }
} group by ?entryuri ?lemmas ?pos ?language ?gender ?senses #?forms
"""
print('Getting entries info with sparql...')
entries = g.query(entry_query, initNs=namespaces)
entrycount = 0

for entry in entries:
	entrycount += 1
	entryuri = str(entry.entryuri)
	lemmas = str(entry.lemmas)
	language = isolang_map[entry.language.n3()]
	if entry.pos:
		pos = ontology_map[entry.pos.n3()]
	else:
		pos = "Q19"
	print(f'\n[{str(entrycount)}] Now processing entry with original URI {entryuri}: lemmagroup {lemmas}, pos {pos}.')

	if entryuri in lexeme_map:
		continue
		lexeme = kwbi.wbi.lexeme.get(entity_id=lexeme_map[entryuri])
		print('Found this lexeme on wikibase: ' + lexeme.id)
		# print(str(lexeme.get_json()))
	else:
		time.sleep(0.2)
		lexeme = kwbi.wbi.lexeme.new(language=language, lexical_category=pos)
	for lem_lang in lemmas.split('|'):
		lem_lang_split = lem_lang.split('@')
		lemlang = wikilang_map[lem_lang_split[1]]
		lemtext = lem_lang_split[0]
		lexeme.lemmas.set(language=lemlang , value=lemtext)
	lexeme.claims.add(kwbi.URL(prop_nr='P11', value=str(entryuri)))
	lexeme.claims.add(kwbi.Item(prop_nr='P10', value=dictitem))
	if entry.gender:
		lexeme.claims.add(kwbi.Item(prop_nr='P13', value=ontology_map[entry.gender.n3()]))

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
		for sense in senses:
			newsense = kwbi.Sense()
			newsense.claims.add(kwbi.URL(prop_nr='P11', value=senseuri))
			definitions = str(sense.definitions).split("|")
			print('Senseglosses: '+str(definitions))
			for definition in definitions:
				defsplit = definition.split('@')
				if len(defsplit) == 2:
					deftext = defsplit[0]
					deflang = defsplit[1]
				newsense.glosses.set(language=wikilang_map[deflang], value=deftext)
			usages = str(sense.usages).split('|')
			for usage in usages:
				usgsplit = usage.split('@')
				if len(usgsplit) == 2:
					print('Usageexample: ' + str(usage))
					usgtext = usgsplit[0]
					usglang = wikilang_map[usgsplit[1]]
					variety = usgsplit[1]
					if variety != usglang: # this is because we have to stick to ku-latn/ku-arab langauge codes for all varieties
						qualifiers = kwbi.Qualifiers()
						qualifiers.add(kwbi.String(prop_nr='P14', value=variety))
					else:
						qualifiers = []
					newsense.claims.add([kwbi.MonolingualText(prop_nr="P12", language=usglang, text=usgtext, qualifiers=qualifiers)], action_if_exists=kwbi.ActionIfExists.FORCE_APPEND)
			lexeme.senses.add(newsense)
	print(f'    Added {str(sensecount)} senses to the lexeme.')

	# formcount = 0
	#
	# for formuri in entry.forms.split(' '):
	# 	if not formuri.startswith('http'):
	# 		continue
	# 	print('  Processing form: '+formuri)
	# 	formcount += 1
	# 	# get form level information
	# 	form_query = """
	# 	  SELECT DISTINCT ?formuri (lang(?wrep) as ?wreplang) ?wrep ?number ?gender WHERE {
	# 	  BIND(<""" + formuri + """> as ?formuri)
	# 		 ?formuri ontolex:writtenRep ?wrep.
	# 		 optional { ?formuri lexinfo:number ?number . }
	# 		 optional { ?formuri lexinfo:gender ?gender . }
	# 		 # case, etc. should go here
	# 	  } group by ?formuri ?wreplang ?wrep ?number ?gender"""
	#
	# 	forms = g.query(form_query, initNs=namespaces)
	# 	for form in forms:
	# 		grammatical_features = []
	# 		if form.number:
	# 			grammatical_features.append(ontology_map[form.number.n3()])
	# 		if form.gender:
	# 			grammatical_features.append(ontology_map[form.gender.n3()])
	# 		newform = kwbi.Form()
	# 		newform.grammatical_features = grammatical_features
	# 		newform.representations.set(language=wikilang_map[str(form.wreplang)], value=str(form.wrep)) # we assume here cardinality 1 for ontolex:writtenRep
	# 		newform.claims.add(kwbi.URL(prop_nr='P11', value=formuri))
	# 		lexeme.forms.add(newform)
	# print(f'    Added {str(formcount)} forms to the lexeme.')
	#


	done = False
	while not done:
		try:
			# print(str(lexeme.get_json()))
			lexeme.write(is_bot=True)
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

