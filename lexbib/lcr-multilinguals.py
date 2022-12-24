import lwbi, langmapping, config_private
import csv

with open(config_private.datafolder+"lcr_multilingual.csv") as csvfile:
	lcrlist = csv.DictReader(csvfile)
	for entry in lcrlist:
		statements = []
		qualifiers = []
		seenlangs = []
		if "sourcelangs" in entry:
			sourcelangs = entry['sourcelangs'].split(",")
			for lang in sourcelangs:
				langqid = langmapping.getqidfromiso(langmapping.getiso3(lang))
				qualifiers.append({'prop_nr':'P150', 'type':'item', 'value':langqid})
				seenlangs.append(langqid)
		if "targetlangs" in entry:
			targetlangs = entry['targetlangs'].split(",")
			for lang in targetlangs:
				langqid = langmapping.getqidfromiso(langmapping.getiso3(lang))
				qualifiers.append({'prop_nr':'P134', 'type':'item', 'value':langqid})
				seenlangs.append(langqid)
		print('Languages: '+str(set(seenlangs)))
		if len(qualifiers) > 0:
			if len(set(seenlangs)) == 2: # bilingual dictionary
				statements.append({'prop_nr':'P115', 'type': 'item', 'value': 'Q14384', 'qualifiers': qualifiers})
			elif len(set(seenlangs)) > 2: # multilingual dictionary
				statements.append({'prop_nr':'P115', 'type': 'item', 'value': 'Q14422', 'qualifiers': qualifiers})
		if len(statements) > 0:
			lwbi.itemwrite({'qid': entry['lcrqid'], 'statements':statements, 'qualifiers':qualifiers})
			print('...wrote source / target language info to '+entry['lcrqid']+'\n')
		else:
			print('...found nothing to process for '+entry['lcrqid']+'\n')
print('Finished.')
