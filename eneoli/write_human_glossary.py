import csv, time, sys, json, xwbi, re

import mwclient, config_private

site = mwclient.Site("eneoli.wikibase.cloud")
def get_token():
	global site

	# lwb login via mwclient
	while True:
		try:
			login = site.login(username=config_private.wb_bot_user, password=config_private.wb_bot_pwd)
			break
		except Exception as ex:
			print('lwb login via mwclient raised error: '+str(ex))
			time.sleep(60)
	# get token
	csrfquery = site.api('query', meta='tokens')
	token = csrfquery['query']['tokens']['csrftoken']
	print("Got fresh CSRF token for eneoli wikibase.")
	return token
token = get_token()

query = """#title: Export for Task 1.4

PREFIX enwb: <https://eneoli.wikibase.cloud/entity/>
PREFIX endp: <https://eneoli.wikibase.cloud/prop/direct/>
PREFIX enp: <https://eneoli.wikibase.cloud/prop/>
PREFIX enps: <https://eneoli.wikibase.cloud/prop/statement/>
PREFIX enpq: <https://eneoli.wikibase.cloud/prop/qualifier/>

select (strafter(str(?concept),str(enwb:)) as ?concept_id) ?concept_label ?wd 
(group_concat(distinct concat(strafter(str(?broad),str(enwb:)),"@",str(?broad_label));SEPARATOR="|") as ?broaders) 
(group_concat(distinct concat(strafter(str(?narrow),str(enwb:)),"@",str(?narrow_label));SEPARATOR="|") as ?narrowers) 
(group_concat(distinct concat(strafter(str(?result),str(enwb:)),"@",str(?result_label));SEPARATOR="|") as ?results) 
(group_concat(distinct concat(strafter(str(?process),str(enwb:)),"@",str(?process_label));SEPARATOR="|") as ?processes) 
?language_name ?language_code ?long_def 
(group_concat(distinct strafter(str(?def_source),str(enwb:));SEPARATOR="|") as ?def_sources)
?gloss ?lemma (strafter(str(?term_sense),str(enwb:)) as ?sense_id) ?pos
(group_concat(distinct concat(str(YEAR(?date)),"@",strafter(str(?bib_item),str(enwb:)),"@",str(?bib_desc),"@",?bib_title,"@",?freq);SEPARATOR="|") as ?attestations) 
(group_concat(distinct concat(strafter(str(?homograph_sense),str(enwb:)),"@",str(?homograph_gloss));SEPARATOR="|") as ?homographs)

where { values ?concept {enwb:Q1308 enwb:Q1083}
  ?concept endp:P82 enwb:Q12; rdfs:label ?concept_label. filter(lang(?concept_label)="en") # part of NeoVoc collection
  optional {?concept endp:P1 ?wd.}
  optional {?concept endp:P4 ?broad. ?broad rdfs:label ?broad_label. filter(lang(?broad_label)="en")}
  optional {?narrow endp:P4 ?concept. ?narrow rdfs:label ?narrow_label. filter(lang(?narrow_label)="en")}
  optional {?concept endp:P69 ?result. ?result rdfs:label ?result_label. filter(lang(?result_label)="en")}
  optional {?process endp:P69 ?concept. ?process rdfs:label ?process_label. filter(lang(?process_label)="en")}
  ?term_sense endp:P12 ?concept.
  ?term ontolex:sense ?term_sense; dct:language [rdfs:label ?language_name]. filter(lang(?language_name)="en")
  ?term wikibase:lemma ?lemma; wikibase:lexicalCategory [rdfs:label ?pos]. filter(lang(?pos)="en") bind(lang(?lemma) as ?language_code)
  optional {?bib_item endp:P30 ?date; enp:P65 [enps:P65 ?term; enpq:P66 ?freq]; endp:P55 ?bib_title; schema:description ?bib_desc. filter(lang(?bib_desc)="en")}
  optional {?term ontolex:sense ?homograph_sense. filter(?homograph_sense != ?term_sense). ?homograph_sense skos:definition ?homograph_gloss. filter(lang(?homograph_gloss)=?language_code)}
  optional {?concept schema:description ?gloss. filter(lang(?gloss)=?language_code)}
  optional {?concept enp:P101 ?def_st. ?def_st enps:P101 ?long_def. filter(lang(?long_def)=?language_code)
            optional {?def_st enpq:P102 ?def_source.}
            }
    
} group by ?concept ?concept_label ?wd ?broaders ?narrowers ?results ?processes ?language_name ?language_code ?long_def ?def_sources ?gloss ?lemma ?term_sense ?pos ?attestations ?homographs
 order by ?concept_id ?language_code
  """

