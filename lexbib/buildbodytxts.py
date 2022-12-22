
import re
import json
import os
import csv
from collections import OrderedDict
from datetime import datetime
import shutil
import sys
import sparql
import json
import requests
import config
import nlp
import time

# load bodytxt collection built in previous iterations
with open(config.datafolder+'bodytxt/bodytxt_collection.json', encoding="utf-8") as infile:
	bodytxtcoll = json.load(infile)

#get bibitems to process
query = """
PREFIX lwb: <https://lexbib.elex.is/entity/>
PREFIX ldp: <https://lexbib.elex.is/prop/direct/>
PREFIX lp: <https://lexbib.elex.is/prop/>
PREFIX lps: <https://lexbib.elex.is/prop/statement/>
PREFIX lpq: <https://lexbib.elex.is/prop/qualifier/>

select

?bibItem
(sample(?txtfolder) as ?txt)
(sample(?pdffolder) as ?pdf)
?zotero
?isolang
?abstractLang

where
{
  #BIND(lwb:Q1605 as ?bibItem)

  ?bibItem ldp:P5 lwb:Q3 .
  filter not exists {?bibItem ldp:P100 lwb:Q24.} # exclude dictionaries (only allow metalexicography)
  ?bibItem ldp:P11 ?lang . ?lang ldp:P32 ?isolang .
  #filter(?lang = lwb:Q201 || ?lang = lwb:Q204) # English or Spanish only
  ?bibItem ldp:P85 ?coll . # Items with Elexifinder collection only
  ?bibItem lp:P16 ?zoterostatement .
  ?zoterostatement lps:P16 ?zotero .
 OPTIONAL{?zoterostatement lpq:P70 ?pdffolder .}
 OPTIONAL{?zoterostatement lpq:P71 ?txtfolder .}
 OPTIONAL{?zoterostatement lpq:P105 ?abstractLang . filter(?abstractLang = lwb:Q201)}
 }
group by ?bibItem ?txt ?pdf ?zotero ?isolang ?abstractLang
"""
print(query)

url = "https://lexbib.elex.is/query/sparql"
print("Waiting for SPARQL...")
sparqlresults = sparql.query(url,query)
print('\nGot bibItem list from LexBib SPARQL.')

sourcecount = {'failed':0,'manual_txt':0,'grobid':0,'zotero_pdf2text':0,'zotero_abstract':0,'zotero_title':0, 'zotero_english_abstract':0}

