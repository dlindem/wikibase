from tkinter import Tk
from tkinter.filedialog import askopenfilename
import time
import sys
import json
import csv
import re
import unidecode
import os
import shutil
import requests
import urllib.parse
import collections
# import eventmapping
import langmapping
import lwb, lwbi
import config_private
from pyzotero import zotero
pyzot = zotero.Zotero(1892855,'group',config_private.zotero_api_key)

# ask for file to process
print('Please select Zotero export JSON to be processed.')
Tk().withdraw()
infile = askopenfilename()
print('This file will be processed: '+infile)

# #load done items from previous runs
# with open(config_private.datafolder+"logs/bibimport_doneitems.txt", "r", encoding="utf-8") as donelist:
# 	done_items = donelist.read().split('\n')
done_items = []
outfilename = infile.replace('.json', '_lwb_import_data.jsonl')
if os.path.exists(outfilename):
	with open(outfilename, encoding="utf-8") as outfile:
		doneits = outfile.read().split('\n')
		count = 0
		for doneit in doneits:
			count += 1
			if doneit != "":
				try:
					doneitjson = json.loads(doneit)
					#print(doneit)
					done_items.append(doneitjson['lexBibID'])
				except Exception as ex:
					print('Found unparsable doneit json in '+outfilename+' line ['+str(count)+']: '+doneit)
					print(str(ex))
					pass
#load input file
try:
	with open(infile, encoding="utf-8") as f:
		data =  json.load(f)
		data_length = len(data)
except Exception as ex:
	print ('Error: file does not exist.')
	print (str(ex))
	sys.exit()

# load list of place-mappings

# wppage_lwbplace.jsonl
wikipairs = {}
with open(config_private.datafolder+'mappings/wppage-wdid-mappings.json', encoding="utf-8") as f:
	wikipairs_orig =  json.load(f, encoding="utf-8")
	for placename in wikipairs_orig:
		wikipairs[urllib.parse.unquote(placename)] = wikipairs_orig[placename]
print('Wikiplace-pairs loaded.')

# load list of already exported PDFs

with open('D:/LexBib/zot2wb/attachment_folders.csv', 'r', encoding="utf-8") as f:
	rows = csv.reader(f, delimiter = "\t")
	attachment_folder_list = {}
	for row in rows:
		attachment_folder_list[row[0]] = int(row[1])

# load zotero-to-wikibase link-attachment mapping

linked_done = {}
with open(config_private.datafolder+'mappings/linkattachmentmappings.jsonl', encoding="utf-8") as jsonl_file:
	mappings = jsonl_file.read().split('\n')
	count = 0
	for mapping in mappings:
		count += 1
		if mapping != "":
			try:
				mappingjson = json.loads(mapping)
				#print(mapping)
				linked_done[mappingjson['bibitem']] = {"itemkey":mappingjson['itemkey'],"attkey":mappingjson['attkey']}
			except Exception as ex:
				print('Found unparsable mapping json in linkattachmentmappings.jsonl line ['+str(count)+']: '+mapping)
				print(str(ex))
				pass

# define LexBib BibItem URI

