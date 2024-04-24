import json, csv, requests, sys, re, time
import config_private# iwb
from pyzotero import zotero
#
pyzot = zotero.Zotero(config_private.zotero_group_nr, 'group', config_private.zotero_api_key)

with open('data/done_pdf_attachments.txt', 'r') as donefile:
	donelist = donefile.read().split('\n')
	pdf_keys = {}
	for item in donelist:
		try:
			itemdata = item.split('\t')
			pdf_keys[itemdata[0]] = {'zot_parent':itemdata[1], 'pdf_key':itemdata[2]}
		except:
			pass
	print(f"pdf keys: {pdf_keys}")

	for entry in pdf_keys:
		print(f"\nNow processing: {entry}")
		qid = entry
		zot_parent = pdf_keys[entry]['zot_parent']
		pdf_key = pdf_keys[entry]['pdf_key']
		filepath = f'/home/david/Zotero/storage/{pdf_key}/.zotero-ft-cache'
		try:
			with open(filepath, 'r') as txtfile:
				pdftxt = txtfile.read()
				regex = re.search('Abstract[ \n]*([^\n]+)', pdftxt)
				if regex:
					abstract = regex.group(1)
					print(f"\n{abstract}\n")
				else:
					abstract = None
					print('No abstract found')
				regex = re.search('Keywords:[ \n]*([^\n]+)', pdftxt)
				if regex:
					keyw = regex.group(1)
					keyw = keyw.replace(" – ",";")
					keyw = keyw.replace(", ",";")
					keyw = keyw.replace("·",";")
					keyw = keyw.split(";")
					keywords = []
					for key in keyw:
						keywords.append(key.strip())
					print(f"{keywords}\n")
				else:
					keywords = None
					print('No keywords found')
		except Exception as ex:
			print(f'Could not find: {filepath}, {str(ex)}')
			continue

		if abstract:
			if keywords:
				abstract += f"\n\nKeywords: {', '.join(keywords)}"


			zotitem = pyzot.item(zot_parent)
			print(f"{zotitem}")
			zotitem['data']['abstractNote'] = abstract
			pyzot.update_item(zotitem)

		# filename = re.search('[^/]+\.pdf$', pdf_link).group(0)
		# print(f"Downloading {pdf_link}...")
		# try:
		# 	response = requests.get(pdf_link)
		# except:
		# 	continue
		# pdf_file = f'data/pdf/{qid}_full_text.pdf'
		# with open(pdf_file, 'wb') as f:
		# 	f.write(response.content)
		# print(f"Creating Zotero attachment...")
		# att_data = pyzot.attachment_simple([pdf_file], zot_parent)
		# print(f"Attachment data: {att_data}")
		# try:
		# 	att_key = att_data['unchanged'][0]['key']
		# except:
		# 	att_key = att_data['success'][0]['key']
		# print(f"Attachment key is {att_key}")
		#
		# iwb.setqualifier(qid, "P64", zot_statement, "P65", att_key, "externalid")
		#
		# # statements = [{'prop_nr':'P64', 'type':'externalid', 'action': 'replace', 'value': zotid}] #, 'qualifiers':[{'prop_nr':'P65', 'type':'externalid', 'value':attkey}]}]
		# #
		# # iwbi.itemwrite({'qid': qid, 'statements': statements})
		# with open('data/done_pdf_attachments.txt', 'a') as outfile:
		# 	outfile.write(f"{qid}\t{zot_parent}\t{att_key}\n")

		time.sleep(1)
