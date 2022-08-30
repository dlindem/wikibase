import lxml
from xml.etree import ElementTree
import re
import os
import csv
import sys
import json
from wikibaseintegrator import wbi_helpers
import clbwbi

def process_creator(ind1, subfields, clbrecord=None):
	global creatorqid
	global creator_ordinal
	creator_role_prop = None
	nkcr = None
	namequalis = None

	roles = {
	'aut' : 'P12',
	'edt' : 'P13',
	'edc' : 'P13'
	}
	creatordata = {'qid': False, 'statements' : []}

	for subfield in subfields:
		code = subfield.attrib['code']
		# NKCR
		if code == "7":
			nkcr = subfield.text
			if nkcr in creatorqid:
				print('This creator is existing Qid '+creatorqid[nkcr])
				creatordata['qid'] = creatorqid[nkcr]
			else:
				print('This creator will be created as new: '+nkcr)
				creatordata['statements'].append({'action':'replace','type':'ExternalID', 'value':nkcr, 'prop_nr':'P8','references':[{'type':'externalid','value':clbrecord,'prop_nr':'P7'}]})
				print('Querying Wikidata for NKCR AUT ID: '+nkcr+'...')
				query = 'select ?wd where {?wd wdt:P691 "'+nkcr+'".}'
				bindings = wbi_helpers.execute_sparql_query(query=query, endpoint="https://query.wikidata.org/sparql", user_agent="User:DL2204")['results']['bindings']
				if len(bindings) > 0:
					wdqid = bindings[0]['wd']['value'].replace("http://www.wikidata.org/entity/","")
					print('Found wikidata item: '+wdqid)
					creatordata['statements'].append({'action':'replace','type':"ExternalID", 'value':wdqid, 'prop_nr':"P1"})
				else:
					print('Nothing found on Wikidata for this NKCR AUT ID.')
		# creator role
		if code == "4":
			if subfield.text in roles:
				creator_role_prop = roles[subfield.text]
				print('Found creator role prop '+creator_role_prop)
		# creator name
		if code == "a":
			if ind1 == "1":
				creatordata['statements'].append({'action':'replace','type':'Item', 'value':'Q5', 'prop_nr':'P5'}) # instance of human
				lastname = subfield.text.split(",")[0]
				creatordata['statements'].append({'action':'replace','type':'String', 'value':lastname, 'prop_nr':'P48'})
				firstname = subfield.text.split(",")[1].strip()
				creatordata['statements'].append({'action':'replace','type':'String', 'value':firstname, 'prop_nr':'P47'})
				creatordata['labels'] = [{'lang':'en', 'value': firstname + " " + lastname}, {'lang': 'cs', 'value': firstname + " " + lastname}]
				creatordata['altlabels'] = [{'lang':'en', 'value': lastname + ", " + firstname}, {'lang': 'cs', 'value': lastname + ", " + firstname}]
				namequalis = [{'type': 'string', 'value': lastname, 'prop_nr': 'P48'}, {'type': 'string', 'value': firstname, 'prop_nr': 'P47'}]
			else:
				print('Unforeseen name type: ind1='+ind1+', Abort.')
				sys.exit()
		if code == "d":
			birthyear = subfield.text.split("-")[0]
			creatordata['statements'].append({'action':'replace','type':'Time', 'precision':9, 'value':'+'+birthyear+'-01-01T00:00:00Z', 'prop_nr':'P43'})
			deathyear = subfield.text.split("-")[1].strip()
			if len(deathyear) == 4:
				creatordata['statements'].append({'action':'replace','type':'Time', 'precision':9, 'value':'+'+deathyear+'-01-01T00:00:00Z', 'prop_nr':'P44'})

	qualifiers = [{'type': 'string', 'value': str(creator_ordinal[creator_role_prop]), 'prop_nr': 'P14'}]

