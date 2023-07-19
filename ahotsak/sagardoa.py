from nltk.tokenize import word_tokenize

with open('sagardoa/sagardoari_iturria.txt', encoding="utf-8") as iturria:
	text = iturria.read()

tokens = word_tokenize(text)

numbered_tokens = {}

count = 0
for token in tokens:
	count += 1
	numbered_tokens[str(count)] = token

print(str(numbered_tokens))