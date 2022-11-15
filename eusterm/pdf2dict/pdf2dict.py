import re, time, json

with open('mendizaletasuna.txt') as infile:
	sarrerak = infile.read().split("@")

# parse entry
resultdict = []
for sarrera in sarrerak:
	result = {'id':None,'eusterm':None,'eustermqual':None,'sins':[],'eusdef':'','es':'','fr':'','en':''}
	id_and_eusterm = re.search('^([0-9]+) *\n([^\(]+)\(([0-9])\)([^@]+)',sarrera+'@')
	if id_and_eusterm.group(1):
		result['id'] = id_and_eusterm.group(1)
		print('Found term id',result['id'])
	if id_and_eusterm.group(2):
		result['eusterm'] = re.sub(' *\n *',' ',id_and_eusterm.group(2).strip())
		print('Found eusterm',result['eusterm'])
	if id_and_eusterm.group(3):
		result['eustermqual'] = id_and_eusterm.group(3)
		print('Found eustermqual',result['eustermqual'])
	if id_and_eusterm.group(4):
		body = id_and_eusterm.group(4)
		#print('\nBody:'+body)
	# else:
	# 	print('Found no body')
	# 	time.sleep(3)
	split1 = body.split('\nes\t')
	eusdeflines = split1[0].split('\n')
	for eusdefline in eusdeflines:
		if eusdefline.startswith('Sin.'):
			for singroup in eusdefline.split(')'):
				print(str(singroup))
				sinpair = singroup.split(' (')
				print(str(sinpair))
				sin = sinpair[0].replace('Sin. ','').replace(';','').strip()
				if len(sinpair) == 1:
					continue
				result['sins'].append({'sin':sin,'qual':sinpair[1]})
		else:
			result['eusdef'] += eusdefline+' '
	result['eusdef'] = result['eusdef'].strip()

	translines = split1[1].split('\n')
	print(str(translines))
	index = 0
	while not re.search('^[fe][rn]',translines[index]) and index < len(translines)-1:
		result['es'] += translines[index]+' '
		index += 1
	# print('ES:',result['es'])
	# print(str(index))
	lang = 'es'
	while index < len(translines):
		# if len(translines[index]) == 0:
		# 	index += 1
		# 	continue

		newlang = re.search('^[fe][rn]',translines[index])
		if newlang:
			if newlang.group(0) == lang:
				result[lang] = result[lang].strip()+"; "
			lang = newlang.group(0)

		result[lang] += re.sub('^[fe][rn]\t?','',translines[index]).strip()+' '
		index += 1

	result['es'] = result['es'].strip()
	result['fr'] = result['fr'].strip()
	result['en'] = result['en'].strip()
	print(str(result))


	resultdict.append(result)

with open('mendizaletasuna.json', 'w') as outfile:
	json.dump(resultdict, outfile, indent=2)
