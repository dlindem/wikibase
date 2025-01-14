import json, re, time, os, sys
import xwbi

donefiles = os.listdir('data/wikibase-upload')

with open('data/parsed-wikt.json') as infile:
	wikt = json.load(infile)

for entry in wikt:
	filename = f"{entry['lemma']}.{entry['pos']}"
	print(f"\nWill now process: {filename}")
	cont = True
	for donefile in donefiles:
		if filename in donefile:
			print(f"Entry '{filename}' done before, skipped.")
			cont = False
	if not cont:
		continue

	# claim_references = xwbi.References()  # Create a group of references
	# claim_reference1 = xwbi.Reference()
	# claim_reference1.add(xwbi.Item(prop_nr='P6', value='Q16'))
	# claim_reference2 = xwbi.Reference()
	# claim_reference2.add(xwbi.URL(prop_nr='P8', value=entry['reference']))
	# claim_reference3 = xwbi.Reference()
	# claim_reference3.add(xwbi.Item(prop_nr='P11', value='Q17'))
	# claim_reference4 = xwbi.Reference()

	# Create a group of references
	main_references = xwbi.References()
	main_reference1 = xwbi.Reference()
	main_reference1.add(xwbi.URL(prop_nr='P8', value=entry['reference']))
	main_reference1.add(xwbi.Item(prop_nr='P11', value='Q17'))
	main_reference1.add(xwbi.Time(prop_nr='P9', time='now'))
	main_references.add(main_reference1)

	claim_references = xwbi.References()
	claim_reference1 = xwbi.Reference()
	claim_reference1.add(xwbi.Item(prop_nr='P6', value='Q16'))
	claim_reference1.add(xwbi.URL(prop_nr='P8', value=entry['reference']))
	claim_reference1.add(xwbi.Item(prop_nr='P11', value='Q17'))
	claim_reference1.add(xwbi.Time(prop_nr='P9', time='now'))
	claim_references.add(claim_reference1)


	lexeme = xwbi.wbi.lexeme.new(lexical_category=entry['pos'], language="Q4")

	lexeme.lemmas.set(language="mwl", value=entry['lemma'])

	ptwiktclaim = xwbi.Item(prop_nr='P6', value="Q16", references=main_references) # described in pt.wikt
	lexeme.claims.add(ptwiktclaim)

	if 'hyphen' in entry:
		claim = xwbi.String(prop_nr='P10', value=entry['hyphen'], references=claim_references)
		lexeme.claims.add(claim)

	if 'gender' in entry:
		claim = xwbi.Item(prop_nr='P12', value=entry['gender'], references=claim_references)
		lexeme.claims.add(claim)

	# senses
	if 'senses' in entry:
		for senseblock in entry['senses']:
			senseblock = senseblock.replace("# ", "")  # delete block begin
			senseblock = senseblock.replace("¶","") # delete EOL
			senseblock = senseblock.replace("'", "") # delete markup italics, bold
			senseblock = re.sub(r'\[\[[^\:\]]+\:[^\]]+\]\],? ?', '', senseblock) # delete Category: etc.
			senseblock = re.sub(r'\[\[#[^\]]+\]\],? ?', '', senseblock) # delete Category: etc.
			senseblock = re.sub(r'\{\{[^\}]+\}\} ?', '', senseblock) # delete wiki templates
			senseblock = senseblock.replace("[","") # delete xrefs
			senseblock = senseblock.replace("]","") # delete xrefs
			if senseblock.strip() == '':
				senseblock = "XXX"
			print(f"Sense: {senseblock}")
			sense = xwbi.Sense()
			sense.glosses.set(language='pt', value=senseblock.strip())
			sense.claims.add(ptwiktclaim)
			lexeme.senses.add(sense)

	# forms
	for formblock in entry['forms']:
		form = xwbi.Form()
		form.representations.set(language='mwl', value=formblock['form'])
		form.grammatical_features = formblock['gram']
		form.claims.add(ptwiktclaim)
		lexeme.forms.add(form)



	done = False
	while not done:
		try:
			lexeme.write()
			done = True
		except Exception as ex:
			if "404 Client Error" in str(ex):
				print('Got 404 response from wikibase, will wait and try again...')
				time.sleep(10)
			else:
				print('Unexpected error:\n'+str(ex))
				sys.exit()

		with open(f'data/wikibase-upload/{filename}.{lexeme.id}.json', 'w') as outfile:
			json.dump({"URI": f"https://lhenguabase.wikibase.cloud/entity/{lexeme.id}", "entry": entry}, outfile, indent=2)
		print('Finished processing '+lexeme.id, filename)
		time.sleep(0.5)