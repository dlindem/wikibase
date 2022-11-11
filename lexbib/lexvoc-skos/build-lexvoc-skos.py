from datetime import datetime
import json
import time
from rdflib import Graph, Namespace, BNode, URIRef, Literal
from otsrdflib import OrderedTurtleSerializer
import lwbi # that is my lexbib wikibase I/O bot, here used for sparql queries

# entities_cache_file = 'D:/LexBib/lexmeta/entities-labels.json'
# statements_cache_file = 'D:/LexBib/lexmeta/statements.json'

contributors_query = """# gets LexVoc contributors from Q70 P172

select *

where { lwb:Q70 ldp:P172 ?contributor .
       ?contributor ldp:P101 ?firstname; ldp:P102 ?lastname .
	   optional {?contributor ldp:P2 ?wikidata.}
	   optional {?contributor ldp:P39 ?orcid.}

  } order by ?contributor
"""


skosrel_query = """# gets all skosrels between all terms in the LexVoc facets concept tree

select ?Term ?skosrel ?skosrelLabel ?relterm

where {
  ?facet ldp:P131 lwb:Q1 .
  ?Term ldp:P5 lwb:Q7;
        ldp:P72* ?facet ;
  ?skosrel ?relterm . values ?skosrel {ldp:P72 ldp:P73 ldp:P76 ldp:P77 ldp:P78}
  ?p wikibase:directClaim ?skosrel . ?p rdfs:label ?skosrelLabel . filter (lang(?skosrelLabel)="en")

  }

"""

print('\nThis will build LexVoc SKOS.\n')

skosrels = lwbi.wbi_helpers.execute_sparql_query(query=skosrel_query, prefix=lwbi.sparql_prefixes)['results']['bindings']
print('Got '+str(len(skosrels))+' statements.')

