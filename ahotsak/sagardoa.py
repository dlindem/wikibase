from nltk.tokenize import word_tokenize
import awbi

with open('sagardoa/sagardoari_iturria.txt', encoding="utf-8") as iturria:
	text = iturria.read()

texttitle = 'Sagardoari (1860)'
textitem = 'Q926'
wikisourcepageurl = 'https://eu.wikisource.org/wiki/Orrialde:Sagardoari_(1860).pdf/1'

tokens = word_tokenize(text)

numbered_tokens = {}

count = 0
for token in tokens:
	count += 1
	numbered_tokens[str(count)] = token

print(str(numbered_tokens))

for token in numbered_tokens:
	print('\nWill now process ', token, numbered_tokens[token])

	statements = [{'prop_nr': 'P3', 'type':'item', 'value': 'Q295'}] # instance of corpus token
	statements.append({'prop_nr': 'P28', 'type': 'string', 'value': token})  # token zenbakia hurrenkeran
	statements.append({'prop_nr': 'P26', 'type':'string', 'value': numbered_tokens[token]}) # jatorrizko forma
	statements.append({'prop_nr': 'P8', 'type': 'item', 'value': textitem})
	statements.append({'prop_nr': 'P27', 'type': 'url', 'value': wikisourcepageurl})  # wikisource page url

	awbi.itemwrite({'qid':False, 'labels':[{'lang': 'eu', 'value': numbered_tokens[token]}],
								'descriptions': [{'lang': 'eu', 'value': '#'+token+' '+texttitle}],
								'statements': statements}) # write to new Q-item
