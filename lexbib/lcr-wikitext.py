import lwbi, lwb, zoterobot, config, json

lcr_skipprops = ['P55', 'P75', 'P177']
lex_works = ['Q16236', "Q33598"]
lex_works_values = ""
for lex_work in lex_works:
	lex_works_values += 'lwb:'+lex_work+' '
print(lex_works_values)
query = """select distinct ?work ?workLabel (group_concat(distinct ?zot_about_work) as ?zot_subj_work) ?wikipage ?lcr ?dist ?dist_zot (group_concat(distinct ?zot_about_dist) as ?zot_subj_dist) ?bibtypeLabel where {
  values ?work { """+lex_works_values+"""}
  ?work ldp:P118 ?lcr.
  optional {?work ldp:P75/ldp:P16 ?zot_about_work.}
  optional {?work ldp:P165 ?wikipage.}
  ?lcr ldp:P55 ?dist.
  ?dist ldp:P91 ?bibtype .
  optional {?dist ldp:P16 ?dist_zot.}
  optional {?dist ldp:P75/ldp:P16 ?zot_about_dist.}
SERVICE wikibase:label { bd:serviceParam wikibase:language "eu,en". }}
group by ?work ?workLabel ?zot_subj_work ?wikipage ?lcr ?dist ?dist_zot ?zot_subj_dist ?bibtypeLabel
order by ?work ?lcr ?dist"""

print(query)
r = lwbi.wbi_helpers.execute_sparql_query(query, prefix=config.lwb_prefixes)

output = {}
work = None
lcr = None
dist = None
for row in r['results']['bindings']:
	#print(str(row))
	if row['work']['value'] != work: # new work
		lcrcount = 0
		work = row['work']['value']
		workid = work.replace(config.entity_ns,'')
		wikipage = row['wikipage']['value']
		print(f'\nWill process work {workid}...')
		output[wikipage] = "= " + row['workLabel']['value'] + " =\n\n"

		# +" =\n\nHemen WORK informazioa.\n\n"

		if len(row['zot_subj_work']['value']) > 1:
			output[wikipage] += "Proiektu lexikografiko honi buruzkoak:\n"
			for zotid in row['zot_subj_work']['value'].split(' '):
				output[wikipage] += "* "+zoterobot.getcitation(zotid)+"\n"

	if row['lcr']['value'] != lcr: # new lcr
		lcrcount += 1
		lcr = row['lcr']['value']
		lcrid = lcr.replace(config.entity_ns,'')
		print(f'\nWill process lcr {lcrid}...')

		#get lcr info
		lcr_info = ""
		query = """select ?lcr (group_concat(distinct ?zot_about_lcr) as ?zot_subj_lcr) ?prop ?propLabel ?range (strafter(str(?type), "http://wikiba.se/ontology#") as ?proptype) ?value ?valueLabel where {
				  bind(lwb:"""+lcrid+""" as ?lcr)
                  {?prop ldp:P168 lwb:Q4. # props with domain LCR
                   optional {?prop ldp:P48 ?range. filter(?range = lwb:Q4)}
				  ?prop wikibase:directClaim ?p; wikibase:propertyType ?type.
				  ?lcr ?p ?value.
				  
				  } union # for source and target language info
                  {?prop ldp:P168 lwb:Q4.
                   ?prop wikibase:qualifier ?quali; wikibase:propertyType ?type.
                   ?lcr lp:P115 [?quali ?value].}
                   optional {?lcr ldp:P75/ldp:P16 ?zot_about_lcr.}
                  SERVICE wikibase:label { bd:serviceParam wikibase:language "eu,en". }
				  } group by ?lcr ?zot_subj_lcr ?prop ?propLabel ?range ?type ?value ?valueLabel 
				  order by ?lcr ?range"""
		#print(query)
		r2 = lwbi.wbi_helpers.execute_sparql_query(query, prefix=config.lwb_prefixes)
		#print(str(r2))
		about_lcr = ""
		for proprow in r2['results']['bindings']:
			if not about_lcr and len(proprow['zot_subj_lcr']['value']) > 1:
				about_lcr = "\nBertsio honi buruzkoak:\n"
				for zotid in proprow['zot_subj_lcr']['value'].split(' '):
					about_lcr += f"* {zoterobot.getcitation(zotid)}\n"
			if proprow['prop']['value'].replace(config.entity_ns,'') not in lcr_skipprops:
				if 'range' in proprow: # points to another LCR
					targetlcr = proprow['value']['value'].replace(config.entity_ns,'')
					propval = f"[[Item:{targetlcr}|{targetlcr}]]"
				elif proprow['proptype']['value'] == "WikibaseItem":
					propval = f"[[Item:{proprow['value']['value'].replace(config.entity_ns,'')}|{proprow['valueLabel']['value']}]]"
				else:
					propval = proprow['value']['value']
				lcr_info += f"* {proprow['propLabel']['value']}: {propval}\n"

		if len(row['zot_subj_dist']['value']) > 1:
			output[wikipage] += "\nBertsio honi buruzkoak:\n"
			for zotid in row['zot_subj_dist']['value'].split(' '):
				about_lcr += "* " + zoterobot.getcitation(zotid) + "\n"

		output[wikipage] += f"\n=={str(lcrcount)}. bertsioa ([[Item:{lcrid}|{lcrid}]])==\n\n{lcr_info}{about_lcr}\nBertsio honen argitalpena(k):\n"
	dist = row['dist']['value']
	distid = dist.replace(config.entity_ns,'')
	if 'dist_zot' in row:
		citation = zoterobot.getcitation(row['dist_zot']['value'])#.replace(config.entity_ns+distid,'')
		output[wikipage] += f"* ({row['bibtypeLabel']['value']}:) {citation}\n"
	else:
		output[wikipage] += f"* {row['bibtypeLabel']['value']}: Ikus [[Item:{distid}|{distid}]].\n"



with open('data/testout.json', 'w', encoding='utf-8') as outfile:
	json.dump(output, outfile)
with open('data/testout.txt', 'w', encoding='utf-8') as outfile:
	outfile.write(output[wikipage])

input('\nTest output files written. Press return to proceed writing wikipages.')

for pagetitle in output:
	pagecreation = lwb.site.post('edit', token=lwb.token, contentformat='text/x-wiki', contentmodel='wikitext', bot=True, recreate=True, summary="recreate wiki page using lcr-wikitext.py", title=pagetitle, text=output[pagetitle])
	print(str(pagecreation))