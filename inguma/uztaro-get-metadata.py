import csv, requests, re, json, time, os, iwbi, urllib

akatsdunak = ["https://wikibase.inguma.eus/entity/Q34588", "https://wikibase.inguma.eus/entity/Q34560", "https://wikibase.inguma.eus/entity/Q25005", "https://wikibase.inguma.eus/entity/Q24999", "https://wikibase.inguma.eus/entity/Q34549", "https://wikibase.inguma.eus/entity/Q25188", "https://wikibase.inguma.eus/entity/Q24103", "https://wikibase.inguma.eus/entity/Q24384", "https://wikibase.inguma.eus/entity/Q34488", "https://wikibase.inguma.eus/entity/Q34483", "https://wikibase.inguma.eus/entity/Q34543", "https://wikibase.inguma.eus/entity/Q24101", "https://wikibase.inguma.eus/entity/Q24610", "https://wikibase.inguma.eus/entity/Q34577", "https://wikibase.inguma.eus/entity/Q24997", "https://wikibase.inguma.eus/entity/Q34578", "https://wikibase.inguma.eus/entity/Q24325", "https://wikibase.inguma.eus/entity/Q34561", "https://wikibase.inguma.eus/entity/Q36946", "https://wikibase.inguma.eus/entity/Q34568", "https://wikibase.inguma.eus/entity/Q16605", "https://wikibase.inguma.eus/entity/Q25003", "https://wikibase.inguma.eus/entity/Q34574", "https://wikibase.inguma.eus/entity/Q25328", "https://wikibase.inguma.eus/entity/Q34572", "https://wikibase.inguma.eus/entity/Q25330", "https://wikibase.inguma.eus/entity/Q34547", "https://wikibase.inguma.eus/entity/Q34587", "https://wikibase.inguma.eus/entity/Q34558", "https://wikibase.inguma.eus/entity/Q34585", "https://wikibase.inguma.eus/entity/Q34581", "https://wikibase.inguma.eus/entity/Q34565", "https://wikibase.inguma.eus/entity/Q16606", "https://wikibase.inguma.eus/entity/Q34556", "https://wikibase.inguma.eus/entity/Q24386", "https://wikibase.inguma.eus/entity/Q24318", "https://wikibase.inguma.eus/entity/Q24102", "https://wikibase.inguma.eus/entity/Q24099", "https://wikibase.inguma.eus/entity/Q25329", "https://wikibase.inguma.eus/entity/Q24321", "https://wikibase.inguma.eus/entity/Q34554", "https://wikibase.inguma.eus/entity/Q25186", "https://wikibase.inguma.eus/entity/Q24604", "https://wikibase.inguma.eus/entity/Q34555", "https://wikibase.inguma.eus/entity/Q24383", "https://wikibase.inguma.eus/entity/Q34550", "https://wikibase.inguma.eus/entity/Q34582", "https://wikibase.inguma.eus/entity/Q25002", "https://wikibase.inguma.eus/entity/Q34518", "https://wikibase.inguma.eus/entity/Q34489", "https://wikibase.inguma.eus/entity/Q34570", "https://wikibase.inguma.eus/entity/Q34552", "https://wikibase.inguma.eus/entity/Q24176", "https://wikibase.inguma.eus/entity/Q24607", "https://wikibase.inguma.eus/entity/Q34557", "https://wikibase.inguma.eus/entity/Q24048", "https://wikibase.inguma.eus/entity/Q34545", "https://wikibase.inguma.eus/entity/Q24100", "https://wikibase.inguma.eus/entity/Q34551", "https://wikibase.inguma.eus/entity/Q34485", "https://wikibase.inguma.eus/entity/Q24387", "https://wikibase.inguma.eus/entity/Q34541", "https://wikibase.inguma.eus/entity/Q24606", "https://wikibase.inguma.eus/entity/Q26498", "https://wikibase.inguma.eus/entity/Q34645", "https://wikibase.inguma.eus/entity/Q34459", "https://wikibase.inguma.eus/entity/Q26497", "https://wikibase.inguma.eus/entity/Q25535", "https://wikibase.inguma.eus/entity/Q34456"]

# with open('data/uztaro_metadata_akatsak_2.csv') as txtfile:
# 	existing = txtfile.read().split('\n')
#
# 	kasu_egin = []
# 	for exist in existing:
# 		kasu_egin.append(exist.split(",")[0])
# print(kasu_egin)

