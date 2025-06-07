import re, sys, csv, time
import mwclient, config_private

site = mwclient.Site("eneoli.wikibase.cloud")
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

with open('data/language-page-template.txt') as txtfile:
	template = txtfile.read()

with open('data/languages_table.csv') as csvfile:
	language_table = csv.DictReader(csvfile, delimiter=",")
	#language_name,iso-639-1,iso-639-3,wiki_languagecode,wikibase_item,wikidata_item
	indextext = "Access from here the page for your working language:\n\n"
	for row in language_table:
		# if row['wiki_languagecode'] != "is":
		# 	continue
		langpage = template
		rowdata = {'langname' : row['language_name'], 'langwikicode': row['wiki_languagecode'], 'wikibase_item': row['wikibase_item']}
		print(rowdata)

		indextext += f"*[[NeoVoc/language/{row['wiki_languagecode']}|{row['language_name']}]]\n"

		for key in rowdata:
			langpage = langpage.replace(f"@{key}", rowdata[key])
		# print(template)

		pagecreation = site.post('edit', token=token, contentformat='text/x-wiki', contentmodel='wikitext',
									 bot=True, recreate=True, summary=f"recreate wiki page for {row['language_name']} using upload_lang_page.py",
									 title=f"NeoVoc/language/{row['wiki_languagecode']}", text=langpage)
		print(str(pagecreation))
		time.sleep(0.5)

	pagecreation = site.post('edit', token=token, contentformat='text/x-wiki', contentmodel='wikitext',
								 bot=True, recreate=True, summary="recreate wiki page using upload_lang_page.py",
								 title="NeoVoc/language", text=indextext)
	print(str(pagecreation))

