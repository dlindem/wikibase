import re, time
import charade
from nltk.tokenize import word_tokenize
import spacy
import config_private

sp = None
sp_lang = None
def sp_load(iso):
	global sp_lang
	sp_lang = iso
	if iso == 'eng':
		return spacy.load('en_core_web_sm') # English
	if iso == 'spa':
		return spacy.load('es_core_news_sm') # Spanish
	if iso == 'fra':
		return spacy.load('fr_core_news_sm') # French
	if iso == 'deu':
		return spacy.load('de_core_news_sm') # German
	if iso == 'por':
		return spacy.load('pt_core_news_sm') # Portuguese
	if iso == 'ell':
		return spacy.load('el_core_news_sm') # Greek
	if iso == 'cat':
		return spacy.load('ca_core_news_sm') # Catalan
	if iso == 'hrv':
		return spacy.load('hr_core_news_sm') # Croatian
	if iso == 'ron':
		return spacy.load('ro_core_news_sm') # Romanian
	if iso == 'ukr':
		return spacy.load('uk_core_news_sm') # Ukranian
	if iso == 'lit':
		return spacy.load('lt_core_news_sm') # German

# lemmatize text and clean it
def lemmatize_clean(bodytxt, lang="eng"):
	if not bodytxt or len(bodytxt)<2 :
		return ''
	global sp
	global sp_lang
	if sp_lang != lang: # if new lang, load new model (if same lang than before, do not load again)
		sp = sp_load(lang)
		print(f"Loaded spacy model: {sp}")
	bodylem = ""
	tokencount = 0
	for token in sp(bodytxt[0:999999]):
		tokencount += 1
		#bodylem += ("%s " % token.lemma_)
		if len(token.lemma_) > 0:
			bodylem += (f"{token.lemma_} ")
	# remove stop words
	lemtokens = word_tokenize(bodylem)
	#print(lemtokens)
	cleantokens = []
	stopchars = re.compile('[\\/_\.:;,\(\)\[\]\{\}<>\!]') # tokens with any of these characters are skipped
	for token in lemtokens:
		if stopchars.search(token) == None and token not in config_private.stopwords:
			cleantokens.append(token)
	cleantext = ' '.join([str(x) for x in cleantokens])
	return cleantext
	# return ({'lemmatized': cleantext, 'tokencount': tokencount})

import lxml
from xml.etree import ElementTree
from bs4 import BeautifulSoup

#grobid body text Function
def getgrobidbody(xmlfile):
	tree = ElementTree.parse(xmlfile)
	root = tree.getroot()
	ns = re.match(r'{.*}', root.tag).group(0)

	for text_elem in root.findall(f"{ns}text"):
		for body_elem in text_elem.findall(f"{ns}body"):
			# body = ElementTree.tostring(root[1][0])
			body = ElementTree.tostring(body_elem)


			soup = BeautifulSoup(body, features="lxml")
			return re.sub(r'\n ', '\n', ' '.join(soup.find_all(text=True)).replace('  ',' '))

def getgrobidabstractbody(xmlfile):
	tree = ElementTree.parse(xmlfile)
	root = tree.getroot()
	# ns = re.match(r'{.*}', root.tag).group(0)
	# print(ns)
	# body = ElementTree.tostring(root[1][0])
	abstract = None
	body = None
	for firstchild in root:
		if firstchild.tag == "{http://www.tei-c.org/ns/1.0}teiHeader":
			for secondchild in firstchild:
				if secondchild.tag == "{http://www.tei-c.org/ns/1.0}profileDesc":
					for thirdchild in secondchild:
						if thirdchild.tag == "{http://www.tei-c.org/ns/1.0}abstract": # abstract element can be more than one! consider element's xml:lang: TBD (Basque is not well identified by Grobid)
							if abstract: # if there was another one
								abstract += '\n\n'
							else:
								abstract = ''
							soup = BeautifulSoup(ElementTree.tostring(thirdchild), features="lxml")
							abstract += re.sub(r'[\r\n] *', '', ' '.join(soup.find_all(text=True)).replace(' + ',' '))
							if abstract == '':
								abstract = None
		if firstchild.tag == "{http://www.tei-c.org/ns/1.0}text":
			for secondchild in firstchild:
				if secondchild.tag == "{http://www.tei-c.org/ns/1.0}body":
					soup = BeautifulSoup(ElementTree.tostring(secondchild), features="lxml")
					body = re.sub(r'[\r\n] *', '', ' '.join(soup.find_all(text=True)).replace(' + ',' '))
					if body == '':
						body = None
	return {'abstract':abstract,'body':body}


# check string encoding and return always utf-8
def check_encoding(txt, txtname="unknown"):
	txtenc = txt.encode()
	encoding = charade.detect(txtenc)
	if encoding['encoding'] == "utf-8":
		return txt
	else:
		print('Will change encoding of '+txtname+' from '+encoding['encoding']+' to utf-8...')
		return txtenc.decode(encoding['encoding'])