with open('data/inguma-uztaro-articles.csv') as csvfile:
	uztaro = csv.DictReader(csvfile, delimiter="\t")

	count = 0
	for entry in uztaro:
		# if entry['artikulua'] not in kasu_egin:
		# 	continue
		statements = []
		count += 1
		print(f"\n[{count}]")
		qid = entry['artikulua'].replace("https://wikibase.inguma.eus/entity/", "")
		# if qid in existing:
		# 	print("This has been processed before.")
		# 	continue
		inguma = entry['inguma']
		# landing_page = "https://www.inguma.eus/produkzioa/ikusi/"+inguma
		ojs_page = entry['ojs_landing']
		# search_url = f"https://aldizkariak.ueu.eus/index.php/uztaro/search/index?query={urllib.parse.quote(entry['title'])}&dateFromYear=&dateFromMonth=&dateFromDay=&dateToYear=&dateToMonth=&dateToDay=&authors="
		# print("Getting "+search_url)
		# search_page = requests.get(search_url)
		# pagetext = re.sub(r'[\n\r\t]','',search_page.text)
		# ojs_re = re.search(r'<a id=[^ ]+ href=\"(https://aldizkariak.ueu.eus/index.php/uztaro/article/view/\d+)\">([^<]+)</a>', pagetext)
		# # ojs_re = re.search(r'href=\"(https://aldizkariak.ueu.eus/index.php/uztaro/article/view/\d+)', pagetext)
		# if ojs_re:
		# 	ojs_link = ojs_re.group(1)
		#
		# 	ojs_title = ojs_re.group(2).strip()
		# 	print(f"Found page and title: {ojs_title}")


		# print(f"Try to get html landing page {ojs_page}")
		response = requests.get(ojs_page)
		# ojs_link_re = re.search(r'\"(https://aldizkariak.ueu.eus/index.php/uztaro/article/view/[^\"]+)\"', response.text)
		# if not ojs_link_re:
		# 	print(f"Failed to get pdf_link for {qid}...")
		# 	ojs_link = None
		# 	time.sleep(4)
		# else:
		# 	ojs_link = ojs_link_re.group(1)
			# statements.append({'prop_nr':'P24', 'type':'url', 'value':ojs_link, 'action': 'replace'})

			# if len(entry['doi']) == 0:
			# 	print(f"Try to get OJS page {ojs_link}")
			# response2 = requests.get(ojs_link)
				# doi_re = re.search(r'<meta name=\"citation_doi\" content=\"([^\"]+)\"/>', response2.text)
				# if doi_re:
				# 	doi = doi_re.group(1)
				# 	print('Found DOI: ' + doi)
				# 	statements.append({'prop_nr': 'P20', 'type': 'externalid', 'value': doi})
				# else:
				# 	print('Failed to fetch DOI.')
				# 	doi = Nonedoi_re = re.search(r'<meta name=\"citation_doi\" content=\"([^\"]+)\"/>', response2.text)
				# title_re = re.search(r'<meta name=\"citation_title\" content=\"([^\"]+)\"/>', response2.text)
				# if title_re:
				# 	ojs_title = title_re.group(1)
				# 	if ojs_title == entry['title'] or entry['title'] in ojs_title:
				# 		title_check = f"{ojs_link}\tTitle OK."
				# 	else:
				# 		title_check = f"{ojs_link}\tojs_title\t{ojs_title}\twikibase_title\t{entry['title']}"
				# 	print(title_check)
				# else:
				# 	print(f"{ojs_link}\tFailed to fetch title")
				# 	title_check = f"{ojs_link}\tERROR: no OJS page found"
				
		pdf_re = re.search(r'<meta name=\"citation_pdf_url\" content=\"([^\"]+)\"/>', response.text)
		if pdf_re:
			pdf = pdf_re.group(1)
			print('Found PDF: ' + pdf)
			statements.append({'prop_nr': 'P48', 'type': 'URL', 'value': pdf, 'action':'replace'})
		else:
			print('Failed to fetch PDF.')
			pdf = None
		with open('data/uztaro_metadata.done', 'a') as resultfile:
			resultfile.write(f"{entry['artikulua']}\thttps://www.inguma.eus/produkzioa/ikusi/{entry['inguma']}\t{pdf}\n")
			# resultfile.write(f"{entry['artikulua']}\thttps://www.inguma.eus/produkzioa/ikusi/{entry['inguma']}\t{pdf}\t{title_check}\n")
		if len(statements) > 0:
			iwbi.itemwrite({'qid': qid, 'statements': statements})



			print(f"Success for {entry['artikulua']}.")
		time.sleep(0.6)


