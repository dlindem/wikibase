import lxml
from xml.etree import ElementTree
import re
import os
import csv
import sys
import json
from wikibaseintegrator import wbi_helpers
# import clbwbi

def process_creator(ind1, subfields):
	global creatorqid
	creator_role_prop = None

	roles = {
	'aut' : 'P12',
	'edt' : 'P13',
	'edc' : 'P13'
	}
	creatordata = {'qid': False, 'statements' : {'append':[],'replace':[]}}

	for subfield in subfields:
		code = subfield.attrib['code']
		nkcr = subfield.text
		if code == "7":
			if nkcr in creatorqid:
				print('This creator is existing Qid '+creatorqid[nkcr])
				creatordata['qid'] = creatorqid[nkcr]
			else:
				print('This creator will be created as new: '+nkcr)
				creatordata['statements']['replace'].append({'type':'ExternalID', 'value':nkcr, 'prop_nr':'P8'})
				print('Querying Wikidata for NKCR AUT ID: '+nkcr+'...')
				query = 'select ?wd where {?wd wdt:P691 "'+nkcr+'".}'
				bindings = wbi_helpers.execute_sparql_query(query=query, endpoint="https://query.wikidata.org/sparql", user_agent="User:DL2204")['results']['bindings']
				if len(bindings) > 0:
					wdqid = bindings[0]['wd']['value'].replace("http://www.wikidata.org/entity/","")
					print('Found wikidata item: '+wdqid)
					creatordata['statements']['replace'].append({'type':"ExternalID", 'value':wdqid, 'prop_nr':"P1"})
				else:
					print('Nothing found on Wikidata for this NKCR AUT ID.')
		if code == "4":
			if subfield.text in roles:
				creator_role_prop = roles[subfield.text]
				print('Found creator role prop '+creator_role_prop)

		if code == "a":
			if ind1 == "1":
				creatordata['statements']['replace'].append({'type':'Item', 'value':'Q5', 'prop_nr':'P5'}) # instance of human
				lastname = subfield.text.split(",")[0]
				creatordata['statements']['replace'].append({'type':'String', 'value':lastname, 'prop_nr':'P66'})
				firstname = subfield.text.split(",")[1].strip()
				creatordata['statements']['replace'].append({'type':'String', 'value':firstname, 'prop_nr':'P65'})
			else:
				print('Unforeseen name type: ind1='+ind1+', Abort.')
				sys.exit()
		if code == "d":
			birthyear = subfield.text.split("-")[0]
			creatordata['statements']['replace'].append({'type':'Time', 'precision':11, 'time':'+'+birthyear+'-01-01T00:00:00Z', 'prop_nr':'P52'})
			deathyear = subfield.text.split("-")[1].strip()
			if len(deathyear) == 4:
				creatordata['statements']['replace'].append({'type':'Time', 'precision':11, 'time':'+'+deathyear+'-01-01T00:00:00Z', 'prop_nr':'P53'})

	if creatordata['qid'] == False:
		print('Will create new creator item')

		# clbwbi.itemwrite(creatordata)
		# return {'creator_qid':creatordata['qid'], 'creator_role_prop':creator_role_prop}
	return {'creatordata':creatordata, 'creator_role_prop':creator_role_prop}

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
	countries = {}
	for row in countrydict:
		countries[row['code']] = row['wikidata']

# load language codes mapping
with open('data/marc-languages-wikidata.csv', 'r', encoding="utf-8") as file:
	langdict = csv.DictReader(file)
	languages = {}
	for row in langdict:
		languages[row['code']] = row['wikidata']

root = tree.getroot()
if root.tag != xmlns+"collection":
	print('This input file is not MARC21 XML. Abort.')
	sys.exit()
else:
	print('Will proceed to load MARC21 XML.')

