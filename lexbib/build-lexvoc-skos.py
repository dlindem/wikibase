from datetime import datetime
import json
import time
from rdflib import Graph, Namespace, BNode, URIRef, Literal
import lwbi # that is my lexbib wikibase I/O bot, here used for sparql queries

# entities_cache_file = 'D:/LexBib/lexmeta/entities-labels.json'
# statements_cache_file = 'D:/LexBib/lexmeta/statements.json'

owl_header = """@prefix : <http://w3id.org/meta-share/lexmeta/> .
@prefix bibo: <http://purl.org/ontology/bibo/> .
@prefix cc: <http://creativecommons.org/ns#> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix ms: <http://w3id.org/meta-share/meta-share/> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix swrc: <http://swrc.ontoware.org/ontology#> .
@prefix vann: <http://purl.org/vocab/vann/> .
@prefix lexmeta: <http://w3id.org/meta-share/lexmeta/> .
@base <http://w3id.org/meta-share/lexmeta/> .

<http://w3id.org/meta-share/lexmeta/> rdf:type owl:Ontology ;
                                       owl:versionIRI <http://w3id.org/meta-share/lexmeta/0.0.1> ;
									   bibo:status "Draft" ;
									   dct:modified \""""+datetime.now().replace(microsecond=0).isoformat()+"""\" ;
                                       dc:description "LexMeta, a metadata model for the description of human-readable and computational lexical resources in catalogues."@en ;
                                       dc:title "LexMeta ontology"@en ;
									   dc:abstract "LexMeta is a metadata model for the description of human-readable and computational lexical resources in catalogues. Our initial motivation is the extension of the LexBib knowledge graph with the addition of metadata for dictionaries, making it a catalogue of and about lexicographical works. The scope of the proposed model, however, is broader, aiming at the exchange of metadata with catalogues of Language Resources and Technologies and addressing a wider community of researchers besides lexicographers. For the definition of the LexMeta core classes and properties, we deploy widely used RDF vocabularies, mainly Meta-Share, a metadata model for Language Resources and Technologies, and FRBR, a model for bibliographic records."@en ;
                                       dct:creator "David Lindemann" ,
                                                   "Penny Labropoulou" ;
									   dct:contributor "Christiane Klaes" ,
									   			   "Katerina Gkirtzou" ;
                                       dct:license <http://purl.org/NET/rdflicense/cc-by4.0> ;
                                       vann:preferredNamespacePrefix "lexmeta" ;
                                       vann:preferredNamespaceUri <http://w3id.org/meta-share/lexmeta/> .
"""

range_expr_header = """@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix lexmeta: <http://w3id.org/meta-share/lexmeta/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

"""


skosrel_query = """# gets all skosrels between all terms

select ?Term ?skosrel ?skosrelLabel ?relterm

where {
 # ?facet ldp:P131 lwb:Q1 .
  ?Term ldp:P5 lwb:Q7;
 #       ldp:P72* ?facet ;
  ?skosrel ?relterm . values ?skosrel {ldp:P72 ldp:P73 ldp:P76 ldp:P77 ldp:P78}
  ?p wikibase:directClaim ?skosrel . ?p rdfs:label ?skosrelLabel . filter (lang(?skosrelLabel)="en")

  }

"""

print('\nThis will build LexVoc SKOS.\n')
presskey = input("Enter 's' for refreshing saved sparql result, any other input will skip query and load saved results.\n")

if presskey == "s":

	# terms = lwbi.wbi_helpers.execute_sparql_query(query=term_labels_query, prefix=lwbi.sparql_prefixes)['results']['bindings']
	# print('Got '+str(len(terms))+' terms with labels and collections.')
	# with open(entities_cache_file, "w", encoding="utf-8") as f:
	# 	json.dump(entities, f, indent=2)
	skosrels = lwbi.wbi_helpers.execute_sparql_query(query=skosrel_query, prefix=lwbi.sparql_prefixes)['results']['bindings']
	print('Got '+str(len(skosrels))+' statements.')
	# with open(statements_cache_file, "w", encoding="utf-8") as f:
	# 	json.dump(statements, f, indent=2)
else:
	sys.exit()
	# with open(entities_cache_file, encoding="utf-8") as f:
	# 	entities =  json.load(f, encoding="utf-8")
	# with open(statements_cache_file, encoding="utf-8") as f:
	# 	statements =  json.load(f, encoding="utf-8")

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

graph = Graph()

graph.parse(data=owl_header, format='turtle')

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