#go through sparqlresults
rowindex = 0
for row in sparqlresults:
	rowindex += 1
	item = sparql.unpack_row(row, convert=None, convert_type={})
	print('\nNow processing item ['+str(rowindex)+']:\n'+str(item))
	bibItem = item[0].replace("https://lexbib.elex.is/entity/","")


	# check if already processed
	if bibItem in bodytxtcoll:
		if bodytxtcoll[bibItem]['source'] == 'manual_txt':
			print(bibItem+' is in bodytxtcoll already with manual txt, skipped.')
		continue

	if item[1]:
		txtFolder = item[1]
	else:
		txtFolder = None
	if item[2]:
		pdfFolder = item[2]
	else:
		pdfFolder = None
	zotItem = item[3]
	if item[4]:
		lang = item[4].replace("https://lexbib.elex.is/entity/","")
	else:
		lang = None
	enAbstract = False
	if item[5] == "https://lexbib.elex.is/entity/Q201":
		enAbstract = True

	# load txt. Try (1), txt file manually attached to Zotero item (excluding manually attached pdf2text and grobidbody files), (2) GROBID body TXT, (3) pdf2txt Zotero cache file, (4) abstract, (5) title

	bodytxt = None
	bodytxtsource = None

	#check if manual txt is available. Files named "pdf2text.txt" are not manual txts and are excluded
	if txtFolder:
		path = "D:/Zotero/storage/"
		print('TxtFolder contains: '+str(os.listdir(path+txtFolder)))
		for file in os.listdir(path+txtFolder):
			if file.endswith("pdf2text.txt") or file.endswith("grobidbody.txt") or file.endswith("zotero-ft-cache"):
				continue
			print("Found manually attached txt file: "+path+txtFolder+'/'+file)
			with open(path+txtFolder+'/'+file, "r", encoding="utf-8", errors="ignore") as txtfile:
				bodytxt = txtfile.read().replace('\r', ' ').replace('\n', ' ')
				bodytxtsource = "manual_txt"
			break

	if bodytxt == None and pdfFolder:
		#check if grobid output is available
		try:
			path="D:/LexBib/zot2wb/grobid_download/"
			pdfFolder = pdfFolder.replace("http://lexbib.org/zotero/","")
			for file in os.listdir(path+pdfFolder):
				if file.endswith(".tei.xml"):
					print('Found grobid TEI XML')
					bodytxt = nlp.getgrobidbody(path+pdfFolder+'/'+file)
					bodytxtsource = "grobid"
					break
		except Exception as ex:
			print('Access to Grobid output failed. '+str(ex))

	if bodytxt == None and pdfFolder:
		#check out zotero full text cache
		try:
			path = "D:/Zotero/storage/"
			pdfFolder = pdfFolder.replace("http://lexbib.org/zotero/","")
			for file in os.listdir(path+pdfFolder):
				if file.endswith("zotero-ft-cache"):
					print("Found Zotero full text cache file")
					print(path+pdfFolder+'/'+file)
					with open(path+pdfFolder+'/'+file, "r", encoding="utf-8", errors="ignore") as txtfile:
						bodytxt = txtfile.read().replace('\n', ' ')
						bodytxtsource = "zotero_pdf2text"
						break
		except Exception as ex:
			print('Access to Zotero Full Text cache failed. '+str(ex))

	if bodytxt == None and zotItem:
		# check if abstract is available from Zotero. *** TBD: ":abstractLanguage"
		print('Will now try to get abstract text from Zotero...')
		#time.sleep(2)
		try:
			request_uri = "https://api.zotero.org/groups/1892855/items/"+zotItem
			r = requests.get(request_uri)
			#print(str(r.json()))
			if 'abstractNote' in r.json()['data']:
				bodytxt = r.json()['data']['abstractNote'].replace("\n", " ")
				bodytxtsource = "zotero_abstract"
				print('Took Zotero abstract as bodytxt')
			if bodytxt == None or len(str(bodytxt)) < len(r.json()['data']['title']): #if abstract field was empty or shorter than item title
				bodytxt = r.json()['data']['title']
				bodytxtsource = "zotero_title"
				print('Took Zotero title as bodytxt')
		except Exception as ex:
			print('Access to Zotero API failed. '+str(ex))
			time.sleep(4)

	if bodytxt:
		if lang in list(nlp.sp.keys()):
			bodylemclean = nlp.lemmatize_clean(bodytxt, lang=lang)
		else:
			print('Language '+lang+' not implemented in nlp.py, will check for English abstract.')
			if enAbstract:
				print('Will now try to get abstract text from Zotero...')
				#time.sleep(2)
				try:
					request_uri = "https://api.zotero.org/groups/1892855/items/"+zotItem
					r = requests.get(request_uri)
					#print(str(r.json()))
					if 'abstractNote' in r.json()['data']:
						enabstxt = r.json()['data']['abstractNote'].replace("\n", " ")
						bodytxtsource = "zotero_english_abstract"
						bodylemclean = nlp.lemmatize_clean(enabstxt, lang="eng")
						print('Took Zotero English abstract for bodylem, not replacing non-English bodytxt.')
				except Exception as ex:
					print('Access to Zotero API failed. '+str(ex))
					time.sleep(4)
			else:
				print('No English abstract. Skipped lemmatization.')
				bodylemclean = None
		bodytxtcoll[bibItem] = {'zotItem': zotItem, 'source': bodytxtsource, 'lang': lang, 'bodytxt': bodytxt, 'bodylemclean' : bodylemclean}
	else:
		bodytxtsource = "failed"
		with open(config.datafolder+'/bodytxt/bodytxt_failed.txt', 'a', encoding="utf-8") as failed_list:
			failed_list.write(bibItem+'\n')

	sourcecount[bodytxtsource] += 1

	# # communicate with Zotero, write Qid to "archive location"
	# zotapid = zotItem.replace("http://lexbib.org/zotero/", "https://api.zotero.org/groups/1892855/items/")
	# zotitemid = zotItem.replace("http://lexbib.org/zotero/", "")
	# attempts = 0
	# while attempts < 5:
	# 	try:
	# 		attempts += 1
	# 		r = requests.get(zotapid)
	# 		if "200" in str(r):
	# 			zotitem = r.json()
	# 			print(zotitemid+': got zotitem data')
	# 			break
	# 		if "400" or "404" in str(r):
	# 			print('*** Fatal error: Item ('+zotitemid+') got '+str(r)+', does not exist on Zotero. Will skip.')
	# 			time.sleep(5)
	# 			break
	# 		print('Zotero API GET request failed ('+zotitemid+'), will repeat. Response was '+str(r))
	# 		time.sleep(2)
	# 	except Exception as ex:
	# 		print(str(ex))
	# 	print('Zotero API read request failed '+str(attempts)+' times.')
	# 	time.sleep(3)
	#
	# if attempts < 5:
	# 	version = zotitem['version']
	# 	tags = zotitem['data']['tags']
	# else:
	# 	print('Abort after 5 failed attempts to get data from Zotero API.')
	# 	sys.exit()
	#
	# #update fulltextsource tag
	# tagupdatedone = False
	# newtags = []
	# for tag in tags:
	# 	if tag['tag'].startswith("_ft_"):
	# 		if tag['tag'] == "_ft_"+bodytxtsource:
	# 			tagupdatedone = True
	# 			print('Zotero fulltextsource tag is already there, with accurate value.')
	# 			newtags.append(tag)
	# 		else:
	# 			print('Will delete unaccurate ft source tag: '+tag['tag'])
	# 	else:
	# 		newtags.append(tag)
	#
	# if tagupdatedone == False:
	# 	newtags.append({'tag':'_ft_'+bodytxtsource})
	#
	# 	#write to zotero
	# 	attempts = 0
	# 	while attempts < 5:
	# 		attempts += 1
	# 		try:
	# 			r = requests.patch(zotapid,
	# 			headers={"Zotero-API-key":config.zotero_api_key},
	# 			json={"tags":newtags,"version":version})
	#
	# 			if "204" in str(r):
	# 				print('Successfully written ft source tag to zotero item '+zotitemid+'.')
	# 				break
	# 			print('Zotero API PATCH request failed ('+zotitemid+'), will repeat. Response was '+str(r)+str(r.content))
	# 			time.sleep(2)
	# 		except Exception as ex:
	# 			print(str(ex))
	# 		print('Zotero API patch request failed '+str(attempts)+' times.')
	# 		time.sleep(3)
	#
	# 	else:
	# 		print('Abort after 5 failed attempts.')
	# 		sys.exit()
	#
	# 	#time.sleep(5)


with open(config.datafolder+'bodytxt/bodytxt_collection.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(bodytxtcoll, json_file, indent=2)
with open(config.datafolder+'bodytxt/bodytxt_sourcecount.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(sourcecount, json_file, indent=2)
print('\n\nFinished writing output files. Bodytxtcoll has now '+str(len(bodytxtcoll))+' bodytxt items.')
print('Used sources: '+str(sourcecount))