count = 0
issn_log = {}
for record in root:
	statements = {'append':[],'replace':[]}
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
			if text in recordqid:
				itemqid = text
			else:
				itemqid = False
				statements['append'].append({'type':"String",'value':text, 'prop_nr':"P8"})

		# read controlfield 008: time of publication
		if tag == "008":

			# date of publication
			prec = text[6]
			rv = {}
			if prec == "e":
				if text[13:15] != "  ":
					datetime = '+'+text[7:11]+'-'+text[11:13]+'-'+text[13:15]+'T00:00:00Z'
					precision = 9
				else:
					datetime = '+'+text[7:11]+'-'+text[11:13]+'-01T00:00:00Z'
					precision = 10
			elif prec == "s":
				datetime = '+'+text[7:11]+'-01-01T00:00:00Z'
				precision = 11
			statements['replace'].append({'type':"Time", 'time':datetime, 'precision':precision, 'prop_nr':"P15"})

			# country of publication
			try:
				countryqid = countries[text[15:18].strip()]
				print('Found publication country '+countryqid+' for '+text[15:18])
			except:
				print('Country code '+text[15:18]+' not found in country-qidmapping.\nUpdate marc-countries-wikidata.csv and restart.')
				sys.exit()
			statements['replace'].append({'type':"Item", 'value':countryqid, 'prop_nr':"P9"})

			# language of publication
			try:
				languageqid = languages[text[35:38]]
				print('Found publication language '+languageqid+' for '+text[35:38])
			except:
				print('Language code '+text[35:38]+' not found in language-qidmapping.\nUpdate marc-languges-wikidata.csv and restart.')
				sys.exit()
			statements['replace'].append({'type':"Item", 'value':languageqid, 'prop_nr':"P11"})

	for datafield in record.findall(xmlns+"datafield"):
		tag = datafield.attrib['tag']
		ind1 = datafield.attrib['ind1']
		ind2 = datafield.attrib['ind2']
		# process creators
		if tag == "100" or tag == "700":
			print(process_creator(ind1, datafield.findall(xmlns+"subfield")))
		# process title etc. (245)
		if tag == "245":
			title = None
			subtitle = None
			transtitle = None

			for subfield in datafield.findall(xmlns+"subfield"):
				code = subfield.attrib['code']
				if code == "a":
					if subfield.text.endswith("="):
						transtitle == True
						title = re.sub(' *=$',subfield.text)
					else: # do we want to replace space in title colon : subtitle ?
						title = subfield.text
				if code == "b" and title and (not transtitle): # subtitle is merged to title
					title += " "+subfield.text
				if code == "b" and title and transtitle:
					transtitle = subfield.text
			if title:
				statements['replace'].append({'type':'String', 'value':title, 'prop_nr':'P6'})
			if transtitle:
				pass # tbd. 246 is also transtitle

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
						wdqid = issn_log[value]
						print('ISSN already known as '+wdqid)
					else:
						print('Querying Wikidata for ISSN: '+value+'...')
						query = 'select ?wd where {?wd wdt:P236 "'+value+'".}'
						bindings = wbi_helpers.execute_sparql_query(query=query, endpoint="https://query.wikidata.org/sparql", user_agent="User:DL2204")['results']['bindings']
						if len(bindings) > 0:
							wdqid = bindings[0]['wd']['value'].replace("http://www.wikidata.org/entity/","")
							print('Found wikidata item: '+wdqid)
							wdquali = [{'type':'ExternalID','value':wdqid, 'prop_nr':"P1"}]
							issn_log[value] = wdqid
						else:
							print('Nothing found on Wikidata for this ISSN.')
							wdquali = []
					statements['replace'].append({'type':'ExternalID', 'value':value, 'prop_nr':'P20', 'qualifiers':wdquali})
		# process 020
		if tag == "020":
			for subfield in datafield.findall(xmlns+"subfield"):
				code = subfield.attrib['code']
				if code == "a":
					pass
					# process ISBN (TBD)

	print('\nStatements: '+str(statements))
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
