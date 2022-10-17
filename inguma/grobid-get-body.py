import nlp
import os
import json

pdfFolder = 'D:/Inguma/fulltexts'

for file in os.listdir(pdfFolder):
	if file.endswith(".tei.xml"):
		print('Processing grobid TEI XML: '+file)
		bodytxt = nlp.getgrobidabstractbody(pdfFolder+'/'+file)
		# print(bodytxt)
		with open(pdfFolder+'/'+file.replace(".tei.xml","_txt.json"), "w", encoding="utf-8") as jsonfile:
			json.dump(bodytxt, jsonfile, indent=2)
