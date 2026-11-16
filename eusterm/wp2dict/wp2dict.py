#!/usr/bin/python3
import re, requests, os, time
from google import csv2sheet

# inlink expl # https://de.wikipedia.org/wiki/Marxistische_Wirtschaftstheorie
# apilink expl # https://de.wikipedia.org/w/api.php?action=parse&prop=text&page=Marxistische_Wirtschaftstheorie&format=json

allowed_lang = ['eu', 'es', 'en', 'fr', 'it', 'de', 'ca']

header_entries = ['"wikidata"', '"wikidatalink"', '"source_page"', '"instance_of"', '"part_of"', '"subclass_of"']
for lang in allowed_lang:
	header_entries.append('"'+lang+'"')
	header_entries.append('"'+lang+'_wikipedia"')



with open('pagelinks.py', 'r') as file:
	pagelinks = file.read().split('\n')
	print(str(pagelinks))

for pagelink in pagelinks:
	if not pagelink.startswith('https://'):
		continue
	wlang = re.search(r'https://([^\.]+)\.', pagelink).group(1)
	pagetitle = re.search(r'wikipedia.org/wiki/(.*)', pagelink).group(1)
	print('\nProcessing '+pagetitle+', language '+wlang+'...\n')
	outfilename = 'output/' + pagetitle + '.' + wlang + '.csv'
	if os.path.isfile(outfilename):
		print('This Wikipedia page has been processed before.')
		continue

	headers = {
		'User-Agent': 'Wikidata user DL2204 python script david.lindemann@ehu.eus'
	}
	gettexturl = 'https://'+wlang+'.wikipedia.org/w/api.php?action=parse&prop=text&page='+pagetitle+'&format=json'
	print(gettexturl)
	r = requests.get(url=gettexturl, headers=headers)
	print(r)
	pagetext = r.json()['parse']['text']['*']
	print(pagetext)
	pagejson = requests.get(url='https://www.wikidata.org/w/api.php?action=wbgetentities&sites='+wlang+'wiki&format=json&titles='+pagetitle, headers=headers).json()
	pageqid = list(pagejson['entities'].keys())[0]
	# print(str(pageqid))
	# time.sleep(10)
	links = [pagetitle]
	# links += re.findall('href="https://[^/]+/wiki/[^ ]+ title="([^"]+)"', pagetext.split('<ol class="references">')[0]) # wiki crossrefs in text body before the references section
	links += re.findall('href="/wiki/[^ ]+ title="([^"]+)"', pagetext.split('<ol class="references">')[0]) # wiki crossrefs in text body before the references section
	print(str(links))
	print(f"\n Found {len(links)} wikipedia pages in {pagetitle}.")
	seen_pagelinks = []
	with open(outfilename, 'w', encoding="utf-8") as outfile:
		outfile.write("\t".join(header_entries)+'\n')

		seenqid = [pageqid] # first line of result table will be the page qid itself, then the qids for blue links
		countresults = 0
		for linkpagetitle in links:
			if linkpagetitle in seen_pagelinks:
				print(f"Seen link: {linkpagetitle}")
				continue
			seen_pagelinks.append(linkpagetitle)
			if re.search('[A-Z][a-z]+:', linkpagetitle): # "Spezial:", "Datei:", etc.
				continue
			if re.search('(disambiguation)', linkpagetitle): # exclude Disambiguation pages
				continue
			if re.search('[0-9]', linkpagetitle): # exclude page titles with numbers (pages describing days, years)
				continue

			apiurl = 'https://www.wikidata.org/w/api.php?action=wbgetentities&sites='+wlang+'wiki&format=json&titles='+linkpagetitle.replace(" ","_")
			print(apiurl)
			while True:
				try:
					wdjsonsource = requests.get(url=apiurl, headers=headers)
					wdjson =  wdjsonsource.json()
					print("Api call successful.")
					time.sleep(1.6)
					break
				except:
					print(f"API call failed... will repeat...", end=" ")
					time.sleep(2)
				# with open('entity.json', 'w') as jsonfile:
				#	 json.dump(wdjson, jsonfile, indent=2)


			result = {'labels':{}, 'sitelinks':{}, 'part_of': [], 'subclass_of':[], 'instance_of':[]}

			for wdid in wdjson['entities']:
				print(f"{wdid}...", end=" ")
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
	input('Press ENTER for sending this to google sheets.')
	print("Wait...")
	csv2sheet.csv2sheet(title='Erauzketa_'+wlang+'_'+pagetitle, csvpath=outfilename)

print('\nFinished.\n')




