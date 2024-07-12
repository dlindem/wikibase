import csv, requests, re, json, time, os

existing = []
with open('data/asju_metadata.qs') as txtfile:
	qslist = txtfile.read().split('\n')
	for row in qslist:
		qid_re = re.search(r'Q[0-9]+', row)
		if qid_re:
			qid = qid_re.group(0)
			if qid not in existing:
				existing.append(qid)

print(f"QIDs already on the QuickStatements list: {len(existing)}")
print(existing)


with open('data/asju_item_pdfloc.csv') as csvfile:
	asju = csv.DictReader(csvfile, delimiter=",")

	count = 0
	for entry in asju:
		count += 1
		print(f"\n[{count}]")
		qid = entry['item'].replace("https://wikibase.inguma.eus/entity/", "")
		if qid in existing:
			print("This has been processed before.")
			continue
		pdf_loc = entry['pdf_loc']
		if 'download' in pdf_loc: # this is a direct download not html landing page link
			pdf_link = pdf_loc
			print(f"Have found for {qid} direct PDF link {pdf_loc}")
		else:
			landing_page_re = re.search(r'https?://[^A]+ASJU/article/view/[0-9]+', pdf_loc)
			if not landing_page_re:
				print(f"Failed to get landing page link for {qid}")
				time.sleep(4)
				continue
			landing_page = landing_page_re.group(0)
			print(f"Try to get html landing page {landing_page}")
			response = requests.get(landing_page)
			pdf_link_re = re.search(r'\"(https://ojs.ehu.eus/index.php/ASJU/article/download/[^\"]+)\"', response.text)
			if not pdf_link_re:
				print(f"Failed to get pdf_link for {qid}...")
				pdf_link = None
				time.sleep(4)
			else:
				pdf_link = pdf_link_re.group(1)
			doi_re = re.search(r'<meta name=\"citation_doi\" content=\"([^\"]+)\"/>', response.text)
			if doi_re:
				doi = doi_re.group(1)
				print('Found DOI: ' + doi)
			else:
				print('Failed to fetch DOI.')
				doi = None
		print(f"{qid}\tP48\t{pdf_link} | {qid}\tP20\t{doi}\n")
		result = ""
		if pdf_link:
			result+= f'{qid}\tP48\t"{pdf_link}"\n'
		if doi:
			result+= f'{qid}\tP20\t"{doi}"\n'

		with open('data/asju_metadata.qs', 'a') as resultfile: # for quickstatements
			resultfile.write(result)
		print(f"Success for {qid}.")
		time.sleep(1)


