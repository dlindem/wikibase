import euswbi
import json, re, time, sys
eginda = """336
337
338
339
340
"""
eginlist = eginda.split('\n')

arloa = "sare_sozialak"
schemeqid = "Q5964"
refqid = "Q7631" # UZEI dict.

# load items to import
with open('pdf2dict/sare_sozialak.json', 'r') as jsonfile:
	source = json.load(jsonfile)
	for entry in source:
		# if int(entry['id']) < 306:
		# 	continue
		itemdata = {'qid':False, 'statements':[], 'labels':[], 'aliases':[], 'descriptions':[]}
		# id
		termid = arloa+'_'+entry['id'].rjust(3, '0')
		if termid in eginlist:
			print('Skip',termid)
			continue
		itemdata['statements'].append({'type':'string', 'prop_nr':'P15', 'value':termid,
		'references':[{'type':'item','prop_nr':'P17','value':refqid}]})
		# scheme
		itemdata['statements'].append({'type':'item', 'prop_nr':'P6', 'value':schemeqid})
		# labels
		itemdata['labels'].append({'lang':'eu', 'value':entry['eusterm']})
		itemdata['statements'].append({'type':'string', 'prop_nr':'P8', 'value':entry['eusterm'],
		'references':[{'type':'item','prop_nr':'P17','value':refqid}],
		'qualifiers':[{'type':'string','prop_nr':'P18','value':entry['eustermqual']}]})
		# aliases
		for sin in entry['sins']:
			itemdata['aliases'].append({'lang':'eu', 'value':sin['sin']})
			itemdata['statements'].append({'type':'string', 'prop_nr':'P8', 'value':entry['eusterm'],
			'references':[{'type':'item','prop_nr':'P17','value':refqid}],
			'qualifiers':[{'type':'string','prop_nr':'P18','value':entry['eustermqual']}]})

		if len(entry['eusdef']) > 1:
			itemdata['statements'].append({'type':'string', 'prop_nr':'P13', 'value':entry['eusdef'], 'references':[{'type':'item','prop_nr':'P17','value':refqid}]})
		langs = ['es', 'fr', 'en']
		for lang in langs:
			if entry[lang] != "":
				langentry = entry[lang].split('; ')
				itemdata['labels'].append({'lang':lang, 'value':langentry.pop(0)})
				for alias in langentry:
					itemdata['aliases'].append({'lang':lang, 'value':alias})
		for lang in langs:
			langdefentry = entry[lang+'def']
			if langdefentry != "":
				itemdata['descriptions'].append({'lang':lang, 'value':langdefentry})

		euswbi.itemwrite(itemdata)
