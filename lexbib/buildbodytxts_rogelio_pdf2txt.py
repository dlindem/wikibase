

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
import lwb
import time

langmap = {
}


# load bodytxt collection built in previous iterations
try:
	with open('D:/Rogelio/bodytxt_collection_rogelio.json', encoding="utf-8") as infile:
		bodytxtcoll = json.load(infile)
except:
	print('Failed to load json infile. Starting from scratch.')
	bodytxtcoll = {}

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
?lang

where
{
  #BIND(lwb:Q1605 as ?bibItem)

  ?bibItem ldp:P5 lwb:Q3 .
  filter not exists{?bibItem ldp:P100 lwb:Q30.} # no videos
  ?bibItem ldp:P11 ?lang .
  filter(?lang = lwb:Q204 || ?lang = lwb:Q201) # Spanish and English only
  #?bibItem ldp:P85 ?coll . # Items with Elexifinder collection only
  ?bibItem lp:P16 ?zoterostatement .
  ?zoterostatement lps:P16 ?zotero .
 OPTIONAL{?zoterostatement lpq:P70 ?pdffolder .}
 OPTIONAL{?zoterostatement lpq:P71 ?txtfolder .}
 }
group by ?bibItem ?txt ?pdf ?zotero ?lang
"""
print(query)

url = "https://lexbib.elex.is/query/sparql"
print("Waiting for SPARQL...")
sparqlresults = sparql.query(url,query)
print('\nGot bibItem list from LexBib SPARQL.')

sourcecount = {'failed':0,'manual_txt':0,'grobid':0,'zotero_pdf2text':0,'zotero_abstract':0,'zotero_title':0}

#go through sparqlresults
rowindex = 0
for row in sparqlresults:
	rowindex += 1
	item = sparql.unpack_row(row, convert=None, convert_type={})
	print('\nNow processing item ['+str(rowindex)+']:\n'+str(item))
	bibItem = item[0].replace("https://lexbib.elex.is/entity/","")


	# check if already processed
	# if bibItem in bodytxtcoll:
	# 	if bodytxtcoll[bibItem]['source'] == 'zotero_pdf2text':
	# 		print(bibItem+' is in bodytxtcoll already as zotero_pdf2text, skipped.')
	# 		continue

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
		if item[4] in langmap:
			lang = langmap[item[4]]
		else:
			p32claims = lwb.getclaims(item[4].replace("https://lexbib.elex.is/entity/",""),"P32")[1]
			print(str(p32claims))
			lang = p32claims['P32'][0]['mainsnak']['datavalue']['value']
			print('Found and mapped new language '+lang)
			time.sleep(2)
			langmap[item[4]] = lang
	else:
		lang = None

	# load txt. Try (1), txt file manually attached to Zotero item (excluding manually attached pdf2text and grobidbody files), (2) GROBID body TXT, (3) pdf2txt Zotero cache file, (4) abstract, (5) title

	bodytxt = None
	bodytxtsource = None

	if pdfFolder:
		try:
			path = "D:/Zotero/storage/"
			pdfFolder = pdfFolder.replace("http://lexbib.org/zotero/","")
			shutil.copytree(path+pdfFolder,"D:/Rogelio/pdffolders/"+pdfFolder)
			print('Found and copied PDF folder: '+pdfFolder)
		except Exception as ex:
			print('Copying file failed. '+str(ex))

	#check if manual txt is available. Files named "pdf2text.txt" are not manual txts and are excluded
	# if txtFolder:
	# 	path = "D:/Zotero/storage/"
	# 	print('TxtFolder contains: '+str(os.listdir(path+txtFolder)))
	# 	for file in os.listdir(path+txtFolder):
	# 		if file.endswith("pdf2text.txt") or file.endswith("grobidbody.txt") or file.endswith("zotero-ft-cache"):
	# 			continue
	# 		print("Found manually attached txt file: "+path+txtFolder+'/'+file)
	# 		with open(path+txtFolder+'/'+file, "r", encoding="utf-8", errors="ignore") as txtfile:
	# 			bodytxt = txtfile.read().replace('\r', ' ').replace('\n', ' ')
	# 			bodytxtsource = "manual_txt"
	# 		break

	# if bodytxt == None and pdfFolder:
	# 	#check if grobid output is available
	# 	try:
	# 		path="D:/LexBib/zot2wb/grobid_download/"
	# 		pdfFolder = pdfFolder.replace("http://lexbib.org/zotero/","")
	# 		for file in os.listdir(path+pdfFolder):
	# 			if file.endswith(".tei.xml"):
	# 				print('Found grobid TEI XML')
	# 				bodytxt = nlp.getgrobidbody(path+pdfFolder+'/'+file)
	# 				bodytxtsource = "grobid"
	# 				break
	# 	except Exception as ex:
	# 		print('Access to Grobid output failed. '+str(ex))

	if pdfFolder:
		#check out zotero full text cache
		try:
			path = "D:/Zotero/storage/"
			pdfFolder = pdfFolder.replace("http://lexbib.org/zotero/","")
			for file in os.listdir(path+pdfFolder):
				if file.endswith("zotero-ft-cache"):
					print("Found Zotero full text cache file")
					print(path+pdfFolder+'/'+file)
					with open(path+pdfFolder+'/'+file, "r", encoding="utf-8", errors="ignore") as txtfile:
						bodytxt = txtfile.read() # .replace('\n', ' ')
						bodytxtsource = "zotero_pdf2text"
						break
		except Exception as ex:
			print('Access to Zotero Full Text cache failed. '+str(ex))

	# if bodytxt == None and zotItem:
	# 	# check if abstract is available from Zotero. *** TBD: ":abstractLanguage"
	# 	print('Will now try to get abstract text from Zotero...')
	# 	#time.sleep(2)
	# 	try:
	# 		request_uri = "https://api.zotero.org/groups/1892855/items/"+zotItem
	# 		r = requests.get(request_uri)
	# 		#print(str(r.json()))
	# 		if 'abstractNote' in r.json()['data']:
	# 			bodytxt = r.json()['data']['abstractNote'].replace("\n", " ")
	# 			bodytxtsource = "zotero_abstract"
	# 			print('Took Zotero abstract as bodytxt')
	# 		if bodytxt == None or len(str(bodytxt)) < len(r.json()['data']['title']): #if abstract field was empty or shorter than item title
	# 			bodytxt = r.json()['data']['title']
	# 			bodytxtsource = "zotero_title"
	# 			print('Took Zotero title as bodytxt')
	# 	except Exception as ex:
	# 		print('Access to Zotero API failed. '+str(ex))
	# 		time.sleep(4)

	if bodytxt:
		bodytxt = nlp.check_encoding(bodytxt, txtname=bibItem)
		#bodylemclean = nlp.lemmatize_clean(bodytxt, lang="spa")
		bodytxtcoll[bibItem] = {'lexbibEntity':'https://lexbib.elex.is/entity/'+bibItem, 'pdfFolder': pdfFolder, 'zotItem': zotItem, 'source': bodytxtsource, 'lang': lang, 'bodytxt': bodytxt} #, 'bodylemclean' : bodylemclean}
	else:
		bodytxtsource = "failed"
		with open('D:/Rogelio/bodytxt_rogelio_failed.txt', 'a', encoding="utf-8") as failed_list:
			failed_list.write(bibItem+'\n')

	sourcecount[bodytxtsource] += 1

	# save txt for Rogelio
	if bodytxt:
		with open('D:/Rogelio/pdf2text/'+bibItem+'.txt', 'w', encoding="utf-8") as target_txt:
			target_txt.write(bodytxt)

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


with open('D:/Rogelio/bodytxt_collection_rogelio.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(bodytxtcoll, json_file, indent=2)
with open('D:/Rogelio/bodytxt_sourcecount.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(sourcecount, json_file, indent=2)
print('\n\nFinished writing output files. Bodytxtcoll has now '+str(len(bodytxtcoll))+' bodytxt items.')

print('Used sources: '+str(sourcecount))
