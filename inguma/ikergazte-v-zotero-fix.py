import json, csv, requests, sys, re, time
import config_private, iwb
from pyzotero import zotero

pyzot = zotero.Zotero(config_private.zotero_group_nr, 'group', config_private.zotero_api_key)

def patch_item(qid=None, zotitem=None, children=[]):
	# communicate with Zotero, write Wikibase entity URI to "extra" and attach URI as link attachment
	needs_update = False
	if True:
		attachment_present = False
		for child in children:
			if 'url' not in child['data']:
				continue
			if child['data']['url'].startswith('https://wikibase.inguma.eus/entity/'):
				if child['data']['url'].endswith(qid):
					print('Correct link attachment already present.')
					attachment_present = True
				else:
					print('Fatal error: Zotero item was linked before to this other Q-id:\n'+child['data']['url'])
					input('Press enter to continue or CTRL+C to abort.')
		if not attachment_present:
			attachment = [
				{
					"itemType": "attachment",
					"parentItem": zotitem['data']['key'],
					"linkMode": "linked_url",
					"title": "Inguma Wikibase",
					"accessDate": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
					"url": 'https://wikibase.inguma.eus/entity/' + qid,
					"note": '<p>See this item as linked data at <a href="' + "https://wikibase.inguma.eus" + '/wiki/Item:' + qid + '">' + 'https://wikibase.inguma.eus/entity/' + qid + '</a>',
					"tags": [],
					"collections": [],
					"relations": {},
					"contentType": "",
					"charset": ""
				}
			]
			r = requests.post('https://api.zotero.org/groups/' + config_private.zotero_group_nr + '/items',
							  headers={"Zotero-API-key": config_private.zotero_api_key,
									   "Content-Type": "application/json"}, json=attachment)
			if "200" in str(r):
				print(f"Link attachment successfully attached to Zotero item {zotitem['data']['key']}.")
				needs_update = True

	if True:
		if 'https://wikibase.inguma.eus/entity/'+qid in zotitem['data']['extra']:
			print('This item already has its Wikibase item URI stored in EXTRA.')
		else:
			zotitem['data']['extra'] = 'https://wikibase.inguma.eus/entity/' + qid + "\n" + zotitem['data']['extra']
			print('Successfully written Wikibase item URI to EXTRA.')
			needs_update = True

	if needs_update:
		return (zotero_update_item(zotitem))
	else:
		return f"Item {zotitem} successfully updated."

def zotero_update_item(zotitem):
	# del zotitem['wikibase_entity']  # raises zotero api error if left in item
	try:
		pyzot.update_item(zotitem, last_modified=None)
		return f"Successfully updated Zotero item <code><a href=\"{zotitem['links']['alternate']['href']}\" target=\"_blank\">{zotitem['key']}</a></code>: Reload records to be exported from Zotero."
	except Exception as err:
		if "Item has been modified since specified version" in str(err):
			return f"Versioning Error (has been modified since) *** <code><a href=\"{zotitem['links']['alternate']['href']}\" target=\"_blank\">{zotitem['key']}</a></code>: Reload records to be exported from Zotero."
		else:
			return f"Unknown error updating *** <code><a href=\"{zotitem['links']['alternate']['href']}\" target=\"_blank\">{zotitem['key']}</a></code>: Reload records to be exported from Zotero."

with open('data/done_pdf_attachments.txt', 'r') as donefile:
	donelist = donefile.read().split('\n')
	doneitems = {}
	for item in donelist:
		try:
			doneitems[(item.split('\t')[0])] = {'zot': item.split('\t')[1], 'att': item.split('\t')[2]}
		except:
			pass
	print(f"List of done items: {doneitems}")

with open('data/ikergazte-v-doi-pdf.csv') as csvfile:
	wikibase_csv = csv.DictReader(csvfile)

	count = 0
	for entry in wikibase_csv:
		# doi_wb[entry['doi_link']] = {'wikibase_item':entry['wikibase_item'], 'inguma_link':entry['inguma_link']}
		qid = re.search('^Q\d+', entry['zot_st']).group(0)




		count += 1
		print(f"[{count}] {qid}")
		if qid in doneitems:
			if entry['pdf'] != doneitems[qid]['att']:
				print(f"Found bad attachment {entry['pdf']}")
				iwb.removeclaim(entry['zot_st'])
			else:
				print(f"Found good attachment {entry['pdf']}")


	# for entry in pyzot.items(tag='ikergazte-fix'):
	# 	print(f"\nNow processing: {entry}")
	# 	zot_parent = entry['key']
	# 	doi = entry['data']['DOI']
	# 	qid = doi_wb[doi]['wikibase_item']
	# 	print(qid)
	#
	# 	children = pyzot.children(zot_parent)
	# 	for child in children:
	# 		if qid in child['data']['title']:
	# 			att_key = child['key']
	# 			print(f"Found correct child {child['key']}")




		# entry['data']['publisher'] = "Udako Euskal Unibertsitatea"
		# entry['data']['conferenceName'] = "V. Ikergazte. Nazioarteko ikerketa euskaraz"
		# inguma_link = 'https://www.inguma.eus/produkzioa/ikusi/'+doi_wb[doi]['inguma_link']
		# inguma_text = requests.get(inguma_link).text
		# pdf_link_re = re.search('https://www.inguma.eus/fso/fitxategia/(.*\.pdf)', inguma_text)
		# pdf_link = pdf_link_re.group(0)
		# pagessearch = re.search('(\d+)[_\-](\d+)', pdf_link)
		# if pagessearch:
		# 	entry['data']['pages'] = f"{pagessearch.group(1)}-{pagessearch.group(2)}"

		# if qid in doneitems:
		# 	print(f"{qid} is done in a previous run, skipped.")
		# 	continue

		# inguma_link = 'https://www.inguma.eus/produkzioa/ikusi/'+doi_wb[doi]['inguma_link']
		# inguma_text = requests.get(inguma_link).text
		# pdf_link_re = re.search('https://www.inguma.eus/fso/fitxategia/(.*\.pdf)', inguma_text)
		# pdf_link = pdf_link_re.group(0)
		# filename = pdf_link_re.group(1)
		# print(filename)
		# iwb.stringclaim(qid, "P48", pdf_link)
		# continue


		# print(f"Downloading {pdf_link}...")
		# response = requests.get(pdf_link)
		# pdf_file = f'data/pdf/{qid}_full_text.pdf'
		# with open(pdf_file, 'wb') as f:
		# 	f.write(response.content)
		#
		#
		#
		#
		# print(f"Creating Zotero attachment...")
		# att_data = pyzot.attachment_simple([pdf_file], zot_parent)
		# print(f"Attachment data: {att_data}")
		# try:
		# 	att_key = att_data['unchanged'][0]['key']
		# except:
		# 	att_key = att_data['success'][0]['key']
		# print(f"Attachment key is {att_key}")

		# zot_statement = iwb.stringclaim(qid, "P64", zot_parent)
		# iwb.setqualifier(qid, "P64", zot_statement, "P65", att_key, "externalid")
		#
		# patch_item(qid=qid, zotitem=entry)

		# statements = [{'prop_nr':'P64', 'type':'externalid', 'action': 'replace', 'value': zotid}] #, 'qualifiers':[{'prop_nr':'P65', 'type':'externalid', 'value':attkey}]}]
		#
		# iwbi.itemwrite({'qid': qid, 'statements': statements})
		# with open('data/done_pdf_attachments.txt', 'a') as outfile:
		# 	outfile.write(f"{qid}\t{zot_parent}\t{att_key}\n")
		#
		# time.sleep(1)
