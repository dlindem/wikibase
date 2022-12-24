# creates descriptions for all instances of a class
import time
import requests
import lwb


descriptions = {
# "Q2": "a LexBib Ontology Class",
"Q4":"a lexical-conceptual resource",
# "Q5":"a person"
# "Q6":"an event",
# "Q7":"a term",
# "Q8":"a natural language",
# "Q9":"a place",
# "Q10":"a project",
# "Q11":"an organization",
# "Q20":"a journal",
# "Q18":"a proceedings volume",
# "Q17":"a country",
# "Q16":"a serial publication volume",
# "Q41":"a lexicographical work",
# "Q21":"a BibItem type"
# "Q34":"a conference series",
# "Q12":"a BibCollection",
# "Q53": "a skos:ConceptScheme",
# "Q33": "a skos:Collection (a term source)"

}

override_existing_descriptions = [
"Q53", "Q33"
] # will replace existing descriptions

wikilang = "en"

for classqid in descriptions:
	description = descriptions[classqid]
	if classqid in override_existing_descriptions:
		print('Will now get a list of all instances of class '+classqid+', will replace existing descriptions.')

		url = "https://lexbib.elex.is/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttps%3A%2F%2Flexbib.elex.is%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttps%3A%2F%2Flexbib.elex.is%2Fprop%2Fdirect%2F%3E%0Aselect%20%3Furi%20%3Fdesc%20where%0A%7B%0A%3Furi%20ldp%3AP5%20lwb%3A"+classqid+".%7D"
		done = False
		while (not done):
			try:
				r = requests.get(url)
				bindings = r.json()['results']['bindings']
			except Exception as ex:
				print('Error: SPARQL request failed: '+str(ex))
				time.sleep(2)
				continue
			done = True
		#print(str(bindings))

		print('Found '+str(len(bindings))+' instances.\n')
	else:
		print('Will now get a list of all those instances of class '+classqid+' that have no description.')

		url = "https://lexbib.elex.is/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttps%3A%2F%2Flexbib.elex.is%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttps%3A%2F%2Flexbib.elex.is%2Fprop%2Fdirect%2F%3E%0Aselect%20%3Furi%20%3Fdesc%20where%0A%7B%0A%3Furi%20ldp%3AP5%20lwb%3A"+classqid+".%0A%20%20FILTER%20NOT%20EXISTS%20%7B%3Furi%20schema%3Adescription%20%3Fdesc%7D%0A%20%20%7D"
		done = False
		while (not done):
			try:
				r = requests.get(url)
				bindings = r.json()['results']['bindings']
			except Exception as ex:
				print('Error: SPARQL request failed: '+str(ex))
				time.sleep(2)
				continue
			done = True
		#print(str(bindings))

		print('Found '+str(len(bindings))+' instances.\n')


	count = 0
	for item in bindings:
		count +=1
		lwbitem = item['uri']['value'].replace("https://lexbib.elex.is/entity/","")
		desc = lwb.setdescription(lwbitem,wikilang,description)
		if desc:
			print('OK. '+str(len(bindings)-count)+' items left.\n')
