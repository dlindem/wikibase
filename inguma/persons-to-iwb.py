import iwbi
import inguma
import json, re

with open('D:/Inguma/persons.json', 'r') as jsonfile:
	persons = json.load(jsonfile)
with open('D:/Inguma/person_ids_upload_done.txt', encoding="utf-8") as txtfile:
	donelistwithcomments = txtfile.read().split('\n')
	donelist = []
	for done in donelistwithcomments:
		try:
			donelist.append(int(re.search(r'^(\d+)',done).group(1)))
		except:
			pass

seen_clearnames = []
index = 0
for person in persons:
	index +=1
	print('['+str(index)+'] Now processing Person with id '+str(person['id'])+'... '+str(len(persons)-index)+' items left.')
	if person['cleanName'] in seen_clearnames:
		print('This clearName has already been seen in this dataset: '+person['cleanName']+', added mark in donelist file.\n')
		with open('D:/Inguma/person_ids_upload_done.txt', 'a', encoding="utf-8") as txtfile:
			txtfile.write(str(person['id'])+'\tDUPLICATE\t'+person['cleanName']+'\n')
			continue
	seen_clearnames.append(person['cleanName'])
	if person['id'] in donelist:
		print('Person with id '+str(person['id'])+' is already uploaded, skipped.\n')
		continue
	statements = []
	for key in person.keys():
		if key in inguma.mappings['persons'] and len(str(person[key])) > 0:
			if inguma.mappings['persons'][key].startswith("str:"):
				prop = inguma.mappings['persons'][key].split(':')[1]
				writevalue = str(person[key]).strip()
				statement = iwbi.String(value=writevalue, prop_nr=prop)
			elif inguma.mappings['persons'][key].startswith("ext:"):
				prop = inguma.mappings['persons'][key].split(':')[1]
				writevalue = str(person[key]).strip()
				statement = iwbi.ExternalID(value=writevalue, prop_nr=prop)
			elif inguma.mappings['persons'][key].startswith("item:"):
				maptable = inguma.mappings['persons'][key]
				map = inguma.mappings[maptable][person[key]].split('_')
				#print(str(map))
				prop = map[0]
				writevalue = map[1]
				statement = iwbi.Item(value=writevalue, prop_nr=prop)
		statements.append(statement)
	item = iwbi.wbi.item.new()
	fullname = person['name'].strip()+' '+person['surname'].strip()+' '+person['secondSurname'].strip()
	item.labels.set(language="eu", value=fullname.rstrip())
	item.labels.set(language="en", value=fullname.rstrip())
	item.aliases.set(language="eu", values=[person['name'].strip()+' '+person['surname'].strip(),person['surname'].strip()+', '+person['name'].strip()])
	item.aliases.set(language="en", values=[person['name'].strip()+' '+person['surname'].strip(),person['surname'].strip()+', '+person['name'].strip()])
	item.descriptions.set(language="eu", value="Pertsona bat")
	item.claims.add(statements)
	r = item.write()
	with open('D:/Inguma/person_ids_upload_done.txt', 'a', encoding="utf-8") as txtfile:
		txtfile.write(str(person['id'])+'\n')
	qid = re.search(r"_BaseEntity__id='(Q\d+)'",str(r)).group(1)
	print('Finished writing person with id '+str(person['id'])+': '+person['surname']+', Qid: '+qid+'.\n')