bindings = \
xwbi.wbi_helpers.execute_sparql_query(query=query, user_agent="User:DavidL python script wikibaseintegrator")[
    'results']['bindings']
print('Found ' + str(len(bindings)) + ' result bindings.\n')
time.sleep(1)
count = 0
active_concept = False
active_language = False
entrytext = ""
concepts_text = {}
for binding in bindings:
    count += 1
    if binding['concept_id']['value'] != active_concept:
        active_concept = binding['concept_id']['value']
        print(f"[{count}] Now processing concept {active_concept}")

        entrytext = f"=Concept entry [[Item:{active_concept}]{active_concept}]] '{binding['concept_label']['value']}'="
        if 'broaders' in binding:
            for broad_group in binding['broaders']['value'].split('|'):
                broad_pair = broad_group.split('@')
                entrytext += f"\n* Broader concept: [[Item:{broad_pair[0]}|{broad_pair[1]}]]."
        if 'narrowers' in binding:
            for narrow_group in binding['narrowers']['value'].split('|'):
                narrow_pair = narrow_group.split('@')
                entrytext += f"\n* Narrower concept: [[Item:{narrow_pair[0]}|{narrow_pair[1]}]]."
        if 'results' in binding:
            entrytext += "\nThis concept describes a lexical innovation process type."
            for result_group in binding['results']['value'].split('|'):
                result_pair = result_group.split('@')
                entrytext += f"\n* Corresponding neologism type: [[Item:{result_pair[0]}|{result_pair[1]}]]."
        if 'processes' in binding:
            entrytext += "\nThis concept describes a type of neologism."
            for process_group in binding['processes']['value'].split('|'):
                process_pair = process_group.split('@')
                entrytext += f"\n* Corresponding lexical innovation process type: [[Item:{process_pair[0]}|{process_pair[1]}]]."
        active_language = False
    if active_language != binding['language_code']['value']:
        active_language = binding['language_code']['value']
        entrytext += f"\n=={binding['language_name']['value']}=="
        if 'long_def' in binding:
            entrytext += f"\n* Definition: ''{binding['long_def']['value']}''"
            for source in binding['def_sources']['value'].split("|"):
                if source.startswith("Q"):
                    entrytext += f"\n** Source: [[Item:{source}|{source}]."
        if 'gloss' in binding:
            entrytext += f"\n* Gloss: {binding['gloss']['value']}"

        lemma = binding['lemma']['value']
        sense_id = binding['sense_id']['value']
        sense_url = f"Lexeme:{re.sub(r'\-','#', sense_id)}"
        entrytext += f"\n== ''[[{sense_url}|{lemma}]]'' =="
        entrytext += f"\n* lexical category: ''{binding['pos']['value']}''"

        if 'homographs' in binding:
            for hom_group in binding['homographs']['value'].split('|'):
                hom_pair = hom_group.split('@')
                sense_url = f"Lexeme:{re.sub(r'\-', '#', hom_pair[0])}"
                entrytext += f"\n* Homograph term: [[{sense_url}|{lemma}]]: ''{hom_pair[1]}''"

        if 'attestations' not in binding:
            continue
        attestations = {}
        for att in binding['attestations']['value'].split("|"):
            att_group = att.split("@")
            attestations[int(att_group[0])] = f"\n* [[Item:{att_group[1]}|{att_group[2].replace("Publication by ","")}]]: ''{att_group[3]}'' <small>({att_group[4]} occurrences)</small>"
        attestations = dict(sorted(attestations.items()))
        entrytext += f"\n=== Attestations since {next(iter(attestations))} ==="
        if 'homographs' in binding:
            entrytext += "Attestations may apply to any of the homograph terms."
        for year, text in attestations.items():
            entrytext += text


    entrytext += "This page was created [https://github.automatically] ~~~~"

    concepts_text[active_concept] = entrytext

    pagecreation = site.post('edit', token=token, contentformat='text/x-wiki', contentmodel='wikitext',
                             bot=True, recreate=True,
                             summary=f"recreate wiki page for NeoVoc concept {active_concept} using write_human_glossary.py",
                             title=f"NeoVoc/concepts/{active_concept}", text=entrytext)
    print(str(pagecreation))
    time.sleep(0.5)

with open('data/concepts_text.json', 'w') as outfile:
    json.dump(concepts_text, outfile)