def define_uri(item):
	# get LWB v2 legacy Qid, if any
	global linked_done
	global legacy_qid
	bibItemQid = None
	if 'archive_location' in item:
		if re.match(r'^lexbib.elex.is/Q\d+', item['archive_location']):
			legacy_qid = re.match('^Q\d+',item['archive_location']).group(0)
			bibItemQid = lwb.getidfromlegid("Q3", legacy_qid)
		elif re.match(r'https?://lexbib.elex.is/entity/(Q\d+)', item['archive_location']):
			bibItemQid = re.match(r'https?://lexbib.elex.is/entity/(Q\d+)', item['archive_location']).group(1)
			legacy_qid = None

	if not bibItemQid:	# set up new item
		print('No Qid found for "'+item['title']+'", will create new item.')
		bibItemQid = lwb.newitemwithlabel([], "en", item['title'])

	# # check if this zotId exists on LWB
	# url = "https://data.lexbib.org/query/sparql?format=json&query=PREFIX%20ldp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2F%3E%0Aselect%20%3Fqid%20where%0A%7B%3Fqid%20ldp%3AP16%20%3Chttp%3A%2F%2Flexbib.org%2Fzotero%2F"+zotitemid+"%3E.%20%7D"
	# done = False
	# while (not done):
	# 	try:
	# 		r = requests.get(url)
	# 		result = r.json()['results']['bindings']
	# 	except Exception as ex:
	# 		print('Error: SPARQL request failed: '+str(ex))
	# 		time.sleep(2)
	# 		continue
	# 	done = True
	# if len(result) > 0:
	# 	qid = result[0]['qid']['value'].replace("http://data.lexbib.org/entity/","")
	# 	print('Zotero ID '+zotitemid+' had been exported to '+qid+'; that mapping has disappeared from "archive location", will fix that...')
	#
	# 	lwb.logging.warning('Item mapping has disappeared from zotero data: ',zotitemid,qid)
	# else:


	# communicate with Zotero, write Qid to "archive location" and link to attachment (if not done before)

	zotapid = item['id'].replace("http://zotero.org/", "https://api.zotero.org/")
	zotitemid = re.search(r'items/(.*)',item['id']).group(1)

	if bibItemQid and bibItemQid not in linked_done:
		print('This item needs updated archive_loc and link attachment on Zotero.')
		attempts = 0
		while attempts < 5:
			attempts += 1
			r = requests.get(zotapid)
			if "200" in str(r):
				zotitem = r.json()
				print(zotitemid+': got zotitem data')
				break
			if "400" or "404" in str(r):
				print('*** Fatal error: Item '+zotitemid+' got '+str(r)+', does not exist on Zotero. Will skip.')
				time.sleep(5)
				break
			print('Zotero API GET request failed ('+zotitemid+'), will repeat. Response was '+str(r))
			time.sleep(2)

		if attempts < 5:
			version = zotitem['version']
			zot_qid = zotitem['data']['archiveLocation']
			if re.match(r'https?://lexbib.elex.is/entity/(Q\d+)', zot_qid):
				bibItemQid = re.match(r'https?://lexbib.elex.is/entity/(Q\d+)', zot_qid).group(1)
				legacy_qid = None
				# return bibItemQid
			elif re.match(r'^Q\d+', zot_qid):
				legacy_qid = re.match('^Q\d+',zot_qid).group(0)
				bibItemQid = lwb.getidfromlegid("Q3", legacy_qid)

		else:
			print('Abort after 5 failed attempts to get data from Zotero API.')
			sys.exit()

		#write to zotero AN field

		attempts = 0
		while attempts < 5:
			attempts += 1
			r = requests.patch(zotapid,
			headers={"Zotero-API-key":config_private.zotero_api_key},
			json={"archiveLocation":"https://lexbib.elex.is/entity/"+bibItemQid,"version":version})

			if "204" in str(r):
				print('Successfully patched zotero item '+zotitemid+': '+bibItemQid)
				# with open(config_private.datafolder+'zoteroapi/lwbqid2zotero.csv', 'a', encoding="utf-8") as logfile:
				# 	logfile.write(qid+','+zotitemid+'\n')
				break
			print('Zotero API PATCH request failed ('+zotitemid+': '+bibItemQid+'), will repeat. Response was '+str(r)+str(r.content))
			time.sleep(2)

		if attempts > 4:
			print('Abort after 5 failed attempts.')
			sys.exit()

		#check for presence of link attachment

		attempts = 0
		while attempts < 5:
			attempts += 1
			r = requests.get(zotapid+"/children")
			if "200" in str(r):
				zotitem = r.json()
				print(zotitemid+': got zotitem attachment data')
				break
			if "400" or "404" in str(r):
				print('*** Fatal error: Item '+zotitemid+' got '+str(r)+', does not exist on Zotero. Will skip.')
				time.sleep(5)
				break
			print('Zotero API GET request failed ('+zotitemid+'), will repeat. Response was '+str(r))
			time.sleep(2)

		if attempts < 5:
			att_presence = None
			for attachmnt in r.json():
				if 'title' in attachmnt['data']:
					if attachmnt['data']['title'] == "LexBib Linked Data":
						att_presence = True
						break

		if not att_presence:
			# attach link to wikibase
			attachment = [
			{
			"itemType": "attachment",
			"parentItem": zotitemid,
			"linkMode": "linked_url",
			"title": "LexBib Linked Data",
			"accessDate": "2021-08-08T00:00:00Z",
			"url": "https://lexbib.elex.is/entity/"+bibItemQid,
			"note": '<p>See this item as linked data at <a href="https://lexbib.elex.is/wiki/Item:'+bibItemQid+'">https://lexbib.elex.is/entity/'+bibItemQid+'</a>',
			"tags": [],
			"collections": [],
			"relations": {},
			"contentType": "",
			"charset": ""
			}
			]

			r = requests.post('https://api.zotero.org/groups/1892855/items', headers={"Zotero-API-key":config_private.zotero_api_key, "Content-Type":"application/json"} , json=attachment)

			if "200" in str(r):
				# print(r.json())
				try:
					attkey = r.json()['successful']['0']['key']
					linked_done[bibItemQid] = {"itemkey":zotitemid,"attkey":attkey}
					with open(config_private.datafolder+'mappings/linkattachmentmappings.jsonl', 'a', encoding="utf-8") as jsonl_file:
						jsonline = {"bibitem":bibItemQid,"itemkey":zotitemid,"attkey":attkey}
						jsonl_file.write(json.dumps(jsonline)+'\n')
					print('Zotero item link attachment successfully written and bibitem-attkey mapping stored; attachment key is '+attkey+'.')
				except:
					print('Failed writing link attachment to Zotero item '+zotitemid+' (did not return created attachment - is the zotero item really in the right collection?).')
			else:
				print('Failed writing link attachment to Zotero item '+zotitemid+' (did not respond 200).')
	print('BibItemQid successfully defined: '+bibItemQid)
	return bibItemQid

