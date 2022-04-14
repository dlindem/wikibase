import iwbi
import inguma
import json, re, traceback, csv, sys, time, requests, validators
from pathlib import Path
from urllib.parse import urlparse, urlunparse
import urllib.request
opener = urllib.request.build_opener()
opener.addheaders = [('Accept', 'application/vnd.crossref.unixsd+xml')]

def extra(fieldname, value):
	global groupname
	statements = {'append':[],'replace':[]}
	if fieldname == "id":
		statements['replace'].append(iwbi.String(value=groupname+':'+str(value).strip(), prop_nr="P49"))
	elif fieldname == "address":
		value = value.strip().replace("\t","")
		r = requests.get('https://nominatim.openstreetmap.org/search?q="'+value+'"&format=json')
		#print(str(r.json()))
		if len(r.json()) > 0:
			lat = r.json()[0]['lat']
			lon = r.json()[0]['lon']
			print('Got as first OSM result these coords:',str(lat),str(lon))
			references = [[iwbi.String(value=value, prop_nr="P55")]]
			statements['replace'].append(iwbi.GlobeCoordinate(prop_nr = "P57", latitude = float(lat), longitude = float(lon), references=references))
		else:
			print('Did not find coords on OSM for this address literal.')
		statements['replace'].append(iwbi.String(value=value, prop_nr="P55")) # address literal
	elif fieldname == "secondSurname":
		value = value.strip().replace("\t","")
		namedate = re.search(r'^([^\(]+)\((\d+) ?\- ?(\d+)\)',value)
		if not namedate:
			statements['replace'].append(iwbi.String(value=value, prop_nr="P9"))
		else:
			statements['replace'].append(iwbi.String(value=namedate.group(1).strip(), prop_nr="P9"))
			if namedate.group(2):
				statements['replace'].append(iwbi.Time(time='+'+namedate.group(2)+'-01-01T00:00:00Z', precision=9, prop_nr="P44"))
				print('Found birth year in second surname, processed it.')
			if namedate.group(3):
				statements['replace'].append(iwbi.Time(time='+'+namedate.group(3)+'-01-01T00:00:00Z', precision=9, prop_nr="P45"))
				print('Found death year in second surname, processed it.')
	elif fieldname == "issn":
		if value:
			if "-" not in value.strip(): # normalize ISSN, remove any secondary ISSN
				value = value.strip()[0:4]+"-"+value.strip()[4:9]
			else:
				value = value.strip()[:9]
			print('Found issn: '+value)
			statements['replace'].append(iwbi.ExternalID(value=value, prop_nr="P23"))
			print('Querying Wikidata for ISSN: '+value+'...')
			query = 'select ?wd where {?wd wdt:P236 "'+value+'".}'
			bindings = iwbi.wbi_helpers.execute_sparql_query(query=query, endpoint="https://query.wikidata.org/sparql", user_agent=iwbi.wd_user_agent)['results']['bindings']
			if len(bindings) > 0:
				wdqid = bindings[0]['wd']['value'].replace("http://www.wikidata.org/entity/","")
				print('Found wikidata item: '+iwbqid)
				statements['replace'].append(iwbi.ExternalID(value=wdqid, prop_nr="P1"))
			else:
				print('Nothing found on Wikidata for this ISSN.')

	elif fieldname == "isbn":
		if value:
			value = value.replace("-","").replace(" ","")
			if len(value) == 10 and value.isdigit():
				statements['append'].append(iwbi.ExternalID(value=value, prop_nr="P22"))
			elif len(value) == 13 and value.isdigit():
				statements['append'].append(iwbi.ExternalID(value=value, prop_nr="P21"))
			else:
				print('*** ERROR: Anormal ISBN, cannot be processed: '+value)

	elif fieldname == "year":
		value = str(value)
		statements['replace'].append(iwbi.Time(time='+'+value+'-01-01T00:00:00Z', precision=9, prop_nr="P19"))

	elif fieldname == "writerName":
		if value:
			print('writerName field literal: '+value)
			value = value.strip().replace("\t","")
			value = re.sub('\([^\)]+\)', '', value)
			subregex = ['\.\.+ ?', '\([^\)]+\) ?', '\[[^\]]+\) ?', '[Ee]dito[^,: ]+[,: ]*', '[Aa]rgitar[^,: ]+[: ,]*', '[Kk]oord[^\.,: ]+[: ,]*', '[Ee]d\. ', '[Aa]rg\.']
			for regex in subregex:
				value = re.sub(regex, '', value)
			value = value.replace(" eta ",", ")
			value = value.replace(", ",",")
			names = value.split(",")
			print('Editor names: '+ str(names))
			for name in names:
				if name.replace(" ","").isalpha():
					statements['replace'].append(iwbi.String(value=name.strip(), prop_nr="P60"))
				else:
					print('*** ERROR: unprocessable editor name literal: '+name+' in: '+value)

	elif fieldname == "doi":
		if isinstance(value, str) and len(value) > 5:
			doi = re.search('10\.\d+/.*', value)
			if doi:
				puredoi = doi.group(0).rstrip()
				print('Found DOI: '+puredoi+'...', end=" ")
				statements['replace'].append(iwbi.ExternalID(value=puredoi, prop_nr="P20"))
				# try:
				# 	r = opener.open('http://dx.doi.org/'+puredoi)
				# 	# print(str(r.info()['Link']))
				# 	pdflink = re.search('<([^\>]+\.pdf)>', str(r.info()['Link']))
				# 	if pdflink:
				# 		print('Found PDF link at crossref: '+pdflink.group(1))
				# 		statements['append'].append(iwbi.URL(value=pdflink.group(1), prop_nr="P48", qualifiers=[iwbi.ExternalID(prop_nr="P20", value=puredoi)]))
				# 	else:
				# 		print('No full text link at crossref.')
				# except:
				# 	print('Error querying crossref.')

	return statements

