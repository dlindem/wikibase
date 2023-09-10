import time
import re
import json
import csv
import sparql
import lwb
import lwbi
import config
import zoterobot

def inverseprops(props=None): # props is a list of pairs (each pair in a list). if no list is passes, all props with inverseprop relation set are processed.
	if not props:
		query = """select ?prop ?inverse where 
				   {?prop ldp:"""+config.inverse_prop_relation+""" ?inverse.}"""
		r = lwbi.wbi_helpers.execute_sparql_query(query, prefix=config.lwb_prefixes)
		props = []
		print(f"\nFound {str(len(r['results']['bindings']))} inverse property pairs.\n")
		for binding in r['results']['bindings']:
			props.append([binding['prop']['value'].replace(config.entity_ns, ''),
								   binding['inverse']['value'].replace(config.entity_ns, '')])
		print(str(props))

		input('\nPress return for starting to write missing inverse relations...\n')

	for pair in props:
		print("Will now process inverted properties ", str(pair))

		print(
			f'(1) get items with {pair[0]} set; where an inverse {pair[1]} relation is not present, will add that...\n')
		query = """select distinct ?n ?b 
	    where {
	     ?n ldp:""" + pair[0] + """ ?b.
	     filter not exists { ?b ldp:""" + pair[1] + """ ?n . }
	      }
	    """
		# print(query)
		print("Waiting for SPARQL...")
		bindings = lwbi.wbi_helpers.execute_sparql_query(query=query, prefix=lwbi.sparql_prefixes)['results']['bindings']
		print('Found ' + str(len(bindings)) + ' results to process.\n')
		count = 0
		for item in bindings:
			count += 1
			print('\nNow processing item [' + str(count) + ']...')
			print(str(item))
			source_uri = item['n']['value'].replace(config.entity_ns, "")
			target_uri = item['b']['value'].replace(config.entity_ns, "")
			if source_uri.startswith('Q') and target_uri.startswith('Q'):
				print(f'Inverting relation: {source_uri} {pair[0]} {target_uri} {pair[1]} {source_uri}')
				lwb.updateclaim(target_uri, pair[1], source_uri, "item")

def qualip55():
	print('\nWill get LCR with P55-links without P126-year-of-pub qualifier, and years of the dists linked to them; same for disttype/bibtype.')

	query = """
	select ?lcr ?dist_statement ?dist (YEAR(?pubdate) as ?year) ?disttype ?bibtype where
	{?lcr lp:P55 ?dist_statement. ?dist_statement lps:P55 ?dist .
	 filter not exists {?dist_statement lpq:P126 ?existing .}
	 ?dist ldp:P15 ?pubdate.
	 optional {?dist ldp:P91 ?disttype.}
	 optional {?dist ldp:P100 ?bibtype.}
	 }
	 """
	print("Waiting for SPARQL...")
	bindings = lwbi.wbi_helpers.execute_sparql_query(query=query, prefix=lwbi.sparql_prefixes)['results']['bindings']
	print('Found ' + str(len(bindings)) + ' results to process.\n')
	count = 0
	for item in bindings:
		count += 1
		lcr = item['lcr']['value'].replace('https://lexbib.elex.is/entity/', '')
		print('\nWill process item ' + str(count) + ': ' + lcr)
		statement = item['dist_statement']['value'].replace('https://lexbib.elex.is/entity/statement/', '')
		year = item['year']['value']
		if lwb.setqualifier(lcr, 'P55', statement, 'P126', year, 'string'):
			print('Success writing pubyear ' + year + ' for item ' + str(count))
		disttype = None
		if 'disttype' in item:
			disttype = item['disttype']['value'].replace('https://lexbib.elex.is/entity/', '')
		elif 'bibtype' in item:
			disttype = item['bibtype']['value'].replace('https://lexbib.elex.is/entity/', '')
		if disttype:
			if lwb.setqualifier(lcr, 'P55', statement, 'P91', disttype, 'item'):
				print('Success writing disttype for item ' + str(count))

