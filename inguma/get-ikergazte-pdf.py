import csv, requests, re, json

with open('data/ikergazte-doi-url.csv') as csvfile:
	ikergazte = csv.DictReader(csvfile, delimiter="\t")
	result = {}
	for entry in ikergazte:
		print(str(entry['URL']))
		html = requests.get(entry['URL']).text
		pdflinksearch = re.search('href="(https://www\.inguma\.eus/fso/fitxategia/[^"]+)"', html)
		if pdflinksearch:
			pdflink = pdflinksearch.group(1)
			print('Found ',pdflink)
			result[entry['DOI']] = {'URL':entry['URL'], 'PDF': pdflink}
		else:
			print('Failed to find anything.')

with open('data/ikergazte-doi-url-pdf.json', 'w') as jsonfile:
	json.dump(result, jsonfile, indent=2)