def add_labels(groupname, entryjson, iwbitem):
	langs = ['eu', 'en']
	aliases = None
	if groupname == "persons":
		label = entryjson['name'].strip()+' '+entryjson['surname'].strip()+' '+entryjson['secondSurname'].strip()
		aliases = [entryjson['name'].strip()+' '+entryjson['surname'].strip(),entryjson['surname'].strip()+', '+entryjson['name'].strip()]
	elif groupname == "productions":
		label = entryjson['title']
	elif groupname == "knowledge-areas":
		langs = ['eu']
		label = entryjson['knowledgeArea']
	elif groupname == "organizations":
		langs = ['eu']
		label = entryjson['name']
	for lang in langs:
		iwbitem.labels.set(language=lang, value=label)
		if aliases:
			iwbitem.aliases.set(language=lang, values=aliases)
	print('Item label is: '+label)
	return iwbitem

# load persons
with open('D:/Inguma/content/persons_qidmapping.csv', 'r', encoding="utf-8") as txtfile:
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
		listposquali = iwbi.String(value=listpos, prop_nr="P36")
		try:
			statements['append'].append(iwbi.Item(value=personqid[str(inguma_authors[listpos])], prop_nr="P17", qualifiers=[listposquali]))
		except:
			print('Author ID is missing in persons_qidmapping. Will try to resolve via SPARQL.')
			query = 'select ?wikibase_item where {?wikibase_item idp:P49 "persons:'+str(inguma_authors[listpos])+'".}'
			bindings = iwbi.wbi_helpers.execute_sparql_query(query=query, prefix=iwbi.sparql_prefixes)['results']['bindings']
			if len(bindings) > 0:
				iwbqid = bindings[0]['wikibase_item']['value'].replace("http://wikibase.inguma.eus/entity/","")
				print('Found wikibase item via SPARQL: This item is on IWB, qid is '+iwbqid)
				statements['append'].append(iwbi.Item(value=iwbqid, prop_nr="P17", qualifiers=[listposquali]))
	return statements

# load knowledge areas
with open('D:/Inguma/content/knowledge-areas_qidmapping.csv', 'r', encoding="utf-8") as txtfile:
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
		statements['replace'].append(iwbi.Item(value=areaqid[str(area)], prop_nr="P59"))
	return statements

# load organizations
with open('D:/Inguma/content/organizations_qidmapping.csv', 'r', encoding="utf-8") as txtfile:
	rows = txtfile.read().split("\n")
	orgqid = {}
	for row in rows:
		rowsplit = row.split('\t')
		if len(rowsplit) == 1:
			break
		orgqid[rowsplit[0]] = rowsplit[1]
def get_orgs(entryjson, statements):
	value = orgqid[str(entryjson['organizationId'])]
	statements['replace'].append(iwbi.Item(value=value, prop_nr="P37"))
	print('Found publisher: '+value)
	return statements

print('__________________________________________________________\n')

# groupname = "persons"
groupname = "productions"
print('\nWill process group '+groupname+'...\n')
keypress = input('Press 1 for downloading new data from INGUMA, other keys for re-using existing file.')
if keypress == "1":
	group = inguma.get_ingumagroup(groupname)
else:
	with open('D:/Inguma/content/'+groupname+'.json', 'r') as jsonfile:
		group = json.load(jsonfile)

