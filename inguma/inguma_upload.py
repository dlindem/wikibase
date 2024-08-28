import iwbiv1
import inguma
import json, re, traceback, csv, sys, time, requests, validators, os
from pathlib import Path
from urllib.parse import urlparse, urlunparse
import urllib.request
opener = urllib.request.build_opener()
opener.addheaders = [('Accept', 'application/vnd.crossref.unixsd+xml')]

def update_mapping(groupname):
	print('\nWill now update Inguma database ID -- Inguma Wikibase Qid mapping for group: '+groupname)
	groupmappingfile = Path('data/'+groupname+'_qidmapping.csv')
	date = time.strftime("%Y%m%d")
	groupmappingoldfile = Path('data/'+groupname+'_qidmapping_old_'+date+'.csv')
	query = 'select ?id ?wikibase_item where {?wikibase_item idp:P49 ?id. filter regex (?id, "^'+groupname+':")}'
	bindings = iwbiv1.wbi_helpers.execute_sparql_query(query=query, prefix=iwbiv1.sparql_prefixes)['results']['bindings']
	if len(bindings) > 0:
		print('Found entities: '+str(len(bindings)))
		os.rename(groupmappingfile, groupmappingoldfile)
		with open(groupmappingfile, 'w', encoding="utf-8") as txtfile:
			seen_inguma_id = []
			for binding in bindings:
				inguma_id = binding['id']['value']
				wikibase_id = binding['wikibase_item']['value'].replace("https://wikibase.inguma.eus/entity/","")
				if inguma_id in seen_inguma_id:
					print('\n*** WARNING: This inguma id appears twice!\n***', inguma_id, wikibase_id, 'will not write this to mapping file!')
					for re_binding in bindings:
						if re_binding['id']['value'] == inguma_id:
							print('*** The item to merge to is', re_binding['wikibase_item']['value'], '\n')
							time.sleep(5)
				else:
					txtfile.write(inguma_id.replace(groupname+":","")+'\t'+wikibase_id+'\n')
	return "Mapping for "+groupname+" updated and saved to file."

