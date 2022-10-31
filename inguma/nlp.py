import re
# from nltk.tokenize import word_tokenize
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

# #grobid body text Function
# def getgrobidbody(xmlfile):
# 	tree = ElementTree.parse(xmlfile)
# 	root = tree.getroot()
# 	# ns = re.match(r'{.*}', root.tag).group(0)
# 	body = ElementTree.tostring(root[1][0])
#
# 	if (root[1][0].tag) == "{http://www.tei-c.org/ns/1.0}body":
# 	   	soup = BeautifulSoup(body, features="lxml")
# 	   	return re.sub(r'\n ', '\n', ' '.join(soup.find_all(text=True)).replace('  ',' '))
# 	else:
# 	   	print('File '+infile+' is strange, body not found.')
# 	   	time.sleep(5)
# 	return False

#grobid body text Function
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
								abstract == None
		if firstchild.tag == "{http://www.tei-c.org/ns/1.0}text":
			for secondchild in firstchild:
				if secondchild.tag == "{http://www.tei-c.org/ns/1.0}body":
					soup = BeautifulSoup(ElementTree.tostring(secondchild), features="lxml")
					body = re.sub(r'[\r\n] *', '', ' '.join(soup.find_all(text=True)).replace(' + ',' '))
					if body == '':
						body = None
	return {'abstract':abstract,'body':body}