groupmappingfile = Path('D:/Inguma/content/'+groupname+'_qidmapping.csv')
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
	# if index < :
	# 	continue


	# productions: exclude non-allowed production types
	if groupname == "productions":
		if inguma.mappings['item:ingumaProdType'][group[entry]['type']] == None:
			continue

	print('\n['+str(index)+'] Now processing '+groupname+' item with id '+str(entry)+'... '+str(len(group)-index)+' items left.')
	iwbitem = None

	if str(entry) in qidmapping:
		print('entry id '+str(entry)+' corresponds to existing qid: '+qidmapping[str(entry)]+'.')

		if 'lastModified' in group[entry]:
			pass # TBD: allow updated records override older version (check for conflicting changes in wikibase?)

		# if input('Enter "0" for skipping this item, anything else for overriding it...') == "0":
		continue
		iwbitem = iwbi.wbi.item.get(entity_id=qidmapping[str(entry)])
		clear = True # This will delete all existing claims!!

		#print(str(iwbitem.claims))
	# else:
	# 	query = 'select ?wikibase_item where {?wikibase_item idp:P49 "'+str(entry['id'])+'".}'
	# 	bindings = iwbi.wbi_helpers.execute_sparql_query(query=query, prefix=iwbi.sparql_prefixes)['results']['bindings']
	# 	if len(bindings) > 0:
	# 		iwbqid = bindings[0]['wikibase_item']['value'].replace("http://wikibase.inguma.eus/entity/","")
	# 		print('Found wikibase item via SPARQL: This item is on IWB, qid is '+iwbqid)
	# 		continue
	# 	press_key = input('No existing item found, also not by SPARQL. There will be created a new item, please confirm (y/n)')
	# 	if press_key == "y":

	if not iwbitem:
		iwbitem = iwbi.wbi.item.new()
		print('New item created.')
		clear = False

	# item labels
	iwbitem = add_labels(groupname, group[entry], iwbitem)

	# item description
	if "classdesc" in inguma.mappings[groupname]:
		iwbitem.descriptions.set(language="eu", value=inguma.mappings[groupname]['classdesc'])

	# claims
	statements = {'append':[],'replace':[]}

	# 'instance of' statement
	if "classqid" in inguma.mappings[groupname]:
		statements['append'].append(iwbi.Item(value=inguma.mappings[groupname]['classqid'], prop_nr="P5"))

	# productions and persons: get missing info from inguma
	if groupname == "productions":
		statements = get_authors(entry, statements) # author items
		statements = get_areas(entry, statements) # knowledge area items
		statements = get_orgs(group[entry], statements) # publisher item
	# if groupname == "persons":
	# 	statements = get_affiliations(entry, statements)

	# other claims
	for key, value in group[entry].items():
		if key in inguma.mappings[groupname] and len(str(value)) > 0:
			writevalue = str(value).strip().replace("\t","")
			if inguma.mappings[groupname][key].startswith("str:"):
				if writevalue != "None": # treat "None" as empty string
					prop = inguma.mappings[groupname][key].split(':')[1]
					statements['replace'].append(iwbi.String(value=writevalue, prop_nr=prop))

			elif inguma.mappings[groupname][key].startswith("ext:"):
				writevalue = str(value).strip().replace("\t","")
				if writevalue != "None": # treat "None" as empty string
					prop = inguma.mappings[groupname][key].split(':')[1]
					statements['replace'].append(iwbi.ExternalID(value=writevalue, prop_nr=prop))

			elif inguma.mappings[groupname][key].startswith("url:"):
				prop = inguma.mappings[groupname][key].split(':')[1]
				if prop == "P24" and value.endswith('.pdf'):
					prop = "P48" # download location instead of distribution location
				url_parsed = urlparse(value.strip().replace("\t",""))
				#print(str(url_parsed))
				if url_parsed[0] == '':
					url_parsed = url_parsed._replace(scheme='http')
				url_unparsed = urlunparse(url_parsed)
				if validators.url(url_unparsed):
					statements['replace'].append(iwbi.URL(value=url_unparsed, prop_nr=prop))
				else:
					malformed_url_file = Path('D:/Inguma/content/'+groupname+'_malformed_url.csv')
					groupmappingfile.touch(exist_ok=True) # if file does not exist
					with open(malformed_url_file, "w") as txtfile:
						if 'cleanTitle' in group[entry]:
							itemlabel = group[entry]['cleanTitle']
						elif 'cleanName' in group[entry]:
							itemlabel = group[entry]['cleanName']
						else:
							itemlabel = iwbitem.label(language="eu")
						txtfile.write(entry+'\t'+group[entry]['cleanTitle']+'\t'+value+'\t'+url_unparsed+'\n')

			elif inguma.mappings[groupname][key].startswith("mon:"): # example: "mon:eu:P10" (productions title)
				lang = inguma.mappings[groupname][key].split(':')[1]
				prop = inguma.mappings[groupname][key].split(':')[2]
				writevalue = str(value).strip().replace("\t","")
				statements['replace'].append(iwbi.MonolingualText(text=writevalue, language=lang, prop_nr=prop))

			elif inguma.mappings[groupname][key].startswith("item:"):
				maptable = inguma.mappings[groupname][key]
				map = inguma.mappings[maptable][value].split('_')
				#print(str(map))
				prop = map[0]
				writevalue = map[1]
				statements['replace'].append(iwbi.Item(value=writevalue, prop_nr=prop))

			# extra treatments
			elif inguma.mappings[groupname][key].startswith("extra:"):
				extra_handled = extra(key, value)
				statements['replace'] += extra_handled['replace']
				statements['append'] += extra_handled['append']

	qid = iwbi.itemwrite(iwbitem, statements, clear=clear)
	if entry not in qidmapping:
		with open(groupmappingfile, 'a', encoding="utf-8") as txtfile:
			txtfile.write(str(entry)+'\t'+qid+'\n')

	#print('Finished writing entry with id '+str(entry)+', Qid: '+qid+'.\n')


print('Finished processing '+groupname+'.')
