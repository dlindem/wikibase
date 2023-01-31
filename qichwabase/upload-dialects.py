import csv, time, sys
import qwbi

with open('data/done-dialect-uploads.txt') as donefile:
	donelist = donefile.read().split('\n')

with open('data/csv-row-mapping.csv', encoding='utf8') as csvfile:
	idmapping = csv.reader(csvfile, delimiter=",")
	idmap = {}
	for mapping in idmapping:
		idmap[mapping[0]] = mapping[1]

with open('data/MASTER_dialects_upload.csv', encoding='utf8') as csvfile:
	source = csv.DictReader(csvfile, delimiter="\t")
	count = 0
	for row in source:
		count += 1
		interimid = row['id']
		del row['id']
		if interimid not in idmap:
			print('Fatal error: lexeme does not exist: '+interimid)
			input('Enter to continue')
			continue
		lid = idmap[interimid]
		if lid in donelist:
			print('Item has been done in previous run. Skipped.')
			continue
		# print('\n'+str(row))
		valueset = list(set(row.values()))
		writedict = {}
		for value in valueset:
			if value == '':
				continue
			# value = value.replace('; ', ';')
			writevalues = value.split(';')
			for writevalue in writevalues:
				writeval = writevalue.strip()
				if writeval not in writedict:
					writedict[writeval] = []
				for item in row:
					if row[item] == value:
						writedict[writeval].append(item)
		print('\n['+str(count)+'] Will write to '+lid+' ('+interimid+'):',str(writedict))

		lexeme = qwbi.wbi.lexeme.get(entity_id=lid)
		statements = []
		for lemmavariant in writedict:
			dialects = writedict[lemmavariant]
			qualifiers = []
			for dialect in dialects:
				qualifiers.append({"prop_nr":"P17", "type":"item", "value":dialect})
			statements.append({"prop_nr":"P16", "type":"string", "value":lemmavariant, "qualifiers":qualifiers})
		print(str(statements))

		for statement in statements:
			lexeme = qwbi.packstatements([statement], wbitem=lexeme)

		lexeme.write()
		with open('data/done-dialect-uploads.txt', 'a') as logfile:
			logfile.write(lexeme.id+'\n')
		print('Success for '+lexeme.id)


		# reverserow = {}
		# for key, value in row.items():
		# 	reverserow.setdefault(frozenset(value), []).append(key)
		#
		# writerow = {tuple(value) : set(key) for key, value in reverserow.items()}
		# print(str(writerow))