#	if nkcr:
	if nkcr and creatordata['qid'] == False: # writes only if new creator item
		print('Will try to write to (new) creator item...')
		creatordata['qid'] = clbwbi.itemwrite(creatordata)
		if nkcr not in creatorqid:
			with open('data/creators_qidmapping.csv', 'a', encoding="utf-8") as file:
				file.write(nkcr+'\t'+creatordata['qid']+'\n')
				creatorqid[nkcr] = creatordata['qid']

	elif not nkcr:
		print('***Warning: This creator entry has no NKCR ID, so no Qid. Will write novalue creator statement.')
		qualifiers += namequalis

	return {'creatorstatement': {'action': 'append', 'type': 'Item', 'value':creatordata['qid'], 'prop_nr':creator_role_prop, 'qualifiers': qualifiers},
			'creator_role_prop': creator_role_prop}


marcxml_file = 'data/VuFindExport.xml'
xmlns = "{http://www.loc.gov/MARC21/slim}"
try:
	tree = ElementTree.parse(marcxml_file)
except Exception as ex:
	print ('Error: file does not exist, or XML cannot be loaded.')
	print (str(ex))
	sys.exit()

# load done records Marc record ID - Qid mapping
with open('data/records_qidmapping.csv', 'r', encoding="utf-8") as file:
	rows = file.read().split("\n")
	recordqid = {}
	for row in rows:
		rowsplit = row.split('\t')
		if len(rowsplit) == 1:
			break
		recordqid[rowsplit[0]] = rowsplit[1]

# load existing creator ID - Qid mapping
with open('data/creators_qidmapping.csv', 'r', encoding="utf-8") as file:
	rows = file.read().split("\n")
	creatorqid = {}
	for row in rows:
		rowsplit = row.split('\t')
		if len(rowsplit) == 1:
			break
		creatorqid[rowsplit[0]] = rowsplit[1]

# load country codes mapping
with open('data/marc-countries-wikidata.csv', 'r', encoding="utf-8") as file:
	countrydict = csv.DictReader(file)
	marc_countries = {}
	for row in countrydict:
		marc_countries[row['code']] = row['wikidata']

# load language codes mapping
with open('data/marc-languages-wikidata.csv', 'r', encoding="utf-8") as file:
	langdict = csv.DictReader(file)
	marc_languages = {}
	for row in langdict:
		marc_languages[row['code']] = {'wd': row['wikidata']}

# load exsting languages and countries
with open('data/languages_countries.json', 'r', encoding="utf-8") as file:
	languages_countries = json.load(file)

root = tree.getroot()
if root.tag != xmlns+"collection":
	print('This input file is not MARC21 XML. Abort.')
	sys.exit()
else:
	print('Will proceed to load MARC21 XML.')

