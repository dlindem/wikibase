import csv, requests, re, json, time, os, iwbi


with open('data/uztaro_metadata.done') as txtfile:
	existing = txtfile.read().split('\n')
print(existing)


with open('data/inguma-uztaro-articles.csv') as csvfile:
	uztaro = csv.DictReader(csvfile, delimiter="\t")

	count = 0
	for entry in uztaro:
		statements = []
		count += 1
		print(f"\n[{count}]")
		qid = entry['artikulua'].replace("https://wikibase.inguma.eus/entity/", "")
		if qid in existing:
			print("This has been processed before.")
			continue
		inguma = entry['inguma']
		landing_page = "https://www.inguma.eus/produkzioa/ikusi/"+inguma
		print(f"Try to get html landing page {landing_page}")
		response = requests.get(landing_page)
		ojs_link_re = re.search(r'\"(https://aldizkariak.ueu.eus/index.php/uztaro/article/view/[^\"]+)\"', response.text)
		if not ojs_link_re:
			print(f"Failed to get pdf_link for {qid}...")
			ojs_link = None
			time.sleep(4)
		else:
			ojs_link = ojs_link_re.group(1)
			statements.append({'prop_nr':'P24', 'type':'url', 'value':ojs_link, 'action': 'keep'})

			if len(entry['doi']) == 0:
				print(f"Try to get OJS page {ojs_link}")
				response2 = requests.get(ojs_link)

				doi_re = re.search(r'<meta name=\"citation_doi\" content=\"([^\"]+)\"/>', response2.text)
				if doi_re:
					doi = doi_re.group(1)
					print('Found DOI: ' + doi)
					statements.append({'prop_nr': 'P20', 'type': 'externalid', 'value': doi})
				else:
					print('Failed to fetch DOI.')
					doi = None
		if len(statements) > 0:
			iwbi.itemwrite({'qid': qid, 'statements': statements})


			with open('data/uztaro_metadata.done', 'a') as resultfile: # for quickstatements
				resultfile.write(qid+'\n')
			print(f"Success for {entry['artikulua']}.")
		time.sleep(1)