def extra(groupname=None, fieldname=None, value=None):
	statements = {'append':[],'replace':[]}
	if fieldname == "id":
		statements['replace'].append(iwbiv1.String(value=groupname+':'+str(value).strip(), prop_nr="P49"))
	elif fieldname == "address":
		value = value.strip().replace("\t","")
		r = requests.get('https://nominatim.openstreetmap.org/search?q="'+value+'"&format=json')
		#print(str(r.json()))
		if len(r.json()) > 0:
			lat = r.json()[0]['lat']
			lon = r.json()[0]['lon']
			print('Got as first OSM result these coords:',str(lat),str(lon))
			references = [[iwbiv1.String(value=value, prop_nr="P55")]]
			statements['replace'].append(iwbiv1.GlobeCoordinate(prop_nr = "P57", latitude = float(lat), longitude = float(lon), references=references))
		else:
			print('Did not find coords on OSM for this address literal.')
		statements['replace'].append(iwbiv1.String(value=value, prop_nr="P55")) # address literal
	elif fieldname == "secondSurname":
		value = value.strip().replace("\t","")
		statements['replace'].append(iwbiv1.String(value=value, prop_nr="P9"))
		# namedate = re.search(r'^([^\(]+)\((\d+) ?\- ?(\d+)\)',value)
		# if not namedate:
		# 	statements['replace'].append(iwbiv1.String(value=value, prop_nr="P9"))
		# else:
		# 	statements['replace'].append(iwbiv1.String(value=namedate.group(1).strip(), prop_nr="P9"))
		# 	if namedate.group(2):
		# 		statements['replace'].append(iwbiv1.Time(time='+'+namedate.group(2)+'-01-01T00:00:00Z', precision=9, prop_nr="P44"))
		# 		print('Found birth year in second surname, processed it.')
		# 	if namedate.group(3):
		# 		statements['replace'].append(iwbiv1.Time(time='+'+namedate.group(3)+'-01-01T00:00:00Z', precision=9, prop_nr="P45"))
		# 		print('Found death year in second surname, processed it.')
	elif fieldname == "issn":
		if value:
			if "-" not in value.strip(): # normalize ISSN, remove any secondary ISSN
				value = value.strip()[0:4]+"-"+value.strip()[4:9]
			else:
				value = value.strip()[:9]
			print('Found issn: '+value)
			statements['replace'].append(iwbiv1.ExternalID(value=value, prop_nr="P23"))
			print('Querying Wikidata for ISSN: '+value+'...')
			query = 'select ?wd where {?wd wdt:P236 "'+value+'".}'
			bindings = iwbiv1.wbi_helpers.execute_sparql_query(query=query, endpoint="https://query.wikidata.org/sparql", user_agent=iwbiv1.wd_user_agent)['results']['bindings']
			if len(bindings) > 0:
				wdqid = bindings[0]['wd']['value'].replace("http://www.wikidata.org/entity/","")
				print('Found wikidata item: '+wdqid)
				statements['replace'].append(iwbiv1.ExternalID(value=wdqid, prop_nr="P1"))
			else:
				print('Nothing found on Wikidata for this ISSN.')

	elif fieldname == "isbn":
		if value:
			anormal = False
			value = value.replace("-","").replace(" ","").replace("\t","")
			if len(value) == 10 or len(value) == 13:
				for i in range(len(value)):
					if value[i-1] not in "0123456789X":
						anormal = True
			else:
				anormal = True
			if not anormal:
				if len(value) == 10:
					statements['append'].append(iwbiv1.ExternalID(value=value, prop_nr="P22"))
				if len(value) == 13:
					statements['append'].append(iwbiv1.ExternalID(value=value, prop_nr="P21"))
				print('Found valid isbn: '+value)
			else:
				print('*** ERROR: Anormal ISBN, cannot be processed: '+value)

	elif fieldname == "year":
		value = str(value)
		statements['replace'].append(iwbiv1.Time(time='+'+value+'-01-01T00:00:00Z', precision=9, prop_nr="P19"))

	elif fieldname == "writerName":
		if value:
			print('writerName field literal: '+value)
			value = value.strip().replace("\t","")
			value = re.sub('\([^\)]+\)', '', value)
			subregex = ['\.\.+ ?', '\([^\)]+\) ?', '\[[^\]]+\) ?', '[Ee]dito[^,: ]+[,: ]*', '[Aa]rgitar[^,: ]+[: ,]*', '[Kk]oor[^\.,: ]+[: ,]*', '[Ee]d\. ', '[Aa]rg\.']
			for regex in subregex:
				value = re.sub(regex, '', value)
			value = value.replace(" eta ",", ")
			value = value.replace(", ",",")
			names = value.split(",")
			print('Editor names: '+ str(names))
			for name in names:
				if name.replace(" ","").isalpha():
					statements['replace'].append(iwbiv1.String(value=name.strip(), prop_nr="P60"))
				else:
					print('*** ERROR: unprocessable editor name literal: '+name+' in: '+value)

	elif fieldname == "doi":
		if isinstance(value, str) and len(value) > 5:
			doi = re.search('10\.\d+/.*', value)
			if doi:
				puredoi = doi.group(0).rstrip()
				print('Found DOI: '+puredoi+'...')
				statements['replace'].append(iwbiv1.ExternalID(value=puredoi, prop_nr="P20"))
				try:
					r = opener.open('http://dx.doi.org/'+puredoi)
					# print(str(r.info()['Link']))
					pdflink = re.search('<([^\>]+\.pdf)>', str(r.info()['Link']))
					if pdflink:
						print('Found PDF link at crossref: '+pdflink.group(1))
						statements['append'].append(iwbiv1.URL(value=pdflink.group(1), prop_nr="P48", qualifiers=[iwbiv1.ExternalID(prop_nr="P20", value=puredoi)]))
					else:
						print('No full text link at crossref.')
				except:
					print('Error querying crossref.')
	elif fieldname == "issue": # first number will be "volume", second number "issue" (except for double volumes)
		volume = None
		volume_re = re.search('^ ?(\d+)', value)
		issue_re = re.search('^ ?\d+[^\d]+(\d+)', value)
		double_vol_re = re.search('^ ?(\d+)\-(\d+)', value)
		if double_vol_re:
			if int(double_vol_re.group(2)) - int(double_vol_re.group(1)) == 1: # double vol. like "21-22"
				volume = double_vol_re.group(1)+"-"+double_vol_re.group(1)
		if not volume:
			if volume_re:
				volume = volume_re.group(1)
		if issue_re:
			issue = issue_re.group(1)
		else:
			issue = None
		if volume:
			statements['replace'].append(iwbiv1.String(value=volume, prop_nr="P26"))
		if issue:
			statements['replace'].append(iwbiv1.String(value=issue, prop_nr="P25"))

	elif fieldname == "url":
		if '.pdf' in value: # download location (pdf download) instead of distribution location (landing page)
			value = re.search('^.+\.pdf',value).group(0) # cut off anything after the ".pdf"
			prop = "P48"
		else:
			prop = "P24"
		url_processed = process_url(value)
		if url_processed:
			statements['replace'].append(iwbiv1.URL(value=url_processed, prop_nr=prop))

	elif fieldname == "type":
		statements['replace'].append(iwbiv1.Item(value=inguma.mappings, prop_nr="P26"))

	return statements

