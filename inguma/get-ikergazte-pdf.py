import csv, requests, re, json

with open('data/nullbyte_qid.txt') as txtfile:
	missing = txtfile.read().split('\n')
	print(missing)

with open('data/ikergazte-zot-doi-wikibase-pdf-fix.csv') as csvfile:
	ikergazte = csv.DictReader(csvfile, delimiter=",")

	for entry in ikergazte:
		qid = entry['wikibase_item']
		if qid in missing:
			html = requests.get(entry['pdf']).text
			pdflinksearch = re.search('href="(https://www\.inguma\.eus/fso/fitxategia/[^"]+)"', html)
			if pdflinksearch:
				pdflink = pdflinksearch.group(1)
				print('Found ',pdflink)
				result[entry['DOI']] = {'URL':entry['URL'], 'PDF': pdflink}
			else:
				print('Failed to find anything.')


