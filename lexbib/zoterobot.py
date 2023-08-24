import requests, time, re, json, config
from config_private import zotero_group_id, zotero_api_key

citations_cache = {}
with open('data/citations_cache.jsonl') as jsonlfile:
	jsonl = jsonlfile.read().split('\n')
	for line in jsonl:
		if line.startswith("{"):
			jsonline = json.loads(line)
			citations_cache[jsonline['zotitemid']] = jsonline['citation']

def getcitation(zotitemid):
	global citations_cache
	if zotitemid in citations_cache:
		print(f"Will take citation from cache: {zotitemid}")
		return citations_cache[zotitemid]
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
			# convert Lexbib link (from "archive location" - needs mla style)
			bib = re.sub(r'https?://lexbib.elex.is/entity/(Q[0-9]+)', r'([[Item:\1|\1]])', bib)
			# convert remaining links
			bib = re.sub(r'<a href="(https?://)([^/]+)([^"]+)">[^<]+</a>', r'[\1\2\3 \2]', bib)
			print(bib)
			citations_cache[zotitemid] = bib
			with open('data/citations_cache.jsonl', 'a', encoding='utf-8') as jsonlfile:
				jsonlfile.write(json.dumps({'zotitemid':zotitemid,'citation':bib})+'\n')
			return(bib)

		if "400" or "404" in str(r):
			print('*** Fatal error: Item ' + zotitemid + ' got ' + str(r) + ', does not exist on Zotero. Will skip.')
			time.sleep(5)
			break
		print('Zotero API GET request failed (' + zotitemid + '), will repeat. Response was ' + str(r))
		time.sleep(2)

# testitem = "HERCJU9P"
# print(getcitation(testitem))