def process_url(value, ingumaitem=None):
	url_parsed = urlparse(value.replace("\t","").strip())
	#print(str(url_parsed))
	if url_parsed[0] == '':
		url_parsed = url_parsed._replace(scheme='http')
	url_unparsed = urlunparse(url_parsed)
	if validators.url(url_unparsed):
		return url_unparsed
	else:
		malformed_url_file = Path('data/'+'malformed_url.csv')

		with open(malformed_url_file, "w") as txtfile:
			txtfile.write(str(ingumaitem)+'\t'+value+'\t'+url_unparsed+'\n')
		return None

def add_labels(groupname, entryjson, iwbitem, statements):
	langs = ['eu', 'en'] # by default, labels are set to Basque and English
	aliases = None
	if groupname == "affiliations":
		label = entryjson['name'].strip()
		if entryjson['description'].strip() != "Zentro teknologiko espezializatua":
			aliases = [entryjson['description'].strip()]
	if groupname == "persons":
		if "(" in entryjson['secondSurname']:
			try:
				lifedates = re.search(' ?\(([^\)]+)\) ?', entryjson['secondSurname']).group(1)
				print('Found lifedates: '+lifedates+', secondSurname is '+entryjson['secondSurname'])
				entryjson['secondSurname'] = re.sub(r' ?\([^\)]+\) ?', entryjson['secondSurname'])
				parseddates = re.search(r'([\w ]+)\-([\w ]*)')
				if parseddates.group(1).strip().isdigit() and len(parseddates.group(1).strip()) == 4:
					statements['replace'].append(iwbiv1.Time(time='+'+parseddates.group(1).strip()+'-01-01T00:00:00Z', precision=9, prop_nr="P44"))
				if parseddates.group(2).strip().isdigit() and len(parseddates.group(2).strip()) == 4:
					statements['replace'].append(iwbiv1.Time(time='+'+parseddates.group(2).strip()+'-01-01T00:00:00Z', precision=9, prop_nr="P45"))
			except Exception as ex:
				print('Error in lifedates parsing, secondSurname is '+entryjson['secondSurname']+': '+str(ex))
		label = entryjson['name'].strip()+' '+entryjson['surname'].strip()+' '+entryjson['secondSurname'].strip()
		aliases = [entryjson['name'].strip()+' '+entryjson['surname'].strip(),entryjson['surname'].strip()+', '+entryjson['name'].strip()]
	elif groupname == "productions":
		label_encoded = entryjson['title'][:249].encode("ascii", "ignore") # eliminate unicode characters like '\u2028'
		label = label_encoded.decode()
	elif groupname == "knowledge-areas":
		langs = ['eu']
		label = entryjson['knowledgeArea']
	elif groupname == "organizations":
		langs = ['eu']
		label = entryjson['name'].strip()
	for lang in langs:
		iwbitem.labels.set(language=lang, value=label)
		if aliases:
			iwbitem.aliases.set(language=lang, values=aliases)
	print('Item label is: '+label)
	return {'iwbitem': iwbitem, 'statements': statements}

# load persons
with open('data/persons_qidmapping.csv', 'r', encoding="utf-8") as txtfile:
	rows = txtfile.read().split("\n")
	personqid = {}
	for row in rows:
		rowsplit = row.split('\t')
		if len(rowsplit) == 1:
			break
		personqid[rowsplit[0]] = rowsplit[1]
def get_authors(entry, statements):
	inguma_authors = inguma.get_production_authors(entry)
	for listpos in inguma_authors:
		listposquali = iwbiv1.String(value=listpos, prop_nr="P36")
		try:
			statements['append'].append(iwbiv1.Item(value=personqid[str(inguma_authors[listpos])], prop_nr="P17", qualifiers=[listposquali]))
		except:
			print('Author ID is missing in persons_qidmapping. Will try to resolve via SPARQL.')
			query = 'select ?wikibase_item where {?wikibase_item idp:P49 "persons:'+str(inguma_authors[listpos])+'".}'
			bindings = iwbiv1.wbi_helpers.execute_sparql_query(query=query, prefix=iwbiv1.sparql_prefixes)['results']['bindings']
			if len(bindings) > 0:
				iwbqid = bindings[0]['wikibase_item']['value'].replace("https://wikibase.inguma.eus/entity/","")
				print('Found wikibase item via SPARQL: This item is on IWB, qid is '+iwbqid)
				statements['append'].append(iwbiv1.Item(value=iwbqid, prop_nr="P17", qualifiers=[listposquali]))
	return statements

