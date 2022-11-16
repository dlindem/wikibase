import euswbi
import json, re, time, sys
eginda = """

"""
eginlist = eginda.split('\n')

arloa = "mendizaletasuna"
schemeqid = "Q197"
refqid = "Q195" # UZEI dict.

# load items to import
with open('pdf2dict/'+arloa+'.json', 'r') as jsonfile:
	source = json.load(jsonfile)
	for entry in source:
		itemdata = {'qid':False, 'statements':[], 'labels':[], 'aliases':[]}
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
			itemdata['statements'].append({'type':'string', 'prop_nr':'P13', 'value':entry['eusdef']})
		langs = ['es', 'fr', 'en']
		for lang in langs:
			langentry = entry[lang].split('; ')
			itemdata['labels'].append({'lang':lang, 'value':langentry.pop(0)})
			for alias in langentry:
				itemdata['aliases'].append({'lang':lang, 'value':alias})
		euswbi.itemwrite(itemdata)
