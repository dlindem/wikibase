import iwbi
import inguma
import json, re, traceback, csv

print('___________________________\n')
existing = {}
with open('D:/Inguma/authors_without_duplicates.csv', 'r', encoding="utf-8") as csvfile:
	items = csv.DictReader(csvfile)
	for item in items:
		existing[item['iid']] = {'qid':item['wikibase_item'],'inguma':item['inguma']}


with open('D:/Inguma/persons.json', 'r') as jsonfile:
	persons = json.load(jsonfile)
with open('D:/Inguma/person_ids_upload_done.txt', encoding="utf-8") as txtfile:
	donelistraw = txtfile.read().split('\n')
	donelist = {}
	for done in donelistraw:
		try:
			doneitemid = done.split('\t')[0]
			ingumaurl = done.split('\t')[1]
			# doneitemid = int(re.search(r'^(\d+)',done).group(1))
			if doneitemid not in donelist:
				donelist[doneitemid] = ingumaurl
			# else:
			# 	with open('D:/Inguma/person_ids_upload_duplicates.txt', 'a', encoding="utf-8") as txtfile:
			# 		txtfile.write(str(doneitemid)+'\n')
		except:
			pass
	print('Items already uploaded: '+str(len(donelist)))
seen_cleanNames = []
index = 0
for person in persons:
	index +=1
	print('['+str(index)+'] Now processing Person with id '+str(person['id'])+'... '+str(len(persons)-index)+' items left.')
	if person['cleanName'] in seen_cleanNames:
		print('This cleanName has already been seen in this dataset: '+person['cleanName'])
		for x in donelist.values():
			if x == person['cleanName']:
				print('** Found duplicate in Inguma SQL: '+person['cleanName'])
				for y in existing.values():
					if y['inguma'] == person['cleanName']:
						item = iwbi.wbi.item.get(y['qid'])
						print('Will write this id to: '+item.labels.get('eu').value)
						newidstatement = iwbi.String(value=str(person['id']), prop_nr="P49")
						item.claims.add([newidstatement])
						item.write()
						print('Have added new id to existing item '+y['qid'])
		continue
	seen_cleanNames.append(person['cleanName'])
	# if str(person['id']) in donelist:
	# 	print('Person id '+str(person['id'])+' corresponds to existing '+donelist[person['id']]+', skipped.\n')
	# 	continue
	if str(person['id']) in existing:
		existing_qid = existing[str(person['id'])]['qid']
		print('This item is on IWB, qid is '+existing_qid)
		continue

	else:
		query = 'select ?wikibase_item where {?wikibase_item idp:P49 "'+str(person['id'])+'".}'
		bindings = iwbi.wbi_helpers.execute_sparql_query(query=query, prefix=iwbi.sparql_prefixes)['results']['bindings']
		if len(bindings) > 0:
			iwbqid = bindings[0]['wikibase_item']['value'].replace("http://wikibase.inguma.eus/entity/","")
			print('Found wikibase item via SPARQL: This item is on IWB, qid is '+iwbqid)
			continue
		press_key = input('No existing item found, also not by SPARQL. There will be created a new item, please confirm (y/n)')
		if press_key == "y":
			item = iwbi.wbi.item.new()

	statements = []
	for key in person.keys():
		if key in inguma.mappings['persons'] and len(str(person[key])) > 0:
			if inguma.mappings['persons'][key].startswith("str:"):
				prop = inguma.mappings['persons'][key].split(':')[1]
				writevalue = str(person[key]).strip()
				statements.append(iwbi.String(value=writevalue, prop_nr=prop))
			elif inguma.mappings['persons'][key].startswith("ext:"):
				prop = inguma.mappings['persons'][key].split(':')[1]
				writevalue = str(person[key]).strip()
				statements.append(iwbi.ExternalID(value=writevalue, prop_nr=prop))
			elif inguma.mappings['persons'][key].startswith("item:"):
				maptable = inguma.mappings['persons'][key]
				map = inguma.mappings[maptable][person[key]].split('_')
				#print(str(map))
				prop = map[0]
				writevalue = map[1]
				statements.append(iwbi.Item(value=writevalue, prop_nr=prop))
			# extra treatments
			elif inguma.mappings['persons'][key] == "secondSurname":
				try:
					namedate = re.search(r'^([\(]+)\((\d+) ?\- ?(\d+)\)',person['secondSurname'])
					statements.append(iwbi.String(value=namedate.group(1).strip(), prop_nr="P9"))
					birthyear = namedate.group(2)
					statements.append(iwbi.Time(time='+%'+birthyear+'-%01-%01T00:00:00Z', precision=9, prop_nr="P44"))
					deathyear = namedate.group(3)
					statements.append(iwbi.Time(time='+%'+deathyear+'-%01-%01T00:00:00Z', precision=9, prop_nr="P45"))
					print('Found dates in second surname, processed them.')
				except Exception:
					# print(traceback.format_exc())
					statements.append(iwbi.String(value=person[key].strip(), prop_nr="P9"))


	fullname = person['name'].strip()+' '+person['surname'].strip()+' '+person['secondSurname'].strip()
	item.labels.set(language="eu", value=fullname.rstrip())
	item.labels.set(language="en", value=fullname.rstrip())
	item.aliases.set(language="eu", values=[person['name'].strip()+' '+person['surname'].strip(),person['surname'].strip()+', '+person['name'].strip()])
	item.aliases.set(language="en", values=[person['name'].strip()+' '+person['surname'].strip(),person['surname'].strip()+', '+person['name'].strip()])
	item.descriptions.set(language="eu", value="Pertsona bat")
	item.claims.add(statements)
	d = False
	while d == False:
		try:
			r = item.write()
			d = True
		except Exception:
			ex = traceback.format_exc()
			# print(ex)
			if "wikibase-validator-label-with-description-conflict" in str(ex):
				print('Found an ambigouus person name, but with different clearName.')
				item.descriptions.set(language="eu", value="Beste pertsona bat")

	with open('D:/Inguma/person_ids_upload_done.txt', 'a', encoding="utf-8") as txtfile:
		txtfile.write(str(person['id'])+'\t'+person['cleanName']+'\n')
	qid = re.search(r"_BaseEntity__id='(Q\d+)'",str(r)).group(1)
	print('Finished writing person with id '+str(person['id'])+': '+fullname+', Qid: '+qid+'.\n')
