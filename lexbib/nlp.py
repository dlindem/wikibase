import re, time
import charade
from nltk.tokenize import word_tokenize
# import spacy
# sp = {
# 'eng': spacy.load('en_core_web_sm'), # English
# 'spa': spacy.load('es_core_news_sm') # Spanish
# }

# lemmatize english text and clean it
def lemmatize_clean(bodytxt, lang="eng"):
	global sp
	bodylem = ""
	tokencount = 0
	for token in sp[lang](bodytxt):
		tokencount += 1
		bodylem+=("%s " % token.lemma_)
	# remove stop words
	lemtokens = word_tokenize(bodylem)
	#print(lemtokens)
	cleantokens = []
	stopchars = re.compile('[0-9\\/_\.:;,\(\)\[\]\{\}<>]') # tokens with any of these characters are skipped
	for token in lemtokens:
		if stopchars.search(token) == None:
			cleantokens.append(token)
	cleantext = ' '.join([str(x) for x in cleantokens])
	return (cleantext, tokencount)

import lxml
from xml.etree import ElementTree
from bs4 import BeautifulSoup

#grobid body text Function
def getgrobidbody(xmlfile):
	tree = ElementTree.parse(xmlfile)
	root = tree.getroot()
	ns = re.match(r'{.*}', root.tag).group(0)
	body = ElementTree.tostring(root[1][0])

	if (root[1][0].tag) == "{http://www.tei-c.org/ns/1.0}body":
		soup = BeautifulSoup(body, features="lxml")
		return re.sub(r'\n ', '\n', ' '.join(soup.find_all(text=True)).replace('  ',' '))
	else:
		print('File '+infile+' is strange, body not found.')
		time.sleep(5)
	return False

# check string encoding and return always utf-8
def check_encoding(txt, txtname="unknown"):
	txtenc = txt.encode()
	encoding = charade.detect(txtenc)
	if encoding['encoding'] == "utf-8":
		return txt
	else:
		print('Will change encoding of '+txtname+' from '+encoding['encoding']+' to utf-8...')
		time.sleep(0.5)
		return txtenc.decode(encoding['encoding'])

