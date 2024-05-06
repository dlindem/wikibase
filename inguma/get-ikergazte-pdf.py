import csv, requests, re, json, time, os

# with open('data/nullbyte_qid.txt') as txtfile:
# 	missing = txtfile.read().split('\n')
# 	print(missing)

path = 'data/pdf'
missing = []
for filename in os.listdir(path):
	if os.path.getsize(path+'/'+filename) == 0:
		qid = re.search('^Q\d+', filename).group(0)
		missing.append(qid)
print(f"PDFs with null size: {len(missing)}")
print(missing)

with open('data/ikergazte-zot-doi-wikibase-pdf-fix.csv') as csvfile:
	ikergazte = csv.DictReader(csvfile, delimiter=",")

	for entry in ikergazte:
		qid = entry['wikibase_item']
		if qid in missing:
			pdf_link = entry['pdf']
			print(f"Try to get PDF for {qid} at {pdf_link}")
			response = requests.get(pdf_link)
			pdf_file = f'data/pdf/{qid}_full_text.pdf'
			with open(pdf_file, 'wb') as f:
				f.write(response.content)
			print(f'Success for {pdf_file}: {os.path.getsize(pdf_file)} bytes')

			time.sleep(2)


