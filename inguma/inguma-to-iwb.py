import iwbi
import inguma
import json, re, traceback, csv, sys, time, requests
from pathlib import Path
from urllib.parse import urlparse, urlunparse

def extra(fieldname, value):
	global groupname
	statements = {'append':[],'replace':[]}
	if fieldname == "id":
		statements['replace'].append(iwbi.String(value=groupname+':'+str(value).strip(), prop_nr="P49"))
	elif fieldname == "address":
		value = value.strip()
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
		value = value(strip)
		namedate = re.search(r'^([^\(]+)\((\d+) ?\- ?(\d+)\)',value)
		if namedate.group(1):
			statements['replace'].append(iwbi.String(value=namedate.group(1).strip(), prop_nr="P9"))
		else:
			statements['replace'].append(iwbi.String(value=value.strip(), prop_nr="P9"))
		if namedate.group(2):
			statements['replace'].append(iwbi.Time(time='+'+namedate.group(2)+'-01-01T00:00:00Z', precision=9, prop_nr="P44"))
			print('Found birth year in second surname, processed it.')
		if namedate.group(3):
			statements['replace'].append(iwbi.Time(time='+'+namedate.group(3)+'-01-01T00:00:00Z', precision=9, prop_nr="P45"))
			print('Found death year in second surname, processed it.')
	elif fieldname == "issn":
		if len(value) > 1:
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

	return statements

def add_labels(groupname, entryjson, iwbitem):
	langs = ['eu', 'en']
	aliases = None
	if groupname == "persons":
		label = entryjson['name'].strip()+' '+entryjson['surname'].strip()+' '+entryjson['secondSurname'].strip()
		aliases = [entryjson['name'].strip()+' '+entryjson['surname'].strip(),entryjson['surname'].strip()+', '+entryjson['name'].strip()]
	elif groupname == "productions":
		label = entryjson['title']
	elif groupname == "organizations":
		langs = ['eu']
		label = entryjson['name']
	for lang in langs:
		iwbitem.labels.set(language=lang, value=label)
		if aliases:
			iwbitem.aliases.set(language=lang, values=aliases)
	print('Item label is: '+label)
	return iwbitem







print('___________________________\n')

groupname = "organizations"
print('\nWill process group '+groupname+'...')

# Inguma SQL data: Stored API result is used (created using inguma.py getingumagroup)
# TBD: ask user if a fresh download from inguma api is wanted and call inguma.py getingumagroup
with open('D:/Inguma/'+groupname+'.json', 'r') as jsonfile:
	group = json.load(jsonfile)

groupmappingfile = Path('D:/Inguma/'+groupname+'_qidmapping.csv')
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
	print('['+str(index)+'] Now processing '+groupname+' item with id '+str(entry)+'... '+str(len(group)-index)+' items left.')
	iwbitem = None

	if str(entry) in qidmapping:
		print('entry id '+str(entry)+' corresponds to existing qid: '+qidmapping[str(entry)]+'.')

		if 'lastModified' in group[entry]:
			pass # TBD: allow updated records override older version (check for conflicting changes in wikibase?)

		# if input('Enter "0" for skipping this item, anything else for overriding it...') == "0":
		# 	continue
		iwbitem = iwbi.wbi.item.get(entity_id=qidmapping[str(entry)])
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

	# item labels
	iwbitem = add_labels(groupname, group[entry], iwbitem)
	# item description
	if "classdesc" in inguma.mappings[groupname]:
		iwbitem.descriptions.set(language="eu", value=inguma.mappings[groupname]['classdesc'])

	statements = {'append':[],'replace':[]}
	# 'instance of' statement
	if "classqid" in inguma.mappings[groupname]:
		statements['append'].append(iwbi.Item(value=inguma.mappings[groupname]['classqid'], prop_nr="P5"))

	for key in group[entry].keys():
		if key in inguma.mappings[groupname] and len(str(group[entry][key])) > 0:
			if inguma.mappings[groupname][key].startswith("str:"):
				prop = inguma.mappings[groupname][key].split(':')[1]
				writevalue = str(group[entry][key]).strip()
				statements['replace'].append(iwbi.String(value=writevalue, prop_nr=prop))
			elif inguma.mappings[groupname][key].startswith("ext:"):
				prop = inguma.mappings[groupname][key].split(':')[1]
				writevalue = str(group[entry][key]).strip()
				statements['replace'].append(iwbi.ExternalID(value=writevalue, prop_nr=prop))
			elif inguma.mappings[groupname][key].startswith("url:"):
				prop = inguma.mappings[groupname][key].split(':')[1]
				url_parsed = urlparse(group[entry][key].strip())
				#print(str(url_parsed))
				if url_parsed[0] == '':
					url_parsed = url_parsed._replace(scheme='http')
					#print(str(url_parsed))
				statements['replace'].append(iwbi.URL(value=urlunparse(url_parsed), prop_nr=prop))
			elif inguma.mappings[groupname][key].startswith("mon:"): # example: "mon:eu:P10" (productions title)
				lang = inguma.mappings[groupname][key].split(':')[1]
				prop = inguma.mappings[groupname][key].split(':')[2]
				writevalue = str(group[entry][key]).strip()
				statements['replace'].append(iwbi.MonolingualText(value=writevalue, language=lang, prop_nr=prop))
			elif inguma.mappings[groupname][key].startswith("item:"):
				maptable = inguma.mappings[groupname][key]
				map = inguma.mappings[maptable][group[entry][key]].split('_')
				#print(str(map))
				prop = map[0]
				writevalue = map[1]
				statements['replace'].append(iwbi.Item(value=writevalue, prop_nr=prop))
			# extra treatments
			elif inguma.mappings[groupname][key].startswith("extra:"):
				extra_handled = extra(key, group[entry][key])
				statements['replace'] += extra_handled['replace']
				statements['append'] += extra_handled['append']



	#
	# if len(statements['replace']) > 0:
	# 	item.claims.add(statements['replace'])
	# if len(statements['append']) > 0:
	# 	item.claims.add(statements['append'], action_if_exists=iwbi.ActionIfExists.FORCE_APPEND)
	# d = False
	# while d == False:
	# 	try:
	# 		r = item.write()
	# 		d = True
	# 	except Exception:
	# 		ex = traceback.format_exc()
	# 		# print(ex)
	# 		if "wikibase-validator-label-with-description-conflict" in str(ex):
	# 			print('Found an ambigouus person name, but with different clearName.')
	# 			item.descriptions.set(language="eu", value="Beste pertsona bat")
	#print(str(statements))
	qid = iwbi.itemwrite(iwbitem, statements)
	if entry not in qidmapping:
		with open(groupmappingfile, 'a', encoding="utf-8") as txtfile:
			txtfile.write(str(entry)+'\t'+qid+'\n')

	#print('Finished writing entry with id '+str(entry)+', Qid: '+qid+'.\n')

print('Finished processing '+groupname+'.')
