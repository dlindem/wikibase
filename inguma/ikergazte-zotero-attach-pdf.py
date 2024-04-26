import json, csv, requests, sys, re, time, os
import config_private, iwb
from pyzotero import zotero

pyzot = zotero.Zotero(config_private.zotero_group_nr, 'group', config_private.zotero_api_key)

with open('data/done_pdf_attachments.txt', 'r') as donefile:
	donelist = donefile.read().split('\n')
	doneitems = []
	for item in donelist:
		try:
			doneitems.append(item.split('\t')[0])
		except:
			pass
	print(f"List of done items: {doneitems}")

with open('data/ikergazte-zot-doi-wikibase-pdf-fix.csv') as csvfile:
	entries = csv.DictReader(csvfile)

	for entry in entries:
		print(f"\nNow processing: {entry}")
		qid = entry['wikibase_item']
		# if qid in doneitems:
		# 	print(f"{qid} is done in a previous run, skipped.")
		# 	continue
		zot_parent = entry['zot']
		zot_statement = entry['zot_st']
		pdf_link = entry['pdf']


		# filename = re.search('[^/]+\.pdf$', pdf_link).group(0)
		# print(f"Downloading {pdf_link}...")
		# try:
		# 	response = requests.get(pdf_link)
		# except:
		# 	continue
		pdf_file = f'data/pdf/{qid}_full_text.pdf'
		if not os.path.exists(pdf_file):
			continue
		# with open(pdf_file, 'wb') as f:
		# 	f.write(response.content)
		print(f"Creating Zotero attachment...")
		att_data = pyzot.attachment_simple([pdf_file], zot_parent)
		print(f"Attachment data: {att_data}")
		try:
			att_key = att_data['unchanged'][0]['key']
		except:
			att_key = att_data['success'][0]['key']
		print(f"Attachment key is {att_key}")

		iwb.setqualifier(qid, "P64", zot_statement, "P65", att_key, "externalid")

		# statements = [{'prop_nr':'P64', 'type':'externalid', 'action': 'replace', 'value': zotid}] #, 'qualifiers':[{'prop_nr':'P65', 'type':'externalid', 'value':attkey}]}]
		#
		# iwbi.itemwrite({'qid': qid, 'statements': statements})
		with open('data/done_pdf_attachments.txt', 'a') as outfile:
			outfile.write(f"{qid}\t{zot_parent}\t{att_key}\n")

		time.sleep(1)