wikibase = Namespace('https://lexbib.elex.is/entity/')
wikidata = Namespace('http://www.wikidata.org/entity/')
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
rdf = Namespace ('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
lexmeta = Namespace ('http://w3id.org/meta-share/lexmeta/')
bibo = Namespace ('http://purl.org/ontology/bibo/')
owl = Namespace ('http://www.w3.org/2002/07/owl')
frbr = Namespace ('http://purl.org/vocab/frbr/core#')
frbrer = Namespace('http://iflastandards.info/ns/fr/frbr/frbrer/')
schema = Namespace('http://schema.org/')
dct = Namespace('http://purl.org/dc/terms/')
ms = Namespace('http://w3id.org/meta-share/meta-share/')
lexinfo = Namespace('http://www.lexinfo.net/ontology/3.0/lexinfo#')
gold = Namespace('http://purl.org/linguistics/gold/')
foaf = Namespace('http://xmlns.com/foaf/0.1/')

graph = Graph()

# graph.parse(data=owl_header, format='turtle')

graph.bind("lexbib", wikibase)
graph.bind("wikidata", wikidata)
graph.bind("skos", skos)
graph.bind("rdfs", rdfs)
graph.bind("lexmeta", lexmeta)
graph.bind("rdf", rdf)
graph.bind("bibo", bibo)
graph.bind("owl", owl)
graph.bind("frbr", frbr)
graph.bind("frbrer", frbrer)
graph.bind("schema", schema)
graph.bind("dct", dct)
graph.bind("ms", ms)
graph.bind("lexinfo", lexinfo)
graph.bind("gold", gold)
graph.bind("foaf", foaf)

graph.add((wikibase.Q70, rdf.type, skos.ConceptScheme))
graph.add((wikibase.Q70, schema.about, URIRef("http://lexbib.elex.is/wiki/LexVoc")))
graph.add((wikibase.Q70, skos.prefLabel, Literal("LexVoc")))
graph.add((wikibase.Q70, dct.description, Literal("a SKOS vocabulary of lexicographic concepts")))
graph.add((wikibase.Q70, dct.creator, wikibase.Q1650))
graph.add((wikibase.Q70, dct.license, URIRef("http://purl.org/NET/rdflicense/cc-by4.0")))
graph.add((wikibase.Q70, schema.version, Literal("1.0")))
graph.add((wikibase.Q70, dct.modified, Literal(datetime.now().replace(microsecond=0).isoformat())))

lexvoc_facets = {  # hardcoded!!! TBD: change to live query
"Q14280": "linguistic property",
"Q14285": "dictionary function",
"Q14290": "dictionary distribution",
"Q14291": "dictionary structure",
"Q14317": "dictionary use",
"Q14352": "NLP",
"Q16014": "dictionary linguality",
"Q16015": "lexicographical process",
"Q16094": "dictionary scope",
"Q16129": "dictionary access"
}

for facet in lexvoc_facets:
	graph.add((wikibase.Q70, skos.hasTopConcept, URIRef("https://lexbib.elex.is/entity/"+facet)))
	graph.add((URIRef("https://lexbib.elex.is/entity/"+facet), skos.prefLabel, Literal(lexvoc_facets[facet], lang="en")))

contributors = lwbi.wbi_helpers.execute_sparql_query(query=contributors_query, prefix=lwbi.sparql_prefixes)['results']['bindings']
print('Got '+str(len(contributors))+' LexVoc contributors.')

for person in contributors:
	personUri = URIRef(person['contributor']['value'])
	graph.add((wikibase.Q70, dct.contributor, personUri))
	graph.add((personUri, rdf.type, foaf.Person))
	graph.add((personUri, foaf.givenName, Literal(person['firstname']['value'])))
	graph.add((personUri, foaf.familyName, Literal(person['lastname']['value'])))
	if 'wikidata' in person:
		graph.add((personUri, skos.exactMatch, URIRef('http://www.wikidata.org/entity/'+person['wikidata']['value'])))
	if 'orcid' in person:
		graph.add((personUri, skos.exactMatch, URIRef('https://orcid.org/'+person['orcid']['value'])))

relmapping = {
'https://lexbib.elex.is/prop/direct/P72': skos.broader,
'https://lexbib.elex.is/prop/direct/P73': skos.narrower,
'https://lexbib.elex.is/prop/direct/P77': skos.related
# 'https://lexbib.elex.is/prop/direct/P76': skos.closeMatch,
# 'https://lexbib.elex.is/prop/direct/P78': skos.exactMatch
}

# add terms relations, i.e. add terms that appear in any skos relation
termlog = []
for skosrel in skosrels:
	# print(str(skosrel))
	subject = URIRef(skosrel['Term']['value'])
	subj_in_ns = skosrel['Term']['value'].replace('https://lexbib.elex.is/entity/', 'lwb:')
	if subj_in_ns not in termlog:
		termlog.append(subj_in_ns)
		graph.add((subject, rdf.type, skos.Concept))
		graph.add((subject, skos.inScheme, wikibase.Q70))

	object = URIRef(skosrel['relterm']['value'])
	object_in_ns = skosrel['relterm']['value'].replace('https://lexbib.elex.is/entity/', 'lwb:')
	if object_in_ns not in termlog:
		termlog.append(object_in_ns)
		graph.add((object, rdf.type, skos.Concept))
		graph.add((object, skos.inScheme, wikibase.Q70))

	rel = relmapping[skosrel['skosrel']['value']]
	graph.add((subject, rel, object))

print('\nAdded to graph: '+str(len(termlog))+' terms and their skos relations.')

term_labels_query = """# gets LexBib Q7 items (terms), with their sources (collections), and definitions

select ?Term
(group_concat(distinct concat(?prefLabel,"@",lang(?prefLabel)) ;SEPARATOR="|") as ?prefLabels)
(group_concat(distinct concat(?altLabel,"@",lang(?altLabel)) ;SEPARATOR="|") as ?altLabels)
(group_concat(distinct (str(?wd)) ;SEPARATOR="|") as ?wikidata)
(group_concat(distinct (str(?coll)) ;SEPARATOR="|") as ?colls)
(group_concat(distinct (str(?def)) ;SEPARATOR="|") as ?defs)
(group_concat(distinct (str(?source_uri)) ;SEPARATOR="|") as ?source_uris)
?lexmetauri
(group_concat(distinct (str(?exact_match)) ;SEPARATOR="|") as ?exact_matches)

where {

  ?Term ldp:P5 lwb:Q7; rdfs:label ?prefLabel.
 OPTIONAL { ?Term lp:P74 ?collst . ?collst lps:P74 ?coll. OPTIONAL {?collst prov:wasDerivedFrom [lpr:P108 ?source_uri]. } }
 OPTIONAL { ?Term ldp:P80 ?def. }
 OPTIONAL { ?Term skos:altLabel ?altLabel. }
 OPTIONAL { ?Term ldp:P2 ?wd. }
 OPTIONAL { ?Term lp:P42 ?lexmetast. ?lexmetast lps:P42 ?lexmetauri . OPTIONAL { ?lexmetast prov:wasDerivedFrom [lpr:P167 ?exact_match]. } }
?Term lp:P109 [ lps:P109 ?corpus_hits ; lpq:P84 "LexBib en/es 07-2022"].

  } group by ?Term ?prefLabels ?altLabels ?wikidata ?colls ?defs ?source_uris ?lexmetauri ?exact_matches

"""
termsquery = lwbi.wbi_helpers.execute_sparql_query(query=term_labels_query, prefix=lwbi.sparql_prefixes)['results']['bindings']
print('Got '+str(len(termsquery))+' terms with labels and collections.')

colllog = []
for row in termsquery:
	term = URIRef((row['Term']['value']))

	for item in row['prefLabels']['value'].split("|"):
		label = item.split("@")[0]
		labellang = item.split("@")[1]
		graph.add((term, skos.prefLabel, Literal(label, lang=labellang)))


	if 'altLabels' in row:
		for item in row['altLabels']['value'].split("|"):
			label = item.split("@")[0]
			labellang = item.split("@")[1]
			graph.add((term, skos.altLabel, Literal(label, lang=labellang)))

	# if 'corpus_hits' in row:
	# 	graph.add((owl_entity, skos.exactMatch, URIRef(entity['exact_match']['value'])))

	if 'colls' in row:
		for colluri in row['colls']['value'].split("|"):
			if colluri == "https://lexbib.elex.is/entity/Q49": # exclude MetaShare (which is treated using ldp:P42)
				continue
			colllog.append(colluri)
			graph.add((URIRef(colluri), skos.member, term))

	if 'source_uris' in row:
		for source_uri in row['source_uris']['value'].split("|"):
			graph.add((term, skos.closeMatch, URIRef("http://lexbib.elex.is/entity/"+source_uri)))

	if 'lexmetauri' in row:
		graph.add((term, skos.exactMatch, URIRef(row['lexmetauri']['value'])))

	if 'exact_matches' in row:
		for exact_match in row['exact_matches']['value'].split("|"):
			graph.add((term, skos.exactMatch, URIRef(exact_match)))

	if 'wikidata' in row:
		for wdqid in row['wikidata']['value'].split("|"):
			graph.add((term, skos.closeMatch, URIRef("http://www.wikidata.org/entity/"+wdqid)))

	if 'defs' in row:
		for definition in row['defs']['value'].split("|"):
			graph.add((term, skos.definition, Literal(definition, lang="en")))

collset = list(dict.fromkeys(colllog))
# print(str(collset))
for coll in collset:
	graph.add((URIRef(coll), rdf.type, skos.Collection))
	collitem = lwbi.wbi.item.get(entity_id=coll.replace("https://lexbib.elex.is/entity/",""))
	colllabel = collitem.labels.get('en').value
	print('Processing collection metadata for: '+colllabel)
	graph.add((URIRef(coll), skos.prefLabel, Literal(colllabel, lang="en")))
	try:
		collsource = collitem.claims.get('P83')[0].mainsnak.datavalue['value']['id']
		graph.add((URIRef(coll), dct.source, URIRef("https://lexbib.elex.is/entity/"+collsource)))
		print('Found and added collection source item.')
	except:
		print('Failed to find and add collection source item.')
		pass
	try:
		collsource = collitem.claims.get('P108')[0].mainsnak.datavalue['value']
		graph.add((URIRef(coll), dct.source, URIRef("https://lexbib.elex.is/entity/"+collsource)))
		print('Found and added collection source URI.')
	except:
		print('Failed to find and add collection source URI.')
		pass

serializer = OrderedTurtleSerializer(graph)
serializer.class_order = [
    skos.ConceptScheme,
    foaf.Person,
    skos.Concept,
	skos.Collection
]

with open("lexvoc_skos.ttl", 'wb') as ttl_file:
	serializer.serialize(ttl_file)
print("Lexvoc SKOS TTL file updated.")
graph.serialize(destination="lexvoc_skos.xml", format="xml")
print("Lexvoc SKOS XML file updated.")

# with open(lexvoc_skos.ttl", "w", encoding="utf-8") as file:
# 	file.write("@base <http://w3id.org/meta-share/lexmeta/> .\n")
# 	with open("D:/GitHub/LexMeta/lexmeta_interim.ttl", "r", encoding="utf-8") as interimfile:
# 		interim = interimfile.read().replace("lexmeta: a owl:Ontology", "<http://w3id.org/meta-share/lexmeta/> a owl:Ontology").replace("vann:preferredNamespaceUri lexmeta: ","vann:preferredNamespaceUri <http://w3id.org/meta-share/lexmeta/> ")
# 	file.write(interim)
