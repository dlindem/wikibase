import re, sys, csv, time
import mwclient, config_private

site = mwclient.Site("eusterm.wikibase.cloud")
def get_token():
	global site

	# lwb login via mwclient
	while True:
		try:
			login = site.login(username=config_private.wb_bot_user, password=config_private.wb_bot_pwd)
			break
		except Exception as ex:
			print('lwb login via mwclient raised error: '+str(ex))
			time.sleep(60)
	# get token
	csrfquery = site.api('query', meta='tokens')
	token = csrfquery['query']['tokens']['csrftoken']
	print("Got fresh CSRF token for eneoli wikibase.")
	return token
token = get_token()

with open('TBX/page_template.txt') as txtfile:
	template = txtfile.read()

with open('TBX/hiztegiak.csv') as csvfile:
	hiztegi_table = csv.reader(csvfile, delimiter="\t")
	hiztegiak = {}
	for row in hiztegi_table:
		hiztegiak[row[0]] = row[1]
hiztegiak = dict(sorted(hiztegiak.items()))
print(hiztegiak)

indextext = "= Euskalterm UZEI Hiztegiak Eusterm Wikibasen =\n"
indextext += "Hemendik sartu hiztegi jakin baten orrialdera:\n\n"
indextext += "*[[Euskalterm/Hiztegi_guztiak|Hiztegi guztiak]]\n"
for hiztegi_title in hiztegiak:
	hiztegi_id = hiztegiak[hiztegi_title]
	hiztegi_page = template

	indextext += f"*[[Euskalterm/{hiztegi_title}|{hiztegi_title}]]\n"
	hiztegi_page = hiztegi_page.replace(f"@hiztegi_title@", hiztegi_title)
	hiztegi_page = hiztegi_page.replace(f"@hiztegi_id@", hiztegi_id)
	if hiztegi_id == "Q20876":
		hiztegi_page = hiztegi_page.replace(f"@euswb:hiztegi_id@", "[eusdp:P5 euswb:Q20876]")
	else:
		hiztegi_page = hiztegi_page.replace(f"@euswb:hiztegi_id@", f"euswb:{hiztegi_id}")

	# print(template)

	pagecreation = site.post('edit', token=token, contentformat='text/x-wiki', contentmodel='wikitext',
								 bot=True, recreate=True, summary=f"recreate wiki page for {hiztegi_title} using euskalterm_page_upload.py",
								 title=f"Euskalterm/{hiztegi_title}", text=hiztegi_page)
	print(str(pagecreation))
	time.sleep(1.5)

indextext += """\n= Hiztegiak eta deskribatutako kontzeptuen eta terminoen kopuruak =
<sparql tryit="1">
#title:Euskalterm hiztegiak, kontzeptuen eta euskarazko terminoen kopuruak
PREFIX euswb: <https://eusterm.wikibase.cloud/entity/>
PREFIX eusdp: <https://eusterm.wikibase.cloud/prop/direct/>
PREFIX eusp: <https://eusterm.wikibase.cloud/prop/>
PREFIX eusps: <https://eusterm.wikibase.cloud/prop/statement/>
PREFIX euspq: <https://eusterm.wikibase.cloud/prop/qualifier/>
PREFIX euspr: <https://eusterm.wikibase.cloud/prop/reference/>

select ?euskalterm_hiztegia ?hiztegiaren_izena ?concepts ?terms (?terms/?concepts as ?term_concept_ratio) {
select ?euskalterm_hiztegia ?hiztegiaren_izena (count(distinct ?concept) as ?concepts) (count(?term) as ?terms)
where {
  ?euskalterm_hiztegia eusdp:P5 euswb:Q20876; rdfs:label ?hiztegiaren_izena.
  ?concept eusdp:P17 ?euskalterm_hiztegia; eusdp:P8 ?term. 
     
 } group by ?euskalterm_hiztegia ?hiztegiaren_izena ?concepts ?terms }
order by desc(?term_concept_ratio)
</sparql>

= Euskalterm: Kontzeptu bera izendatzen duten terminoen arteko Levenshtein distantziak =
Ikus [[Euskalterm/Levenshtein]] orrialdea.
= Euskalterm: Hiztegi batean baino gehiagotan agertzen diren unitate terminologikoak =
<sparql tryit="1">
PREFIX euswb: <https://eusterm.wikibase.cloud/entity/>
PREFIX eusdp: <https://eusterm.wikibase.cloud/prop/direct/>
PREFIX eusp: <https://eusterm.wikibase.cloud/prop/>
PREFIX eusps: <https://eusterm.wikibase.cloud/prop/statement/>
PREFIX euspq: <https://eusterm.wikibase.cloud/prop/qualifier/>
PREFIX euspr: <https://eusterm.wikibase.cloud/prop/reference/>

select ?term ?hiztegien_izenak ?hiztegiak { filter (?hiztegiak > 1) {
select ?term (group_concat(?hiztegi_izena;SEPARATOR=", ") as ?hiztegien_izenak) (count(distinct ?hiztegi) as ?hiztegiak)
where {
  ?hiztegi eusdp:P5 euswb:Q20876; rdfs:label ?hiztegi_izena.
  ?concept eusdp:P17 ?hiztegi; eusdp:P8 ?term. 
 
  } group by ?term ?hiztegien_izenak ?hiztegiak  }
  } order by desc(?hiztegiak)
</sparql>
"""

pagecreation = site.post('edit', token=token, contentformat='text/x-wiki', contentmodel='wikitext',
							 bot=True, recreate=True, summary="recreate wiki page using euskalterm_page_upload.py",
							 title="Euskalterm", text=indextext)
print(str(pagecreation))

