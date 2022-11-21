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
import lwb
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
			else:
				print('\n'+str(index)+' items processed. '+str(totalrows-index)+' list items left.\n')
				#time.sleep(1)
				rep += 1
				# zotitemstatement = None
				try:
					item = data[index]
					lexBibID = item['lexBibID']
					print('LexBibID is '+lexBibID)
					if 'lexBibClass' in item and item['lexBibClass'].startswith("Q"):
						classStatement = lwb.updateclaim(lexBibID,"P5",item['lexBibClass'],"item")
					if len(item['creatorvals']) > 0:
						creatortype = item['creatorvals'][0]['property'] # assumes that only one creator type is passed by zotexport.property
						#print('creator type is '+creatortype)
						existingcreators = lwb.getclaims(lexBibID,creatortype)[1]
						#print('existingcreators: '+str(existingcreators))
						existinglistpos = []
						if existingcreators and (creatortype in existingcreators):
							for existingcreator in existingcreators[creatortype]:
								if "qualifiers" in existingcreator and "P33" in existingcreator['qualifiers']:
									#print(str(existingcreator))
									existinglistpos.append(existingcreator['qualifiers']["P33"][0]['datavalue']['value'])
						print('existing creator listpos: '+str(existinglistpos))
						for triple in item['creatorvals']:
							skipcreator = False
							if triple['datatype'] == "novalue" and "Qualifiers" in triple:
								for qualitriple in triple['Qualifiers']:
									if qualitriple['property'] == "P33":
										if qualitriple['value'] in existinglistpos:
											print(qualitriple['value']+' creator listpos is already there, skipped.')
											skipcreator = True
									if qualitriple['property'] == "P38":
										creatorliteral = qualitriple['value']
								if skipcreator == False:
									statement = lwb.updateclaim(lexBibID,triple['property'],creatorliteral,"novalue")

							else:
								statement = lwb.updateclaim(lexBibID,triple['property'],triple['value'],triple['datatype'])
							if skipcreator == False and "Qualifiers" in triple:
								for qualitriple in triple['Qualifiers']:
									lwb.setqualifier(lexBibID,triple['property'],statement, qualitriple['property'], qualitriple['value'], qualitriple['datatype'])

					for triple in item['propvals']:
						if triple['datatype'] == "novalue" and "Qualifiers" in triple:
							for qualitriple in triple['Qualifiers']:
								if qualitriple['property'] == "P38":
									sourceliteral = qualitriple['value']
									statement = lwb.updateclaim(lexBibID,triple['property'],sourceliteral,"novalue")

						else:
							statement = lwb.updateclaim(lexBibID,triple['property'],triple['value'],triple['datatype'])
						if "Qualifiers" in triple:
							for qualitriple in triple['Qualifiers']:
								lwb.setqualifier(lexBibID,triple['property'],statement, qualitriple['property'], qualitriple['value'], qualitriple['datatype'])




				except Exception as ex:
					traceback.print_exc()
					lwb.logging.error('bibimport.py: Error at input line ['+str(index+1)+'] '+item['lexBibID']+':'+str(ex))
					continue

				rep = 0
		index += 1

print('\nFinished. Check error log.')
