with open('data/ikergazte-doi.txt') as file:
	complete_doi = file.read().split('\n')

with open('data/wikibase-doi.txt') as file:
	wikibase_doi = file.read().split('\n')

missing = []
found = 0
for doi in complete_doi:
	if doi not in wikibase_doi:
		missing.append(doi)
	else:
		found += 1

print('Found '+str(found))
with open('data/missing-in-wikibase-doi.txt', 'w') as file:
	file.write('\n'.join(missing))
