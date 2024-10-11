import csv, time, sys, json, xwbi
from langconv.converter import LanguageConverter
from langconv.language.zh import zh_cn
lc_cn = LanguageConverter.from_language(zh_cn)

# get ENEOLI working languages

with open('data/languages_table.csv') as csvfile:
	language_table = csv.DictReader(csvfile, delimiter=",")
	#language_name,iso-639-1,iso-639-3,wiki_languagecode,wikibase_item,wikidata_item
	working_wikilangs = []
	wikilangs_to_write = []
	for row in language_table:
		working_wikilangs.append(row['wiki_languagecode'].split("-")[0])
		wikilangs_to_write.append(row['wiki_languagecode'])
	print(f"Working languages: {working_wikilangs}")

# get ENEOLI concepts

query = """PREFIX enwb: <https://eneoli.wikibase.cloud/entity/>
PREFIX endp: <https://eneoli.wikibase.cloud/prop/direct/>

select ?concept (group_concat(distinct ?equiv_lang) as ?existing_equivlangs) (group_concat(distinct ?desc_lang) as ?existing_desclangs) ?wd ?wd_labels ?wd_descs
where { 
  ?concept endp:P5 enwb:Q12. # instances of "NeoVoc Concept"
  ?concept endp:P1 ?wd. bind (iri(concat(str(wd:),?wd)) as ?wikidata)
  optional {?concept endp:P57 ?equiv. bind(lang(?equiv) as ?equiv_lang)}
  optional {?concept schema:description ?desc. bind(lang(?desc) as ?desc_lang)}
  SERVICE <https://query.wikidata.org/sparql> {
		   select ?wikidata (group_concat(concat('{"lang":"',?wd_label_lang,'", "value":"',?wd_label,'"}'); SEPARATOR = ', ') as ?wd_labels)
				  where { ?wikidata rdfs:label ?wd_lab. bind(lang(?wd_lab) as ?wd_label_lang) bind(replace(?wd_lab,'"',"'") as ?wd_label)
						 } group by ?wikidata ?wd_labels }
  SERVICE <https://query.wikidata.org/sparql> {
		   select ?wikidata (group_concat(concat('{"lang":"',?wd_desc_lang,'", "value":"',?wd_desc,'"}'); SEPARATOR = ', ') as ?wd_descs)
				  where { ?wikidata schema:description ?wd_des. bind(lang(?wd_des) as ?wd_desc_lang) bind(replace(?wd_des,'"',"'") as ?wd_desc)
						 } group by ?wikidata ?wd_descs }
} group by ?concept ?existing_equivlangs ?existing_desclangs ?wd ?wd_labels ?wd_descs
  
  
  """

bindings = xwbi.wbi_helpers.execute_sparql_query(query=query)['results']['bindings']
print('Found ' + str(len(bindings)) + ' results for the query for ENEOLI concepts aligned to Wikidata.\n')
time.sleep(1)
count = 0
for binding in bindings:
	count += 1
	concept_changes = False
	wb_concept = binding['concept']['value'].replace('https://eneoli.wikibase.cloud/entity/','')
	wd_concept = binding['wd']['value']
	print(f"\n[{count}] Now processing Wikibase concept {binding['concept']['value']} (Wikidata {wd_concept})...")
	existing_equivlangs = binding['existing_equivlangs']['value'].split(' ')
	if "zh-hans" in existing_equivlangs:
		existing_equivlangs.append("zh")
	existing_desclangs = binding['existing_desclangs']['value'].split(' ')
	if "zh-hans" in existing_desclangs:
		existing_desclangs.append("zh")

	statements = []
	labels = []
	wd_labels = json.loads("["+binding['wd_labels']['value']+"]")
	zh_hans = False
	for wd_label in wd_labels:

		macrolang = wd_label['lang'].split("-")[0]
		if macrolang in working_wikilangs and macrolang not in existing_equivlangs and not zh_hans:
			concept_changes = True

			if wd_label['lang'] == "zh":
				zh_hans_label = lc_cn.convert(wd_label['value'])
				print(f'Transformed to zh-hans: "{zh_hans_label}"@zh-hans')
				wd_label['value'] = zh_hans_label
				wd_label['lang'] = 'zh-hans'
				zh_hans = True
			if wd_label['lang'] in wikilangs_to_write:
				print(f'Found a new equivalent to draft: "{wd_label['value']}"@{wd_label['lang']}')
				statements.append({'type': 'monolingualtext','prop_nr': 'P57', 'value': wd_label['value'], 'lang': wd_label['lang'], 'qualifiers': [{'prop_nr':'P58', 'value': 'from Wikidata', 'type': 'string'}]})
				labels.append({'value': wd_label['value'], 'lang': wd_label['lang']})

	descriptions = []
	wd_descs = json.loads("["+binding['wd_descs']['value']+"]")
	zh_hans = False
	for wd_desc in wd_descs:

		macrolang = wd_desc['lang'].split("-")[0]
		if macrolang in working_wikilangs and macrolang not in existing_desclangs and not zh_hans:
			concept_changes = True

			if wd_desc['lang'] == "zh":
				zh_hans = True
				zh_hans_desc = lc_cn.convert(wd_desc['value'])
				descriptions.append({'value': zh_hans_desc, 'lang': 'zh-hans'})
				print(f'Transformed to zh-hans: "{zh_hans_desc}"@zh-hans')
				wd_desc['value'] = zh_hans_desc
				wd_desc['lang'] = 'zh-hans'
			if wd_desc['lang'] in wikilangs_to_write:
				print(f'Found a new description to draft: "{wd_desc['value']}"@{wd_desc['lang']}')
				descriptions.append({'value': wd_desc['value'], 'lang': wd_desc['lang']})


	if concept_changes:
		xwbi.itemwrite({'qid': wb_concept, 'statements': statements, 'labels': labels, 'descriptions': descriptions})
        time.sleep(1)




