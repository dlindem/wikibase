import re, json

with open('content/productions.json', 'r', encoding="utf-8") as injson:
	text = injson.read()

doilist = re.findall('http[^ ]+ikergazte[^"]+', text)

with open('data/ikergazte-doi.txt', 'w', encoding="utf-8") as outtxt:
	outtxt.write('\n'.join(doilist))