relmapping = {
'https://lexbib.elex.is/prop/direct/P72': skos.broader,
'https://lexbib.elex.is/prop/direct/P73': skos.narrower,
'https://lexbib.elex.is/prop/direct/P76': skos.related,
'https://lexbib.elex.is/prop/direct/P77': skos.closeMatch,
'https://lexbib.elex.is/prop/direct/P78': skos.exactMatch
}

# add terms relations, i.e. add terms that appear in any skos relation
termlog = []
for skosrel in skosrels:
	print(str(skosrel))
	subject = URIRef(skosrel['Term']['value'])
	subj_in_ns = skosrel['Term']['value'].replace('https://lexbib.elex.is/entity/', 'lwb:')
	if subj_in_ns not in termlog:
		termlog.append(subj_in_ns)
		graph.add((subject, rdf.type, skos.Concept))

	object = URIRef(skosrel['relterm']['value'])
	object_in_ns = skosrel['relterm']['value'].replace('https://lexbib.elex.is/entity/', 'lwb:')
	if object_in_nst not in termlog:
		termlog.append(object_in_ns)
		graph.add((object, rdf.type, skos.Concept))

	rel = relmapping[skosrel['skosrel']['value']]
	graph.add((subject, rel, object))

print('\nAdded to graph: '+str(len(termlog))+' terms and their skos relations.')

term_labels_query = """# gets LexBib Q7 items (terms), with their sources (collections), and definitions

select ?Term
(group_concat(distinct concat(?prefLabel,"@",lang(?prefLabel)) ;SEPARATOR="|") as ?prefLabels)
(group_concat(distinct concat(?altLabel,"@",lang(?altLabel)) ;SEPARATOR="|") as ?altLabels)
#?wikidata
(group_concat(distinct (str(?coll)) ;SEPARATOR="|") as ?colls)
(group_concat(distinct (str(?def)) ;SEPARATOR="|") as ?defs)
?corpus_hits

where {
  values ?Term {"""+" ".join(termlog) +"""}
  ?Term ?prefLabel;
        ldp:P74 ?coll.
 OPTIONAL { ?Term ldp:P80 ?def. }
 OPTIONAL { ?Term skos:altLabel ?altLabel.}
?Term lp:P109 [ lps:P109 ?corpus_hits ; lpq:P84 "LexBib en/es 12-2021"].

  } group by ?Term ?prefLabels ?altLabels ?colls ?defs ?corpus_hits
#    order by DESC (xsd:integer(?corpus_hits))
"""
termsquery = lwbi.wbi_helpers.execute_sparql_query(query=term_labels_query, prefix=lwbi.sparql_prefixes)['results']['bindings']
print('Got '+str(len(terms))+' terms with labels and collections.')

colllog = []
for row in termsquery:
	term = URIRef((row['Term']['value']))

	for item in row['prefLabels']['value'].split("|"):
		label = item.split("@")[0]
		labellang = item.split("@")[1]
		graph.add((term, rdfs.label, Literal(label, lang=labellang)))


	if 'altLabels' in row:
		for item in row['altLabels']['value'].split("|"):
			label = item.split("@")[0]
			labellang = item.split("@")[1]
			graph.add((term, skos.altLabel, Literal(label, lang=labellang)))

	# if 'corpus_hits' in row:
	# 	graph.add((owl_entity, skos.exactMatch, URIRef(entity['exact_match']['value'])))

	if 'colls' in row:
		for colluri in row['colls']['value'].split("|"):
			if colluri not in colllog:
				colllog.append(colluri)
		graph.add((URIRef(colluri), skos.member, term))

	if 'defs' in row:
		for definition in row['defs']['value'].split("|"):
			graph.add((term, skos.definition, Literal(definition, lang="en")))

graph.serialize(destination="lexvoc_skos.ttl", format="turtle")

# with open(lexvoc_skos.ttl", "w", encoding="utf-8") as file:
# 	file.write("@base <http://w3id.org/meta-share/lexmeta/> .\n")
# 	with open("D:/GitHub/LexMeta/lexmeta_interim.ttl", "r", encoding="utf-8") as interimfile:
# 		interim = interimfile.read().replace("lexmeta: a owl:Ontology", "<http://w3id.org/meta-share/lexmeta/> a owl:Ontology").replace("vann:preferredNamespaceUri lexmeta: ","vann:preferredNamespaceUri <http://w3id.org/meta-share/lexmeta/> ")
# 	file.write(interim)

print("Lexvoc SKOS TTL file updated.")
