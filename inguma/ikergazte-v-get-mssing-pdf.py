import csv, requests, re, json, time

with open('data/nullbyte_qid.txt') as txtfile:
	missing = txtfile.read().split('\n')
	print(missing)

with open('data/ikergazte-zot-doi-wikibase-pdf-fix.csv') as csvfile:
	ikergazte = csv.DictReader(csvfile, delimiter=",")

	for entry in ikergazte:
		qid = entry['wikibase_item']
		if qid in missing:
			done = False
			while not done:
				pdf_link = entry['pdf']
				print(f"Downloading {pdf_link}...")
				response = requests.get(pdf_link)
				time.sleep(1)
				if len(response.content) > 0:
					pdf_file = f'data/pdf/{qid}_full_text.pdf'
					with open(pdf_file, 'wb') as f:
						f.write(response.content)
						print(f"Saved PDF with length {len(response.content)}")
						done = True
				else:
					print("Gpot 0 bytes...")