# load knowledge areas
with open('data/knowledge-areas_qidmapping.csv', 'r', encoding="utf-8") as txtfile:
	rows = txtfile.read().split("\n")
	areaqid = {}
	for row in rows:
		rowsplit = row.split('\t')
		if len(rowsplit) == 1:
			break
		areaqid[rowsplit[0]] = rowsplit[1]
def get_areas(entry, statements):
	inguma_areas = inguma.get_production_knowlareas(entry)
	for area in inguma_areas:
		statements['replace'].append(iwbiv1.Item(value=areaqid[str(area)], prop_nr="P59"))
	return statements

# load affiliations
with open('data/affiliations_qidmapping.csv', 'r', encoding="utf-8") as txtfile:
	rows = txtfile.read().split("\n")
	affqid = {}
	for row in rows:
		rowsplit = row.split('\t')
		if len(rowsplit) == 1:
			break
		affqid[rowsplit[0]] = rowsplit[1]
def get_affiliations(entry, statements):
	person_affiliations = inguma.get_person_affiliations(entry)
	for aff in person_affiliations:
		statements['replace'].append(iwbiv1.Item(value=affqid[str(aff)], prop_nr="P61"))
	return statements

# load organizations
with open('data/organizations_qidmapping.csv', 'r', encoding="utf-8") as txtfile:
	rows = txtfile.read().split("\n")
	orgqid = {}
	for row in rows:
		rowsplit = row.split('\t')
		if len(rowsplit) == 1:
			break
		orgqid[rowsplit[0]] = rowsplit[1]
def get_orgs(entryjson, statements):
	value = orgqid[str(entryjson['organizationId'])]
	statements['replace'].append(iwbiv1.Item(value=value, prop_nr="P37"))
	print('Found publisher: '+value)
	return statements