count = 0
issn_log = {}
for record in root:
	statements = []
	record_id = None
	creator_ordinal = {'P12': 1, 'P13': 1}
	title = None
	titlelang = None
	subtitle = None
	transtitle = None
	clear = False
	count += 1
	print('\nNow processing record #'+str(count)+' with leader '+record.findall(xmlns+"leader")[0].text)

	# read controlfields
	for controlfield in record.findall(xmlns+"controlfield"):
		tag = controlfield.attrib['tag']
		text = controlfield.text
		print ("Controlfield ", tag, text)

		# read controlfield 001: Record ID
		if tag == "001":
			record_id = text
			if record_id in recordqid:
				itemqid = recordqid[text]
			else:
				itemqid = False
			statements.append({'action':'replace','type':'Item', 'value':'Q3', 'prop_nr':'P5',
			'qualifiers':[{'type':"String",'value':record_id, 'prop_nr':"P7"}]}) # instance of CLB record

		# read controlfield 008: time of publication
		if tag == "008":

			# date of publication
			prec = text[6]
			rv = {}
			if prec == "e":
				if text[13:15] != "  ":
					datetime = '+'+text[7:11]+'-'+text[11:13]+'-'+text[13:15]+'T00:00:00Z'
					precision = 11
				else:
					datetime = '+'+text[7:11]+'-'+text[11:13]+'-01T00:00:00Z'
					precision = 10
			elif prec == "s":
				datetime = '+'+text[7:11]+'-01-01T00:00:00Z'
				precision = 9
			statements.append({'action':'replace','type':"Time", 'value':datetime, 'precision':precision, 'prop_nr':"P15"})

			# country of publication
			marc_country = text[15:18].strip()
			if marc_country in languages_countries['countries']:
				countryqid = languages_countries['countries'][marc_country]
				print('Found publication country '+countryqid+' for '+marc_country)
			else:
				if marc_country not in marc_countries:
					print('Country code '+marc_country+' not found in marc-countries-wikidata.csv, abort.')
					sys.exit()
				print('Will create new country item.')
				countrydata = {'qid':False, 'statements':{'append':[{'type':'item', 'value':'Q17', 'prop_nr':'P5'},{'type':'String', 'value':marc_country, 'prop_nr':'P54'}], 'replace':[]}}
				if marc_countries[marc_country].startswith("Q"): # wikidata country item
					countrydata['statements'].append({'action':'append', 'type':'string', 'value':marc_countries[marc_country], 'prop_nr':'P1'})
				countryqid = clbwbi.itemwrite(countrydata)
				languages_countries['countries'][marc_country] = countryqid
				with open('data/languages_countries.json', 'w', encoding="utf-8") as file:
					json.dump(languages_countries, file, indent=2)

			statements.append({'action':'replace','type':"Item", 'value':countryqid, 'prop_nr':"P23"})

			# language of publication
			marc_language = text[35:38].strip()
			if marc_language in languages_countries['languages']:
				languageqid = languages_countries['languages'][marc_language]['qid']
				wmcode = languages_countries['languages'][marc_language]['wm']
				print('Found publication language '+languageqid+' for '+marc_language)
			else:
				if marc_language not in marc_languages:
					print('Language code '+marc_languages+' not found in marc-languges-wikidata.csv, abort.')
					sys.exit()
				print('Will create new language item.')
				languagedata = {'qid':False, 'statements':{'append':[{'type':'Item', 'value':'Q8', 'prop_nr':'P5'},{'type':'String', 'value':marc_language, 'prop_nr':'P53'}], 'replace':[]}}
				if marc_languages[marc_language]['wd'].startswith("Q"): # wikidata language item
					languagedata['statements'].append({'action':'append', 'type':'string', 'value':marc_languages[marc_language]['wd'], 'prop_nr':'P1'})
					print('Querying Wikidata for language item data: '+marc_languages[marc_language]['wd']+'...')
					query = 'select ?wmcode ?label where {wd:'+marc_languages[marc_language]['wd']+' wdt:P424 ?wmcode; rdfs:label ?label. filter(lang(?label)="en")}'
					bindings = wbi_helpers.execute_sparql_query(query=query, endpoint="https://query.wikidata.org/sparql", user_agent="User:DL2204")['results']['bindings']
					if len(bindings) > 0:
						wmcode = bindings[0]['wmcode']['value']
						print('Found wikidata language: '+wmcode)
						languagedata['statements'].append({'action':'replace','type':'string','value':wmcode, 'prop_nr':"P39"})
					else:
						print('No wmcode found on Wikidata for this language.')
				languageqid = clbwbi.itemwrite(languagedata)
				languages_countries['languages'][marc_language] = {'qid': languageqid, 'wm': wmcode}
				with open('data/languages_countries.json', 'w', encoding="utf-8") as file:
					json.dump(languages_countries, file, indent=2)

			titlelang = wmcode
			statements.append({'action':'replace','type':"Item", 'value':languageqid, 'prop_nr':"P49"})

	for datafield in record.findall(xmlns+"datafield"):
		tag = datafield.attrib['tag']
		ind1 = datafield.attrib['ind1']
		ind2 = datafield.attrib['ind2']

		# process creators
		if tag == "100" or tag == "700":
			processed_creator = process_creator(ind1, datafield.findall(xmlns+"subfield"), clbrecord=record_id)
			statements.append(processed_creator['creatorstatement'])
			creator_ordinal[processed_creator['creator_role_prop']] += 1
		# process title etc. (245)
		if tag == "245":

			for subfield in datafield.findall(xmlns+"subfield"):
				code = subfield.attrib['code']
				titletext = re.sub(' ?/$','',subfield.text)
				if code == "a":
					if titletext.endswith("="):
						transtitle == True
						title = re.sub(' *=$',titletext)
					else: # do we want to replace space in title colon : subtitle ?
						title = titletext
				if code == "b" and title and (not transtitle): # subtitle is merged to title
					title += " "+titletext
				if code == "b" and title and transtitle:
					transtitle = titletext


		# process 773
		if tag == "773":
			for subfield in datafield.findall(xmlns+"subfield"):
				code = subfield.attrib['code']
				# ISSN
				if code == "x":
					value = subfield.text
					if "-" not in value.strip(): # normalize ISSN, remove any secondary ISSN
						value = value.strip()[0:4]+"-"+value.strip()[4:9]
					else:
						value = value.strip()[:9]
					print('Found issn: '+value)
					if value in issn_log:
						wdqid = issn_log[value]['qid']
						wdlabel = issn_log[value]['label']
						print('ISSN already known as '+wdqid,wdlabel)
					else:
						print('Querying Wikidata for ISSN: '+value+'...')
						query = "select ?wd ?label where {?wd wdt:P236 '"+value+"'; rdfs:label ?label. filter(lang(?label)='en')}"
						bindings = wbi_helpers.execute_sparql_query(query=query, endpoint="https://query.wikidata.org/sparql", user_agent="User:DL2204")['results']['bindings']
						if len(bindings) > 0:
							wdqid = bindings[0]['wd']['value'].replace("http://www.wikidata.org/entity/","")
							wdlabel = bindings[0]['label']['value']
							print('Found wikidata item',wdqid,wdlabel)
							wdquali = [{'type':'ExternalID','value':wdqid, 'prop_nr':"P1"}, {'type':'monolingualtext', 'lang':'en', 'value':wdlabel, 'prop_nr':'P6'}]
							issn_log[value] = {'qid':wdqid, 'label':wdlabel}
						else:
							print('Nothing found on Wikidata for this ISSN.')
							wdquali = []
					statements.append({'action':'replace','type':'ExternalID', 'value':value, 'prop_nr':'P20', 'qualifiers':wdquali})
				# issue, volume
				if code == "q":
					fieldvals = re.search(r'^([0-9]+):([0-9]+)',subfield.text)
					issue = fieldvals.group(1)
					volume = fieldvals.group(2)
					print('Found issue '+str(issue),'Found volume '+str(volume))
					if issue:
						statements.append({'action':'replace','type':'string', 'value':issue, 'prop_nr':'P25'})
					if volume:
						statements.append({'action':'replace','type':'string', 'value':volume, 'prop_nr':'P24'})
		# process 020
		if tag == "020":
			for subfield in datafield.findall(xmlns+"subfield"):
				code = subfield.attrib['code']
				if code == "a":
					pass
					# process ISBN (TBD)
	# write title
	if title:
		if not titlelang:
			presskey = input('Error. no language for the title: '+title)
		statements.append({'action':'replace','type':'Monolingualtext', 'lang': titlelang, 'value':title, 'prop_nr':'P6'})
		itemlabels = [{'lang': titlelang, 'value': title}]
	if transtitle:
		pass # tbd. 246 is also transtitle
	print('\nStatements: '+str(statements))

	realitemqid = clbwbi.itemwrite({'qid': itemqid, 'labels': itemlabels, 'statements': statements})
	if not itemqid:
		with open('data/records_qidmapping.csv', 'a', encoding="utf-8") as file:
			file.write(record_id+'\t'+realitemqid+'\n')
			recordqid[record_id] = realitemqid




	# for controlfield in record.findall(xmlns+"controlfield"):
	# 	process_controlfield(
	# 	tag=controlfield.attrib["tag"],
	# 	text=controlfield.text
	# 	)
	# for datafield in record.findall(xmlns+"datafield"):
	# 	process_datafield(
	# 	tag=datafield.attrib["tag"],
	# 	ind1=datafield.attrib["ind1"],
	# 	ind2=datafield.attrib["ind2"],
	# 	subfields = datafield.findall(xmlns+"subfield")
	# 	)