def lcrfromdicts():
	mapping_cache = {}

	print('\nWill get dictionary distributions with no existing P55 link pointing to them.')

	query = """
	select ?uri (str(?label) as ?title) ?lcr ?codist ?codistlcr where
	{?uri ldp:P5 lwb:Q24; rdfs:label ?label. filter(lang(?label)="en") # Q24: Dictionary Distribution
	 filter not exists { ?lcr ldp:P55 ?uri .}
	 OPTIONAL { ?uri ldp:P180 ?codist . optional {?codistlcr ldp:P55 ?codist.}}
	 } group by ?uri ?label ?lcr ?codist ?codistlcr order by ?codist
	"""
	print("Waiting for SPARQL...")
	bindings = lwbi.wbi_helpers.execute_sparql_query(query=query, prefix=lwbi.sparql_prefixes)['results']['bindings']
	print('Found ' + str(len(bindings)) + ' results to process.\n')
	count = 0
	for item in bindings:
		count += 1
		distrqid = item['uri']['value'].replace('https://lexbib.elex.is/entity/', '')
		title = item['title']['value']

		if 'lcr' in item:
			lcrqid = item['lcr']['value'].replace('https://lexbib.elex.is/entity/', '')
			print('Found P55 link for this dictionary distribution. LCR is ' + lcrqid)
			mapping_cache[distrqid] = lcrqid
		else:
			print('No P55 link for ' + distrqid, title + ' dictionary distribution.')
			if 'codist' in item:
				codistqid = item['codist']['value'].replace('https://lexbib.elex.is/entity/', '')
				if 'codistlcr' in item:
					print('Co-distribution link was in the SPARQL result.')
					codistlcr = item['codistlcr']['value'].replace('https://lexbib.elex.is/entity/', '')
					codistlcr = lwbi.itemwrite({'qid': codistlcr,
												'statements': [{'prop_nr': 'P55', 'type': 'item', 'value': distrqid}]})
					mapping_cache[distrqid] = codistlcr
				elif codistqid in mapping_cache:
					print(
						'Found co-distribution link in mapping cache from this script run. Will set the same LCR as that: ' +
						mapping_cache[codistqid])
					codistlcr = lwbi.itemwrite({'qid': mapping_cache[codistqid],
												'statements': [{'prop_nr': 'P55', 'type': 'item', 'value': distrqid}]})
					mapping_cache[distrqid] = lcrqid
				else:
					print('Error: could not find lcr linked to ' + str(codistqid))
			else:
				print('Will proceed to create new LCR.')
				lcrqid = lwbi.itemwrite({'qid': False,
										 'labels': [{'lang': 'en', 'value': title}],
										 'descriptions': [{'lang': 'en', 'value': 'a lexical-conceptual resource'}],
										 'statements': [{'prop_nr': 'P5', 'type': 'item', 'value': 'Q4'},
														{'prop_nr': 'P55', 'type': 'item', 'value': distrqid}]})
				mapping_cache[distrqid] = lcrqid

	print('Finished. Written P55-links:\n' + str(mapping_cache))

def distdescriptions():
	print('\nWill get distributions with no description, and their years of publication..')

	query = """
	select ?dist (YEAR(?pubdate) as ?year) where
	{?dist ldp:P5 lwb:Q24; ldp:P15 ?pubdate. filter not exists {?dist schema:description ?desc.}}
	 """
	print("Waiting for LexBib v3 SPARQL...")
	bindings = lwbi.wbi_helpers.execute_sparql_query(query=query, prefix=lwbi.sparql_prefixes)['results']['bindings']
	print('Found ' + str(len(bindings)) + ' results to process.\n')
	count = 0
	for item in bindings:
		count += 1
		dist = item['dist']['value'].replace('https://lexbib.elex.is/entity/', '')
		year = item['year']['value']
		if lwb.setdescription(dist, 'en', f"LCR distribution ({year})"):
			print('Success for EN item ' + str(count))
		if lwb.setdescription(dist, 'eu', f"{year}-ko LCR argitalpena"):
			print('Success for EN item ' + str(count))

