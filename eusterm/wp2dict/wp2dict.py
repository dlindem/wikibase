#!/usr/bin/python3
import json, re, requests, time
from csv2sheet import csv2sheet

# inlink expl # https://de.wikipedia.org/wiki/Marxistische_Wirtschaftstheorie
# apilink expl # https://de.wikipedia.org/w/api.php?action=parse&prop=text&page=Marxistische_Wirtschaftstheorie&format=json

allowed_lang = ['eu', 'es', 'en', 'fr', 'it', 'de', 'pt', 'ca', 'cs']

header_entries = ['"wikidata"', '"wikidatalink"', '"source_page"', '"instance_of"', '"part_of"', '"subclass_of"']
for lang in allowed_lang:
	header_entries.append('"'+lang+'"')
	header_entries.append('"'+lang+'_wikipedia"')



with open('pagelinks.txt', 'r') as file:
	pagelinks = file.read().split('\n')
	print(str(pagelinks))

for pagelink in pagelinks:
	if not pagelink.startswith('https://'):
		continue
	wlang = re.search(r'https://([^\.]+)\.', pagelink).group(1)
	pagetitle = re.search(r'wikipedia.org/wiki/(.*)', pagelink).group(1)
	print('\nProcessing '+pagetitle+', language '+wlang+'...\n')
	gettexturl = 'https://'+wlang+'.wikipedia.org/w/api.php?action=parse&prop=text&page='+pagetitle+'&format=json'
	pagetext = requests.get(url=gettexturl).json()['parse']['text']['*']
	print(pagetext)
	pagejson = requests.get(url='https://www.wikidata.org/w/api.php?action=wbgetentities&sites='+wlang+'wiki&format=json&titles='+pagetitle).json()
	pageqid = list(pagejson['entities'].keys())[0]
	# print(str(pageqid))
	# time.sleep(10)
	links = [pagetitle]
	links += re.findall('href="/wiki/[^ ]+ title="([^"]+)"', pagetext.split('<ol class="references">')[0]) # wiki crossrefs in text body before the references section
	print(str(links))

	outfilename = 'output/'+pagetitle+'.'+wlang+'.csv'
	with open(outfilename, 'w', encoding="utf-8") as outfile:
		outfile.write("\t".join(header_entries)+'\n')

		seenqid = [pageqid] # first line of result table will be the page qid itself, then the qids for blue links
		for linkpagetitle in links:
			if re.search('[A-Z][a-z]+:', linkpagetitle): # "Spezial:", "Datei:", etc.
				continue
			if re.search('(disambiguation)', linkpagetitle): # exclude Disambiguation pages
				continue
			if re.search('[0-9]', linkpagetitle): # exclude page titles with numbers (pages describing days, years)
				continue

			apiurl = 'https://www.wikidata.org/w/api.php?action=wbgetentities&sites='+wlang+'wiki&format=json&titles='+linkpagetitle
			print(apiurl)
			wdjsonsource = requests.get(url=apiurl)
			wdjson =  wdjsonsource.json()
			# with open('entity.json', 'w') as jsonfile:
			#	 json.dump(wdjson, jsonfile, indent=2)
			takeresults = 1 # only take the first Qid listed in 'entities'
			countresults = 0
			result = {'labels':{}, 'sitelinks':{}, 'part_of': [], 'subclass_of':[], 'instance_of':[]}
			for wdid in wdjson['entities']:
				if countresults == takeresults:
					break
				countresults += 1
				if wdid in seenqid:
					continue

				if 'labels' in wdjson['entities'][wdid]:
					for labellang in wdjson['entities'][wdid]['labels']:
						result['labels'][labellang] = wdjson['entities'][wdid]['labels'][labellang]['value']

				if 'sitelinks' in wdjson['entities'][wdid]:
					for langsite in wdjson['entities'][wdid]['sitelinks']:
						result['sitelinks'][langsite.replace('wiki','')] = wdjson['entities'][wdid]['sitelinks'][langsite]['title'].replace(' ','_')

				if 'claims' in wdjson['entities'][wdid]:

					if 'P361' in wdjson['entities'][wdid]['claims']:
						for claim in wdjson['entities'][wdid]['claims']['P361']:
							if 'datavalue' in claim['mainsnak']:
								result['part_of'].append('https://wikidata.org/wiki/'+claim['mainsnak']['datavalue']['value']['id'])
					if 'P31' in wdjson['entities'][wdid]['claims']:
						for claim in wdjson['entities'][wdid]['claims']['P31']:
							if 'datavalue' in claim['mainsnak']:
								result['instance_of'].append('https://wikidata.org/wiki/'+claim['mainsnak']['datavalue']['value']['id'])
					if 'P279' in wdjson['entities'][wdid]['claims']:
						for claim in wdjson['entities'][wdid]['claims']['P279']:
							if 'datavalue' in claim['mainsnak']:
								result['subclass_of'].append('https://wikidata.org/wiki/'+claim['mainsnak']['datavalue']['value']['id'])

			#print(str(result))
			if not re.search(r'^Q[0-9]+', wdid): # exclude non-valid Qid
				continue

			csvline = '\t'.join([
						'"'+wdid+'"',
						'"https://wikidata.org/wiki/'+wdid+'"',
						'"'+linkpagetitle+'"',
						'"'+'\n'.join(result['instance_of'])+'"',
						'"'+'\n'.join(result['part_of'])+'"',
						'"'+'\n'.join(result['subclass_of'])+'"'
					])+'\t'
			for lang in allowed_lang:
				if lang in result['labels']:
					langval = '"'+result['labels'][lang].replace('"','')+'"\t'
				else:
					langval = '\t'
				if lang in result['sitelinks']:
					langval += '"https://'+lang+'.wikipedia.org/wiki/'+result['sitelinks'][lang]+'"\t'
				else:
					langval += '\t'
				csvline += langval
			outfile.write(csvline+"\n")
	# send to google sheets
	csv2sheet(title='wp2dict_'+wlang+'_'+pagetitle, csvpath=outfilename)

print('\nFinished.\n')