def update_group(groupname, rewrite=False): # if rewrite=True is passed, existing wikibase items are checked and re-written
	print('\nWill process group '+groupname+'...\n')
	# keypress = input('Press 1 for downloading new data from INGUMA, other keys for re-using existing file.')
	keypress = 0
	if keypress == "1":
		group = inguma.get_ingumagroup(groupname)
	else:
		with open('content/'+groupname+'.json', 'r') as jsonfile:
			group = json.load(jsonfile)

	groupmappingfile = Path('data/'+groupname+'_qidmapping.csv')
	groupmappingfile.touch(exist_ok=True) # if file does not exist
	with open(groupmappingfile, 'r', encoding="utf-8") as txtfile:
		listraw = txtfile.read().split('\n')
		qidmapping = {}
		for item in listraw:
			try:
				itemid = item.split('\t')[0]
				iwbqid = item.split('\t')[1]
				# doneitemid = int(re.search(r'^(\d+)',done).group(1))
				qidmapping[itemid] = iwbqid
			except:
				pass
		print('Items in group '+groupname+' that already have a qid: '+str(len(qidmapping)))
		time.sleep(2)

	index = 0
	for entry in group:
		index +=1

		# for bridging aborted runs
		# if index < 40075:
		# 	continue

		# productions: exclude non-allowed production types
		if groupname == "productions":
			if group[entry]['type'] != "introduction" and inguma.mappings['item:ingumaProdType'][group[entry]['type']] == None:
				continue # type "introduction" is handled through IntroductionSubType

		print('\n['+str(index)+'] Now processing '+groupname+' item with id '+str(entry)+'... '+str(len(group)-index)+' items left.')
		iwbitem = None

		if str(entry) in qidmapping:
			print(groupname+' id '+str(entry)+' maps to existing qid: '+qidmapping[str(entry)]+'.')

			if 'lastModified' in group[entry]:
				pass # TBD: allow updated records override older version (check for conflicting changes in wikibase?)

			# if input('Enter "0" for skipping this item, anything else for overriding it...') == "0":
			if rewrite == False:
				continue # continue: skip existing qid

			iwbitem = iwbiv1.wbi.item.get(entity_id=qidmapping[str(entry)])
			clear = True # clear = True will delete all existing claims!!

			#print(str(iwbitem.claims))
		# else:
		# 	query = 'select ?wikibase_item where {?wikibase_item idp:P49 "'+str(entry['id'])+'".}'
		# 	bindings = iwbiv1.wbi_helpers.execute_sparql_query(query=query, prefix=iwbiv1.sparql_prefixes)['results']['bindings']
		# 	if len(bindings) > 0:
		# 		iwbqid = bindings[0]['wikibase_item']['value'].replace("http://wikibase.inguma.eus/entity/","")
		# 		print('Found wikibase item via SPARQL: This item is on IWB, qid is '+iwbqid)
		# 		continue
		# 	press_key = input('No existing item found, also not by SPARQL. There will be created a new item, please confirm (y/n)')
		# 	if press_key == "y":

		#try:
		if not iwbitem:
			iwbitem = iwbiv1.wbi.item.new()
			print('This '+groupname+' id is not known; new item created.')
			clear = False

		# claims
		statements = {'append':[],'replace':[]}

		# item labels
		labels_added = add_labels(groupname, group[entry], iwbitem, statements)
		iwbitem = labels_added['iwbitem']
		statements = labels_added['statements']

		# item description
		if "classdesc" in inguma.mappings[groupname]:
			iwbitem.descriptions.set(language="eu", value=inguma.mappings[groupname]['classdesc'])

		# 'instance of' statement
		if "classqid" in inguma.mappings[groupname]:
			statements['append'].append(iwbiv1.Item(value=inguma.mappings[groupname]['classqid'], prop_nr="P5"))

		# productions and persons: get missing info from inguma
		if groupname == "productions":
			statements = get_authors(entry, statements) # author items
			statements = get_areas(entry, statements) # knowledge area items
			statements = get_orgs(group[entry], statements) # publisher item
		if groupname == "persons":
		 	statements = get_affiliations(entry, statements)

		# other claims (treated according to inguma.mappings)
		for key, value in group[entry].items():
			if key in inguma.mappings[groupname] and value and len(str(value).strip()) > 0:

				# clean value
				writevalue_encoded = str(value).encode("ascii", "ignore")
				writevalue = writevalue_encoded.decode()
				writevalue = writevalue.strip().replace("\t","").replace("  "," ")

				# actions depending on datatype defined in inguma.mappings
				if inguma.mappings[groupname][key].startswith("str:"):
					if writevalue != "None": # treat "None" as empty string
						prop = inguma.mappings[groupname][key].split(':')[1]
						statements['replace'].append(iwbiv1.String(value=writevalue, prop_nr=prop))

				elif inguma.mappings[groupname][key].startswith("ext:"):
					writevalue = str(value).strip().replace("\t","")
					if writevalue != "None": # treat "None" as empty string
						prop = inguma.mappings[groupname][key].split(':')[1]
						statements['replace'].append(iwbiv1.ExternalID(value=writevalue, prop_nr=prop))

				elif inguma.mappings[groupname][key].startswith("url:"):
					prop = inguma.mappings[groupname][key].split(':')[1]
					url_processed = process_url(value, ingumaitem = groupname+' '+str(entry))
					if url_processed:
						statements['replace'].append(iwbiv1.URL(value=url_processed, prop_nr=prop))

				elif inguma.mappings[groupname][key].startswith("mon:"): # example: "mon:eu:P10" (productions title)
					lang = inguma.mappings[groupname][key].split(':')[1]
					prop = inguma.mappings[groupname][key].split(':')[2]
					statements['replace'].append(iwbiv1.MonolingualText(text=writevalue, language=lang, prop_nr=prop))

				elif inguma.mappings[groupname][key].startswith("item:"):
					maptable = inguma.mappings[groupname][key]
					print(maptable,value)
					if value in inguma.mappings[maptable]:
						if inguma.mappings[maptable][value]:
							for mappair in inguma.mappings[maptable][value].split("|"):
								map = mappair.split('_')
								#print(str(map))
								prop = map[0]
								writevalue = map[1]
								statements['replace'].append(iwbiv1.Item(value=writevalue, prop_nr=prop))
					else:
						print('*** WARNING: Missing '+maptable+' maptable entry: '+str(value))

				# extra treatments
				elif inguma.mappings[groupname][key].startswith("extra:"):
					extra_handled = extra(groupname=groupname, fieldname=key, value=value)
					statements['replace'] += extra_handled['replace']
					statements['append'] += extra_handled['append']

		qid = iwbiv1.itemwrite(iwbitem, statements, clear=clear)
		if entry not in qidmapping and qid:
			with open(groupmappingfile, 'a', encoding="utf-8") as txtfile:
				txtfile.write(str(entry)+'\t'+qid+'\n')
		time.sleep(0.2)
		#except Exception as ex:
			#print('Error: ',str(ex))

		print('Finished writing entry with id '+str(entry)+'\n')


	print('Finished processing '+groupname+'.')

print('inguma-to-iwb functions loaded.\n')