def lcrwikilist():
	print(f"\nWill get list of LCR with info to put in list.")

	query = """
	select ?period ?periodLabel ?work ?workLabel ?lcr ?lcrLabel 
	(group_concat(concat(strafter(str(?dist),"https://lexbib.elex.is/entity/"),"@",?distzot,"@",str(year(?distdate)))) as ?distinfo)
	(year(?date) as ?creationdate) where {
	 ?lcr ldp:P5 lwb:Q4; ldp:P183 ?period .
	  optional {?work ldp:P118 ?lcr.}
	  ?lcr ldp:P55 ?dist. ?dist ldp:P15 ?distdate; ldp:P16 ?distzot.
	  ?lcr ldp:P181 ?date.
	  SERVICE wikibase:label { bd:serviceParam wikibase:language "eu,en". }
	} group by ?period ?periodLabel ?work ?workLabel ?lcr ?lcrLabel ?distinfo ?date
	order by ?period desc(?work) ?creationdate
	 """
	print("Waiting for LexBib v3 SPARQL...")
	bindings = lwbi.wbi_helpers.execute_sparql_query(query=query, prefix=lwbi.sparql_prefixes)['results']['bindings']
	print('Found ' + str(len(bindings)) + ' results to process.\n')
	count = 0
	period = None
	workqid = None
	output = "=Baliabide guztiak aroka, edukien argitalpenekin=\n\n"
	for item in bindings:
		if item['periodLabel']['value'] + "k" != period:  # new period
			period = item['periodLabel']['value'] + "k"
			output += f"\n=={period}==\n\n"
		if 'work' in item:
			if item['work']['value'].replace("https://lexbib.elex.is/entity/", "") != workqid:  # new work
				workqid = item['work']['value'].replace("https://lexbib.elex.is/entity/", "")
				workLabel = item['workLabel']['value']
				output += f"\n* ''Hainbat bertsiotakoa:'' '''{workLabel}''' ([[Item:{workqid}|{workqid}]])"
			stars = "**"
		else:
			stars = "*"

		lcr = item['lcr']['value'].replace("https://lexbib.elex.is/entity/", "")
		lcrLabel = item['lcrLabel']['value']
		creationdate = item['creationdate']['value']
		output += f"\n{stars} '''{creationdate}''': {lcrLabel} ([[Item:{lcr}|{lcr}]])"
		distinfo = item['distinfo']['value'].split(" ")
		distlist_unsorted = []
		for distblock in distinfo:
			distdata = distblock.split('@')
			distlist_unsorted.append({'distqid': distdata[0], 'distzot': distdata[1], 'distyear': distdata[2]})
		distlist = sorted(distlist_unsorted, key=lambda d: d['distyear'])
		for dist in distlist:
			citation = zoterobot.getcitation(dist['distzot'])
			output += f"\n{stars}* {dist['distyear']}: {citation} [https://www.zotero.org/groups/1892855/lexbib/items/{dist['distzot']}/item-details Zotero]"

	pagecreation = lwb.site.post('edit', token=lwb.token, contentformat='text/x-wiki', contentmodel='wikitext',
								 bot=True, recreate=True, summary="recreate wiki page using lcr-list-wikitext.py",
								 title="Euskarazko_baliabide_lexikalen_zerrenda", text=output)
	print(str(pagecreation))

