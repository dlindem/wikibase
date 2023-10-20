import re, time, json, sys

with open('soziolinguistika.txt') as infile:
	sarrerak = infile.read().split("@")

languages = ['es', 'fr', 'en']

# parse entry
resultdict = []
for sarrera in sarrerak:
	print('\n'+sarrera)
	result = {'id':None,'eusterm':None,'eustermqual':None,'sins':[],'eusdef':'','es':'','esdef':'','fr':'','frdef':'','en':'','endef':''}
	id_and_eusterm = re.search('([0-9]+) ([^\[]+)\[([0-9])\]\n([^§]+)§([^\n]+)',sarrera)
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
		eusdefline = id_and_eusterm.group(4)
		print('eusdef:'+eusdefline)
		#OHARRA
	if id_and_eusterm.group(5):
		body = id_and_eusterm.group(5)
		# print('\nBody:'+body)
	else:
		print('Found no body')
		time.sleep(3)
	# split1 = body.split('%')
	# eusdeflines = split1[0].split('\n')

	if eusdefline.startswith('Sin.'):

		for singroup in eusdefline.split(']'):
			print(str(singroup))
			sinpair = singroup.split(' [')
			print(str(sinpair))

			sin = sinpair[0].replace('Sin. ','').replace(';','').strip()
			if len(sinpair) == 1:
				continue
			result['sins'].append({'sin':sin,'qual':sinpair[1]})
		result['eusdef'] = sinpair[0].strip().strip() # last rest after last ] bracket
	else:
		result['eusdef'] += eusdefline.strip().strip()
	result['eusdef'] = re.sub('OHARRA: .*','', result['eusdef'])

	translines = sarrera.split('§')[1].split('%')
	# print(str(translines))

	# while not re.search('^[fe][rn]',translines[index]) and index < len(translines)-1:
	# 	result['es'] += translines[index]+' '
	# 	index += 1
	# # print('ES:',result['es'])
	# # print(str(index))
	# lang = 'es'
	for transline in translines:
		transline = re.sub(r'\n','',transline)
		print('Transline',transline)


		# if len(translines[index]) == 0:
		# 	index += 1
		# 	continue

		langre = re.search('([fe][rns]) (.+)',transline)
		if langre:
			lang = langre.group(1).strip()
			value = langre.group(2).strip()
			if lang in languages:
				if '$' in value:
					valueparts = value.split('$')
					result[lang] = valueparts[0].strip()
					result[lang+'def'] = valueparts[1].strip()
				else:
					result[lang] = value
				# result[lang+'def'] +=





	print(str(result))


	resultdict.append(result)

with open('soziolinguistika.json', 'w') as outfile:
	json.dump(resultdict, outfile, indent=2)
