import csv, requests, re, json, time, os

# with open('data/nullbyte_qid.txt') as txtfile:
# 	missing = txtfile.read().split('\n')
# 	print(missing)

path = 'data/pdf'
existing = []
for filename in os.listdir(path):
	qid_re = re.search(r'Q[0-9]+', filename)
	if qid_re:
		existing.append(qid_re.group(0))

print(f"PDFs already in the folder: {len(existing)}")
print(existing)

with open('data/asju_item_pdfloc.csv') as csvfile:
	asju = csv.DictReader(csvfile, delimiter=",")

	for entry in asju:
		qid = entry['item'].replace("https://wikibase.inguma.eus/entity/", "")
		if qid in existing:
			print("This has been processed before.")
			continue
		pdf_loc = entry['pdf_loc']
		if 'download' in pdf_loc: # this is a direct download not html landing page link
			pdf_link = pdf_loc
			print(f"Will get PDF for {qid} directly {pdf_loc}")
		else:
			print(f"Try to get PDF for {qid} via html landing page {pdf_loc}")
			response = requests.get(pdf_loc)
			pdf_link_re = re.search(r'\"(https://ojs.ehu.eus/index.php/ASJU/article/download/[^\"]+)\"', response.text)
			if not pdf_link_re:
				print(f"Failed for {qid}...")
				time.sleep(4)
				continue
			pdf_link = pdf_link_re.group(1)
		response = requests.get(pdf_link)
		pdf_file = f'data/pdf/{qid}_full_text.pdf'
		with open(pdf_file, 'wb') as f:
			f.write(response.content)
		print(f'Success for {pdf_file}: {os.path.getsize(pdf_file)} bytes')

		time.sleep(2)