def lcrwikipage():
	lcr_skipprops = ['P55', 'P75', 'P177']
	# lex_works = ['Q16236', "Q33598"]
	# lex_works_values = ""
	# for lex_work in lex_works:
	# 	lex_works_values += 'lwb:'+lex_work+' '
	# print(lex_works_values)
	query = """select distinct ?work ?workLabel (group_concat(distinct ?zot_about_work) as ?zot_subj_work) ?wikipage 
	?lcr (year(?creationdate)as ?creationyear) (group_concat(distinct ?zot_about_lcr) as ?zot_subj_lcr)
	?dist ?dist_zot (group_concat(distinct ?zot_about_dist) as ?zot_subj_dist) ?bibtypeLabel ?pubyear where {
      # values ?work {lwb:Q16236} # test work Larramendi
	  ?work ldp:P118 ?lcr.
 	   optional {?work ldp:P75/ldp:P16 ?zot_about_work.}
	   ?work ldp:P165 ?wikipage. 
	  ?lcr lp:P55 ?diststatement.
	  ?diststatement lpq:P91 ?bibtype .
      optional {?diststatement lpq:P126 ?pubyear. }
	  optional {?diststatement lps:P55 ?dist.}
      optional {?lcr ldp:P75/ldp:P16 ?zot_about_lcr.}
	    optional {?dist ldp:P16 ?dist_zot.}
	     optional {?dist ldp:P75/ldp:P16 ?zot_about_dist.}
	  
	  optional {?lcr ldp:P181 ?creationdate.}
	  SERVICE wikibase:label { bd:serviceParam wikibase:language "eu,en". }}
	group by ?work ?workLabel ?zot_subj_work ?wikipage 
	?lcr ?creationdate ?zot_subj_lcr
	?dist ?dist_zot ?zot_subj_dist ?bibtypeLabel ?pubyear
	order by ?work ?lcr ?dist  """

	print(query)
	r = lwbi.wbi_helpers.execute_sparql_query(query, prefix=config.lwb_prefixes)

	output = {}
	work = None
	lcr = None
	dist = None
	for row in r['results']['bindings']:
		print(str(row))
		if row['work']['value'] != work:  # new work
			lcrcount = 0
			work = row['work']['value']
			workid = work.replace(config.entity_ns, '')
			wikipage = row['wikipage']['value']
			print(f'\nWill process work {workid}...')
			output[wikipage] = "= " + row['workLabel']['value'] + " =\n\n"
			output[
				wikipage] += f"Hiztegigintza proiektu hau [[Item:{workid}|{workid}]] entitateak deskribatzen du. Jarraian zerrendatutako bertsioak ditu.\n\n"
			# +" =\n\nHemen WORK informazioa.\n\n"

			if len(row['zot_subj_work']['value']) > 1:
				output[wikipage] += "Proiektu lexikografiko honi buruzkoak:\n"
				for zotid in row['zot_subj_work']['value'].split(' '):
					output[wikipage] += "* " + zoterobot.getcitation(zotid) + "\n"

		if row['lcr']['value'] != lcr:  # new lcr
			lcrcount += 1
			lcr = row['lcr']['value']
			lcrid = lcr.replace(config.entity_ns, '')
			print(f'\nWill process lcr {lcrid}...')

			# get lcr info
			lcr_info = ""
			query = """select ?lcr ?lcrLabel (group_concat(distinct ?zot_about_lcr) as ?zot_subj_lcr) ?prop ?propLabel ?range (strafter(str(?type), "http://wikiba.se/ontology#") as ?proptype) ?value ?valueLabel where {
					  bind(lwb:""" + lcrid + """ as ?lcr)
	                 { {?prop ldp:P168 lwb:Q4.} # props with domain LCR
	                  union
	                  {?prop ldp:P5 lwb:Q67.} # props of class creator role
	                   optional {?prop ldp:P48 ?range. filter(?range = lwb:Q4)}
					  ?prop wikibase:directClaim ?p; wikibase:propertyType ?type.
					  ?lcr ?p ?value.

					  } union # for source and target language info
	                  {?prop ldp:P168 lwb:Q4.
	                   ?prop wikibase:qualifier ?quali; wikibase:propertyType ?type.
	                   ?lcr lp:P115 [?quali ?value].}
	                   optional {?lcr ldp:P75/ldp:P16 ?zot_about_lcr.}

	                  SERVICE wikibase:label { bd:serviceParam wikibase:language "eu,en". }
					  } group by ?lcr ?lcrLabel ?zot_subj_lcr ?prop ?propLabel ?range ?type ?value ?valueLabel 
					  order by ?lcr ?range"""
			# print(query)
			r2 = lwbi.wbi_helpers.execute_sparql_query(query, prefix=config.lwb_prefixes)
			# print(str(r2))
			about_lcr = ""

			for proprow in r2['results']['bindings']:

				if not about_lcr and len(proprow['zot_subj_lcr']['value']) > 1:
					about_lcr = "\nBertsio honi buruzkoak:\n"
					for zotid in proprow['zot_subj_lcr']['value'].split(' '):
						about_lcr += f"* {zoterobot.getcitation(zotid)}\n"
				if proprow['prop']['value'].replace(config.entity_ns, '') not in lcr_skipprops:
					if 'range' in proprow:  # points to another LCR
						targetlcr = proprow['value']['value'].replace(config.entity_ns, '')
						propval = f"[[Item:{targetlcr}|{targetlcr}]]"
					elif proprow['proptype']['value'] == "WikibaseItem":
						propval = f"[[Item:{proprow['value']['value'].replace(config.entity_ns, '')}|{proprow['valueLabel']['value']}]]"
					elif proprow['proptype']['value'] == "Time":
						propval = proprow['value']['value'][0:4] # year only
					lcr_info += f"* {proprow['propLabel']['value']}: {propval}\n"

			if len(row['zot_subj_dist']['value']) > 1:
				output[wikipage] += "\nBertsio honi buruzkoak:\n"
				for zotid in row['zot_subj_dist']['value'].split(' '):
					about_lcr += "* " + zoterobot.getcitation(zotid) + "\n"
			lcryear = row['pubyear']['value']+', ' if 'pubyear' in row else ""

			output[wikipage] += f"\n=={str(lcrcount)}. {proprow['lcrLabel']['value']} ({lcryear}[[Item:{lcrid}|{lcrid}]])==\n\n{lcr_info}{about_lcr}\nBertsio honen argitalpenak:\n"
		dist = row['dist']['value']
		distid = dist.replace(config.entity_ns, '')
		if 'dist_zot' in row:
			citation = zoterobot.getcitation(row['dist_zot']['value'])  # .replace(config.entity_ns+distid,'')
			output[wikipage] += f"* ({row['bibtypeLabel']['value']}, ''{row['pubyear']['value']}'':) {citation}\n"
		else:
			output[wikipage] += f"* {row['bibtypeLabel']['value']}: Ikus [[Item:{distid}|{distid}]].\n"

	with open('data/testout.json', 'w', encoding='utf-8') as outfile:
		json.dump(output, outfile)
	with open('data/testout.txt', 'w', encoding='utf-8') as outfile:
		outfile.write(output[wikipage])

	input('\nTest output files written. Press return to proceed writing wikipages.')

	for pagetitle in output:
		pagecreation = lwb.site.post('edit', token=lwb.token, contentformat='text/x-wiki', contentmodel='wikitext',
									 bot=True, recreate=True, summary="recreate wiki page using lcr-wikitext.py",
									 title=pagetitle, text=output[pagetitle])
		print(str(pagecreation))