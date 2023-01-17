import json, csv, requests, sys, re
import config_private, iwbi

with open('data/ikergazte-doi-url-pdf.json') as jsonfile:
	doi_pdf = json.load(jsonfile)

with open('data/ikergazte-zot-doi-wikibase.csv') as csvfile:
	entries = csv.DictReader(csvfile)
	for entry in entries:
		qid = entry['wikibase']
		zotid = entry['zotero']
		doi = entry['doi']
		if doi not in doi_pdf:
			print('** This doi is not found in URL mapping:',doi)
			continue
		pdflink = doi_pdf[doi]['PDF']
		filename = re.search('[^/]+\.pdf$', pdflink).group(0)

		attachment = [
		{
		"itemType": "attachment",
		"parentItem": zotid,
		"linkMode": "linked_file",
		"title": "Inguma Full Text",
		"accessDate": "2023-01-17T00:00:00Z",
		"url": pdflink,
		"note": "",
		"tags": [],
		"filename": filename,
		"relations": {},
		"contentType": "application/pdf",
		"charset": "",
		"md5": None,
		"mtime": None,
		}
		]

		print(str(attachment))

		r = requests.post('https://api.zotero.org/groups/'+config_private.zotero_group_nr+'/items', headers={"Zotero-API-key":config_private.zotero_api_key, "Content-Type":"application/json"} , json=attachment)

		if "200" in str(r):
			# print(r.json())
			try:
				attkey = r.json()['successful']['0']['key']
				linked_done[bibItemQid] = {"itemkey":zotid,"attkey":attkey}
				with open('data/pdfattachmentmappings.jsonl', 'a', encoding="utf-8") as jsonl_file:
					jsonline = {"bibitem":bibItemQid,"itemkey":zotid,"attkey":attkey}
					jsonl_file.write(json.dumps(jsonline)+'\n')
				print('Zotero item pdf attachment successfully written and bibitem-attkey mapping stored; attachment key is '+attkey+'.')
			except:
				print('Failed writing pdf attachment to Zotero item '+zotid+' (did not return created attachment - is the zotero item really in the right collection?).')
		else:
			print('Failed writing pdf attachment to Zotero item '+zotid+' (did not respond 200).')

		statements = [{'prop_nr':'P64', 'type':'externalid', 'action': 'replace', 'value': zotid, 'qualifiers':[{'prop_nr':'P65', 'type':'externalid', 'value':attkey}]}]

		iwbi.itemwrite({'qid': qid, 'statements': statements})

		sys.exit()