# write creator triples
def write_creatortriples(prop, val):
	global creatorvals
	listpos = 0
	for creator in val:
		listpos += 1
		if "literal" in creator: # this means there is no firstname-lastname but a single string (for Orgs):
			pass # TBD
		else:
			if "non-dropping-particle" in creator:
				creator["family"] = creator["non-dropping-particle"]+" "+creator["family"]
			if creator["family"] == "Various":
				creator["given"] = "Various"

			creatorvals.append({
			"prop_nr": prop,
			# "type": "string",
			# "value": creator["given"]+" "+creator["family"],
			# "type": "novalue",
			# "value": "novalue",
			"type": "item",
			"value": False,
			"qualifiers": [
			{"prop_nr":"P33","type":"string","value":str(listpos)},
			{"prop_nr":"P38","type":"string","value":creator["given"]+" "+creator["family"]},
			{"prop_nr":"P40","type":"string","value":creator["given"]},
			{"prop_nr":"P41","type":"string","value":creator["family"]}
			]
			})



# process Zotero export JSON

lwb_data = []
used_uri = []
seen_titles = []
new_places = []
seen_containers = {}
legacy_qid = None
itemcount = 0
for item in data:
	print("\nItem ["+str(itemcount+1)+"] of "+str(data_length)+": "+item['title'])

	p100set = None
	bibItemQid = define_uri(item)

	if bibItemQid in done_items:
		print('Item done before.')
		itemcount += 1
		# continue

	if bibItemQid in used_uri:
		print('***Fatal Error, attempt to use the same URI twice: '+bibItemQid)
		sys.exit()

	if bibItemQid == False:
		print('***Fatal Error, failed to define URI for item No. ['+str(itemcount+1)+']')
		sys.exit()
	else:
		used_uri.append(bibItemQid)

	creatorvals = []
	statements = [{"prop_nr":"P5","type":"item","value":"Q3"}] # default instance of Q3
	zotitemid = re.search(r'items/(.*)', item['id']).group(1)

	# get language codes and assign to item, title
	if 'language' not in item:
		print('This item has no language, fatal error: '+item['id'])
		item['language'] = "en"

	itemlangiso3 = langmapping.getiso3(item['language'])
	if itemlangiso3 == "nor":
		itemlangiso3 = "nbo" # "Norwegian (mixed) to Norwegian (Bokmal)"
	labellang = langmapping.getWikiLangCode(itemlangiso3)
	itemlangqid = langmapping.getqidfromiso(itemlangiso3)
	abslangqid = itemlangqid
	statements.append({"prop_nr":"P11","type":"item","value":itemlangqid})
	if 'title' in item:
		titletext = item['title']
	else:
		titletext = ''
	statements.append({"prop_nr":"P6","type":"monolingualtext","value":titletext, "lang":labellang})

	# look at other zotero properties and write RDF triples

	# lexbib zotero tags can contain statements (:shortcode[SPACE] for property, and value).
	# If Q-ID as value, and that item does not exist, it is created.
	if "tags" in item:
		for tag in item['tags']:
			if tag["tag"].startswith(':event '):
				eventcode = tag["tag"].replace(":event ","")
				# if eventcode not in eventmapping.mapping:
				# 	print('***ERROR: event not existing in lwb: '+eventcode)
				# 	sys.exit()
				# eventqid = eventmapping.mapping[eventcode]
				if re.match(r'^Q\d+', eventcode):
					eventqid = re.search(r'^Q\d+', eventcode).group(0)
					statements.append({"prop_nr":"P36","type":"item","value":eventqid})
			if tag["tag"].startswith(':container '):
				container = tag["tag"].replace(":container ","")

				if re.match(r'^Q\d+', container): # LexBib version 3 container item is already created and linked
					v3container = re.search(r'^Q\d+', container).group(0)

				elif re.match(r'^https?://', container): # old LexBib v2 container tag (landing page url)
														 # or newly added container-link
														 # (i.e. journal issue landing page URL as value for ":container") found,
														 # will be updated to v3 container tag
					containername = re.sub(r'^https?://','',container)
					print('Found http-container: '+containername)
					if containername in seen_containers:
						v3container = seen_containers[containername]
						print('Container item created before will be used: '+str(v3container))
					else:
						print('Will check if this exists already on LWB; waiting for SPARQL...')
						# check if container already exists (TBD)
						query ="""
								select ?item ?itemLabel where
								{?item ldp:P44|ldp:P111 <"""+container+"""> ; rdfs:label ?itemLabel . filter(lang(?itemLabel)="en")
								 }"""
						# sparqlresults = sparql.query('https://lexbib.elex.is/query/sparql',query)
						sparqlresults = lwbi.wbi_helpers.execute_sparql_query(query=query, prefix=lwbi.sparql_prefixes)['results']['bindings']
						print('Got '+str(len(sparqlresults))+' results.')
						#go through sparqlresults
						v3container = None
						for row in sparqlresults:
							if row['item']['value'].startswith("https://lexbib.elex.is/entity/Q"):
								v3container = row['item']['value'].replace("https://lexbib.elex.is/entity/","")
								print('This container has been found by SPARQL, will rename tag to '+v3container)
						if not v3container: # no container item found
							# create new container item

							print('Nothing found. Will create new container item.')
							# TBD: other bibitem types
							if item['type'] == "article-journal":
								if "ISSN" in item:
									if "-" not in item['ISSN']: # normalize ISSN, remove any secondary ISSN
										contissn = item['ISSN'][0:4]+"-"+item['ISSN'][4:9]
									else:
										contissn = item['ISSN'][:9]
								else:
									contissn = None

								contlabel = ""
								if "container-title" in item:
									contlabel += item['container-title']
								voliss = ""
								if "volume" in item:
									voliss += item['volume']
								if "volume" in item and "issue" in item:
									voliss += "/"
								if "issue" in item:
									voliss += item['issue']
								if voliss != "":
									voliss = " "+voliss
								contyear = ""
								if "issued" in item:
									contyear = " ("+item['issued']['date-parts'][0][0]+")"
								v3container = lwb.newitemwithlabel("Q12","en",contlabel+voliss+contyear)
								print('New container item is: '+str(v3container)+" "+contlabel+voliss+contyear)
								print('Will write container entity data.')
								lwb.itemclaim(v3container,"P5","Q16")
								if contissn:
									lwb.stringclaim(v3container,"P20",contissn)
								if "volume" in item:
									lwb.stringclaim(v3container,"P22",item['volume'])
								if "issue" in item:
									lwb.stringclaim(v3container,"P23",item['issue'])
								lwb.stringclaim(v3container,"P111",container)
								lwb.stringclaim(v3container,"P97",contlabel+voliss+contyear)

						# update zotero container tags for all items that point to this container
						print('Will now update zotero tags to v3 container tag...')
						tagzotitems = pyzot.items(tag=":container "+container)
						for tagzotitem in tagzotitems:
							pyzot.add_tags(tagzotitem, ":container "+v3container)
							print('container-tag '+v3container+' written to '+tagzotitem['key'])
							time.sleep(0.2)
						pyzot.delete_tags(":container "+container)
						print('Zotero container tag '+container+' updated to '+v3container)
						seen_containers[containername] = v3container

				statements.append({"prop_nr":"P9","type":"item","value":v3container}) # container relation

			if tag["tag"].startswith(':type '):
				type = tag["tag"].replace(":type ","")
				if type == "Review":
					statements.append({"prop_nr":"P5","type":"item","value":"Q15"})
				elif type == "Report":
					statements.append({"prop_nr":"P5","type":"item","value":"Q25"})
				elif type == "Proceedings":
					statements.append({"prop_nr":"P5","type":"item","value":"Q18"})
				elif type == "DictionaryDistribution":
					statements.append({"prop_nr":"P5","type":"item","value":"Q24"}) # LCR distribution
				elif type == "e-Dict":
					#lexbibClass = "Q13" # this overrides "Q3"
					p100set = True # this overrides "book" (Zotero type computer program is mapped to book)
					statements.append({"prop_nr":"P100","type":"item","value":"Q13"})
				elif type == "Community":
					statements.append({"prop_nr":"P5","type":"item","value":"Q26"})

			if tag["tag"].startswith(':collection '):
				coll = tag["tag"].replace(":collection ","")
				statements.append({"prop_nr":"P85","type":"string","value":coll})

			if tag["tag"].startswith(':abstractLanguage '):
				abslangcode = tag["tag"].replace(":abstractLanguage ","")
				abslangiso3 = langmapping.getiso3(abslangcode)
				abslangqid = langmapping.getqidfromiso(abslangiso3)

			if tag["tag"].startswith(':enTitle'): # this means zotero field "collection-title" contains the English title of the publication
				if 'collection-title' in item:
					statements.append({"prop_nr":"P6","type":"monolingualtext","value":item['collection-title'], "lang":"en"})
					print('Detected English title in field collection-title')
				else:
					print('*** English title in field collection-title not found.')

	### bibitem type mapping

	if "type" in item and (not p100set): # ; p100set=True skips type setting
		if item['type'] == "paper-conference":
			statements.append({"prop_nr":"P100","type":"item","value":"Q27"})
		elif item['type'] == "article-journal":
			statements.append({"prop_nr":"P100","type":"item","value":"Q19"})
		elif item['type'] == "book":
			statements.append({"prop_nr":"P100","type":"item","value":"Q28"})
		elif item['type'] == "chapter":
			statements.append({"prop_nr":"P100","type":"item","value":"Q29"})
		elif item['type'] == "motion_picture": # videos
			statements.append({"prop_nr":"P100","type":"item","value":"Q30"})
		elif item['type'] == "speech":
			statements.append({"prop_nr":"P100","type":"item","value":"Q31"})
		elif item['type'] == "thesis":
			statements.append({"prop_nr":"P100","type":"item","value":"Q32"})

	# Zotero ID, and, as qualifiers: abstract info, PDF ant TXT file attachments

	att_quali = []
	if "abstract" in item:
		if len(item['abstract']) > 20: # accept literal longer than 20 chars as abstract text
			att_quali.append({"prop_nr":"P105","type":"item","value":abslangqid})
	if "attachments" in item:
		txtfolder = None
		txttype = None
		pdffolder = None
		for attachment in item['attachments']:
			if attachment['contentType'] == "application/pdf" and not pdffolder: # takes only the first PDF
				pdfloc = re.search(r'(D:\\Zotero\\storage)\\([A-Z0-9]+)\\(.*)', attachment['localPath'])
				pdfpath = pdfloc.group(1)
				pdffolder = pdfloc.group(2)
				pdfoldfile = pdfloc.group(3)
				pdfnewfile = pdffolder+".pdf" # rename file to <folder>.pdf
				if pdffolder not in attachment_folder_list or attachment_folder_list[pdffolder] < attachment['version']:
					copypath = 'D:\\LexBib\\zot2wb\\grobid_upload\\'+pdffolder
					if not os.path.isdir(copypath):
						os.makedirs(copypath)
					shutil.copy(pdfpath+'\\'+pdffolder+'\\'+pdfoldfile, copypath+'\\'+pdfnewfile)
					print('Found and copied to GROBID upload folder '+pdfnewfile)
					attachment_folder_list[pdffolder] = attachment['version']
					# save new PDF location to listfile
					with open('D:/LexBib/zot2wb/attachment_folders.csv', 'a', encoding="utf-8") as attachment_folder_listfile:
						attachment_folder_listfile.write(pdffolder+"\t"+str(attachment['version'])+"\n")
				att_quali.append({"prop_nr":"P70","type":"string","value":pdffolder})
			elif attachment['contentType'] == "text/plain": # prefers cleantext or any other over grobidtext
				txtloc = re.search(r'(D:\\Zotero\\storage)\\([A-Z0-9]+)\\(.*)', attachment['localPath']).group(2)
				filetype = None
				if ("GROBID" not in attachment['title']) and ("pdf2txt" not in attachment['title']) and ("pdf2text" not in attachment['title']):
					txtfolder = txtloc
					txttype = "clean"
				elif txttype != "clean" and ("pdf2txt" not in attachment['title']) and ("pdf2text" not in attachment['title']):
					txtfolder = txtloc
					txttype = "GROBID or other"
			elif attachment['contentType'] == "" and "url" in attachment:
				if attachment['url'].startswith("https://wikibase.inguma.eus/entity/Q"): # Inguma Wikibase URI attached to Zotero item
					statements.append({"prop_nr":"P174","type":"externalid","value":attachment['url'].replace("https://wikibase.inguma.eus/entity/","")})
		if txtfolder:
			att_quali.append({"prop_nr":"P71","type":"string","value":txtfolder})

	statements.append({"prop_nr":"P16","type":"string","value":zotitemid, "action":"replace", "qualifiers":att_quali})

	### props with literal value

	if "publisher" in item:
		vallist = item['publisher'].split(";")
		for val in vallist:
			statements.append({"prop_nr":"P35","type":"item","value":False,"qualifiers": [
			{"prop_nr":"P38","type":"string","value":val.strip()}]})
	if "DOI" in item:
		if "http://" in item['DOI'] or "https://" in item['DOI']:
			val = re.search(r'/(10\..+)$', item['DOI']).group(1)
		statements.append({"prop_nr":"P17","type":"string","value":item['DOI']})
	if "ISSN" in item:
		if "-" not in item['ISSN']: # normalize ISSN, remove any secondary ISSN
			item['ISSN'] = item['ISSN'][0:4]+"-"+item['ISSN'][4:9]
		statements.append({"prop_nr":"P20","type":"string","value":item['ISSN'][:9]})
	if "ISBN" in item:
		val = item['ISBN'].replace("-","") # normalize ISBN, remove any secondary ISBN
		val = re.search(r'^\d+',val).group(0)
		if len(val) == 10:
			statements.append({"prop_nr":"P19","type":"string","value":val})
		elif len(val) == 13:
			statements.append({"prop_nr":"P18","type":"string","value":val})
	if "volume" in item and item['type'] == "article-journal": # accept 'volume' only for journals (book series also have "volume", which cannot be mapped to P22)
		statements.append({"prop_nr":"P22","type":"string","value":item['volume']})
	if "issue" in item and item['type'] == "article-journal": # issue only for journals
		statements.append({"prop_nr":"P23","type":"string","value":item['issue']})
	if "page" in item:
		statements.append({"prop_nr":"P24","type":"string","value":item['page']})
	# "journalAbbreviation":
	# 	statements.append({"prop_nr":"P54","type":"string","value":val})
	if "URL" in item:
		if item['URL'].endswith(".pdf"):
			statements.append({"prop_nr":"P113","type":"url","value":item['URL']})
		else:
			statements.append({"prop_nr":"P112","type":"url","value":item['URL']})
	if "issued" in item:
		val = item['issued']
		year = val['date-parts'][0][0]
		precision = 9
		if len(val["date-parts"][0]) > 1:
			month = str(val["date-parts"][0][1])
			if len(month) == 1:
				month = "0"+month
			precision = 10
		else:
			month = "01"
		if len(val["date-parts"][0]) > 2:
			day = str(val["date-parts"][0][2])
			if len(day) == 1:
				day = "0"+day
			precision = 11
		else:
			day = "01"
		timestr = "+"+year+"-"+month+"-"+day+"T00:00:00Z"
		statements.append({"prop_nr":"P15","type":"time", "time":timestr,"precision":precision})
	if "edition" in item:
		statements.append({"prop_nr":"P64","type":"string","value":item['edition']})

	# creators

	if "author" in item:
		write_creatortriples("P12", item['author'])
	elif ("author" not in item) and ("editor" in item):
		write_creatortriples("P13", item['editor'])

	# Extra field, can contain a wikipedia page title, used in Elexifinder project as first-author-location-URI

	if "extra" in item:
		wppage = urllib.parse.unquote(item['extra'].replace("\n","").replace(" ","").split(";")[0].replace("http://","https://"))

		if "https://en.wikipedia.org/wiki/" in wppage:
			print('Found authorloc wppage: '+wppage)
			# check if this location is already in LWB, if it doesn't exist, create it
			wppagetitle = wppage.replace("https://en.wikipedia.org/wiki/","")
			if wppagetitle not in wikipairs:
				wdjsonsource = requests.get(url='https://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&format=json&titles='+wppage)
				wdjson =  wdjsonsource.json()
				entities = wdjson['entities']
				for wdid in entities:
					print("found new wdid on wikidata"+wdid+" for AUTHORLOC "+wppage)
					placeqid = lwb.wdid2lwbid(wdid)
			else:
				wdid = wikipairs[wppagetitle]
				placeqid = lwb.wdid2lwbid(wdid)
			if placeqid:
					print("This is a known authorloc: "+placeqid)
			else:
				print("This is a place unknown to LWB, will be created: "+wppagetitle)
				placeqid = lwb.newitemwithlabel("Q9", "en", wppagetitle)
				wdstatement = lwb.stringclaim(placeqid, "P2", wdid)
				wpstatement = lwb.stringclaim(placeqid, "P66", wppage)
				lwb.save_wdmapping({"lwbid": placeqid, "wdid": wdid})
				lwb.wdids[placeqid] = wdid
				new_places.append({"placeQid":placeqid,"wppage":wppage, "wdid":wdid})
			statements.append({"prop_nr":"P29","type":"item","value":placeqid})


		else:
			print('Found NO authorloc wppage.')

		oclc_re = re.search(r'OCLC: (\d+)',item['extra'])
		if oclc_re:
			oclc = oclc_re.group(1)
			statements.append({"prop_nr":"P62","type":"string","value":oclc})
			print('Found OCLC in EXTRA field.')
		else:
			print('No OCLC found.')


	with open(outfilename, 'a', encoding="utf-8") as outfile:
		outfile.write(json.dumps({"lexBibID":bibItemQid,"creatorvals":creatorvals,"statements":statements})+'\n')
	print('Triples for bibimport.py successfully defined.')
	itemcount += 1



print(str(json.dumps(lwb_data)))
# with open(infile.replace('.json', '_lwb_import_data.json'), 'w', encoding="utf-8") as json_file: # path to result JSON file
# 	json.dump(lwb_data, json_file, indent=2)
print("\n=============================================\nFinished. "+infile.replace('.json', '_lwb_import_data.jsonl')+". Finished.")
print("Now you probably will run bibimport, update placemapping, grobidupload\n")
print('New places:')
print(str(new_places))
with open('newplaces.json', 'a', encoding="utf-8") as placesfile:
	json.dump(new_places, placesfile, indent=2)

# save known wikipedia-wikidata mappings to file
with open(config_private.datafolder+'mappings/wppage-wdid-mappings.json', 'w', encoding="utf-8") as mappingfile:
	json.dump(wikipairs, mappingfile, ensure_ascii=False, indent=2)
print('\nsaved known Wikipedia-Wikdiata mappings.')
