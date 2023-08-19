import requests, time, re, config
from config_private import zotero_group_id, zotero_api_key

def getcitation(zotitemid):
	print(f'Will now get citation for Zotero ID {zotitemid}')
	zotapid = 'https://api.zotero.org/groups/'+zotero_group_id+'/items/'+zotitemid
	attempts = 0
	while attempts < 5:
		attempts += 1
		params = {'format': 'json', 'include': 'bib', 'linkwrap': 1, 'locale': 'eu_ES', 'style':'modern-language-association'}
		r = requests.get(zotapid, params=params)
		if "200" in str(r):
			zotitem = r.json()
			# print(zotitemid + ': got zotitem data')
			# print(zotitem['bib'])
			bib = re.search('<div class="csl-entry">(.*)</div>', zotitem['bib']).group(1)
			# de-html links
			bib = re.sub('<a href=[^>]+>', '', bib)
			bib = re.sub('</a>', '', bib)
			# convert Lexbib link (from "archive location" - needs mla style)
			bib = re.sub(r'https?://lexbib.elex.is/entity/(Q[0-9]+)', r'([[Item:\1|\1]])', bib)
			return(bib)

		if "400" or "404" in str(r):
			print('*** Fatal error: Item ' + zotitemid + ' got ' + str(r) + ', does not exist on Zotero. Will skip.')
			time.sleep(5)
			break
		print('Zotero API GET request failed (' + zotitemid + '), will repeat. Response was ' + str(r))
		time.sleep(2)

# testitem = "HERCJU9P"
# print(getcitation(testitem))

