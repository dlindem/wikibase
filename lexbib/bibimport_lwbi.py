from tkinter import Tk
from tkinter.filedialog import askopenfilename
import mwclient
import traceback
import time
import sys
import os
import json
import re
#import requests
#import urllib.parse
import lwbi
import config_private

# open and load input file
print('Please select post-processed Zotero export JSON to be imported to lexbib.elex.is.')
#time.sleep(2)
Tk().withdraw()
infile = askopenfilename()
infilename = os.path.basename(infile)
print('This file will be processed: '+infilename)
try:
	with open(infile, encoding="utf-8") as f:
		jsonlines = f.read().split('\n')
		data = []
		for jsonline in jsonlines:
			try:
				data.append(json.loads(jsonline))
			except:
				pass
except Exception as ex:
	print ('Error: file does not exist.')
	print (str(ex))
	sys.exit()

totalrows = len(data)

with open(config_private.datafolder+'logs/errorlog_'+infilename+'_'+time.strftime("%Y%m%d-%H%M%S")+'.log', 'w') as errorlog:
	index = 0
	edits = 0
	rep = 0

	while index < totalrows:


		if index >= 0: #start item in infile (change if process had been aborted without finishing)
			if rep > 4: # break 'while' loop after 5 failed attempts to process item
				print ('\nbibimport.py has entered in an endless loop... abort.')
				break

			print('\n'+str(index)+' items processed. '+str(totalrows-index)+' list items left.\n')
			#time.sleep(1)
			rep += 1
			# zotitemstatement = None

			item = data[index]
			# print(str(item))
			lexBibID = item['lexBibID']
			print('LexBibID is '+lexBibID)
			itemdata = {'qid': lexBibID, 'statements':[], 'labels':[]}
			lwbitem = lwbi.wbi.item.get(entity_id=lexBibID)
			print('Successfully got access to item '+lwbitem.id)
			# if 'lexBibClass' in item and item['lexBibClass'].startswith("Q"):
			# 	classStatement = lwb.updateclaim(lexBibID,"P5",item['lexBibClass'],"item")
			if len(item['creatorvals']) > 0:
				creatortype = item['creatorvals'][0]['prop_nr'] # assumes that only one creator type is passed by zotexport.property
				#print('creator type is '+creatortype)
				# existingcreators = lwb.getclaims(lexBibID,creatortype)[1]
				try:
					existingcreators = lwbitem.claims.get(creatortype)
				except:
					existingcreators = []
				#print('existingcreators: '+str(existingcreators))
				existinglistpos = []
				if len(existingcreators) > 0:
					for existingcreator in existingcreators:
						try:
							listposquali = existingcreator.qualifiers.get('P33')
							if listposquali[0].datavalue['value']:
								#print(str(existingcreator))
								existinglistpos.append(listposquali[0].datavalue['value'])
						except:
							pass
				print('existing creator listpos: '+str(existinglistpos))
				for creatorstatement in item['creatorvals']:
					write_creator = True
					if creatorstatement['value'] == False and "qualifiers" in creatorstatement: # the typical zotero literal output from zotexport.py
						if 'qualifiers' in creatorstatement:
							for qualitriple in creatorstatement['qualifiers']:
								if qualitriple['prop_nr'] == "P33":
									actuallistpos = qualitriple['value']
									if actuallistpos in existinglistpos:
										print(qualitriple['value']+' creator listpos is already there, will skip.')
										write_creator = False
						# 	if qualitriple['property'] == "P38":
						# 		creatorliteral = qualitriple['value']
						# if skipcreator == False:
						# 	creatorstatement = {'type':'item','prop_nr':creatortype,'value':False}
							# statement = lwb.updateclaim(lexBibID,triple['property'],creatorliteral,"novalue")

					# else:
					# 	statement = lwb.updateclaim(lexBibID,triple['property'],triple['value'],triple['datatype'])
					# if skipcreator == False and "qualifiers" in triple:
					if write_creator:
						if actuallistpos == 1:
							creatorstatement['action'] = "replace"
						else:
							creatorstatement['action'] = "append"
						itemdata['statements'].append(creatorstatement)
							#lwb.setqualifier(lexBibID,triple['property'],statement, qualitriple['property'], qualitriple['value'], qualitriple['datatype'])
			langlabel = None
			englabel = None
			for statement in item['statements']:
				# if propstatement['value'] == False and "qualifiers" in triple:
				# 	for qualitriple in triple['qualifiers']:
				# 		if qualitriple['property'] == "P38":
				# 			sourceliteral = qualitriple['value']
				# 			statements.app = lwb.updateclaim(lexBibID,triple['property'],sourceliteral,"novalue")

				#else:
				#statement = lwb.updateclaim(lexBibID,triple['property'],triple['value'],triple['datatype'])
				# if "qualifiers" in triple:
				# 	for qualitriple in triple['qualifiers']:
				# 		lwb.setqualifier(lexBibID,triple['property'],statement, qualitriple['property'], qualitriple['value'], qualitriple['datatype'])
				itemdata['statements'].append(statement)
				if statement['prop_nr'] == 'P6': # title

					if statement['type'] == "monolingualtext" and statement['lang'] != "en": # label in original lang if not eng
						langlabel = {'lang':statement['lang'], 'value':statement['value']}
						itemdata['labels'].append(langlabel)
					else:
						itemdata['labels'].append({'lang':'en', 'value':statement['value']})
						enlabel = True

			if not englabel and langlabel: # enlabel by default
				itemdata['labels'].append({'lang':'en','value':langlabel['value']})

			lwbi.itemwrite(itemdata)

			rep = 0
		index += 1

print('\nFinished. Check error log.')
