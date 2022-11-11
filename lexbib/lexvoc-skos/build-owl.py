from datetime import datetime
import json
import time
from rdflib import Graph, Namespace, BNode, URIRef, Literal
import lwbi # that is my lexbib wikibase I/O bot, here used for sparql queries

entities_cache_file = 'D:/LexBib/lexmeta/entities-labels.json'
statements_cache_file = 'D:/LexBib/lexmeta/statements.json'

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

entities_labels_query = """# gets LexMeta OWL entities with labels and exact_matches

select ?entity ?owl_entity (group_concat(distinct str(?owl_class);SEPARATOR="|") as ?owl_classes)
?exact_match ?owl_domain ?owl_range ?owl_range_expr ?owl_subPropOf
(group_concat(distinct concat(?entityLabel,"@",lang(?entityLabel)) ;SEPARATOR="|") as ?entityLabels)
(group_concat(distinct concat(?altLabel,"@",lang(?altLabel)) ;SEPARATOR="|") as ?entityAltLabels)
(group_concat(distinct str(?close_match);SEPARATOR="|") as ?close_matches)

where {
  ?entity lp:P42 ?owl_statement;
          rdfs:label ?entityLabel.
  ?owl_statement lps:P42 ?owl_entity; lpq:P166 ?owl_class.
  optional {?owl_statement lpq:P167 ?exact_match}.
  optional {?owl_statement lpq:P169 ?owl_subPropOf}.
  optional {?entity ldp:P168 ?domain. ?domain ldp:P42 ?owl_domain.}
  optional {?entity lp:P48 ?range_statement. ?range_statement lps:P48 ?range. ?range ldp:P42 ?owl_range.
  			optional {?range_statement lpq:P170 ?owl_range_expr .}}
  optional {?entity lp:P74 [lps:P74 ?coll; prov:wasDerivedFrom [lpr:P108 ?close_match]] .
            values ?coll {lwb:Q15469 lwb:Q14512} # lexInfo or GOLD
			}

 optional {?entity skos:altLabel ?altLabel.}
  }

group by ?entity ?owl_entity ?owl_classes ?exact_match
         ?owl_domain ?owl_range ?owl_range_expr ?owl_subPropOf ?entityLabels ?entityAltLabels ?close_matches

"""

statements_query = """# gets subject, prop, obj for LexMeta-relevant properties

select ?s ?lexmeta_owl_subj ?p ?edge ?lexmeta_owl_prop ?o ?lexmeta_owl_obj ?obj_datatype
where {
  ?s ?p ?o ;
     lp:P42 [lps:P42 ?lexmeta_owl_subj; lpq:P166 ?owl_class] .
  ?edge wikibase:directClaim ?p;
        ldp:P42 ?lexmeta_owl_prop ;
        <http://wikiba.se/ontology#propertyType> ?obj_datatype .
  optional {?o ldp:P42 ?lexmeta_owl_obj .}

  }

"""

print('\nThis will build LexMeta OWL.\n')
presskey = input("Enter 's' for refreshing saved sparql result, any other input will skip query and load saved results.\n")

if presskey == "s":

	entities = lwbi.wbi_helpers.execute_sparql_query(query=entities_labels_query, prefix=lwbi.sparql_prefixes)['results']['bindings']
	print('Got '+str(len(entities))+' entities.')
	with open(entities_cache_file, "w", encoding="utf-8") as f:
		json.dump(entities, f, indent=2)
	statements = lwbi.wbi_helpers.execute_sparql_query(query=statements_query, prefix=lwbi.sparql_prefixes)['results']['bindings']
	print('Got '+str(len(statements))+' statements.')
	with open(statements_cache_file, "w", encoding="utf-8") as f:
		json.dump(statements, f, indent=2)
else:
	with open(entities_cache_file, encoding="utf-8") as f:
		entities =  json.load(f, encoding="utf-8")
	with open(statements_cache_file, encoding="utf-8") as f:
		statements =  json.load(f, encoding="utf-8")

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

# create prop for wikibase equivalent entity (used for pointing to lexbib wikibase and for wikidata entities)
graph.add((lexmeta.wikibaseEntity, rdf.type, URIRef('http://www.w3.org/2002/07/owl#ObjectProperty')))

# create entities-labels derived from wikibase entities
for entity in entities:

	owl_entity = URIRef(entity['owl_entity']['value'])

	if 'owl_classes' in entity:
		for owl_class in entity['owl_classes']['value'].split("|"):
			graph.add((owl_entity, rdf.type, URIRef(owl_class)))

	if entity['owl_entity']['value'].startswith("http://w3id.org/meta-share/lexmeta/"): # only write labels for entities in lexmeta ns
		for item in entity['entityLabels']['value'].split("|"):
			label = item.split("@")[0]
			if label == "wikidata entity": # lexbib:P2, on LexBib wikibase, is used for pointing to wikidata equivalents; here, it is extended to pointing back to LexBib Wikibase entities as well.
				label = "wikibase entity"
				graph.add((owl_entity, rdfs.comment, Literal("Points to an equivalent entity described on wikidata or another wikibase.", lang="en")))
			labellang = item.split("@")[1]
			graph.add((owl_entity, rdfs.label, Literal(label, lang=labellang)))
			# graph.add((owl_entity, skos.prefLabel, Literal(label, lang=labellang)))

		if 'entityAltLabels' in entity:
			for item in entity['entityAltLabels']['value'].split("|"):
				label = item.split("@")[0]
				labellang = item.split("@")[1]
				graph.add((owl_entity, skos.altLabel, Literal(label, lang=labellang)))

	if 'exact_match' in entity:
		graph.add((owl_entity, skos.exactMatch, URIRef(entity['exact_match']['value'])))

	if 'owl_subPropOf' in entity:
		graph.add((owl_entity, rdfs.subPropertyOf, URIRef(entity['owl_subPropOf']['value'])))

	if 'owl_domain' in entity:
		graph.add((owl_entity, rdfs.domain, URIRef(entity['owl_domain']['value'])))

	if 'owl_range' in entity:
		if 'owl_range_expr' in entity:
			expr = range_expr_header+'<'+entity['owl_entity']['value']+'> rdfs:range '+entity['owl_range_expr']['value']+' .'
			#print(expr)
			graph.parse(data=expr, format='turtle')
		else:
			graph.add((owl_entity, rdfs.range, URIRef(entity['owl_range']['value'])))

	if 'owl_superclass' in entity:
		graph.add((owl_entity, rdfs.range, URIRef(entity['owl_superclass']['value'])))

	if 'close_matches' in entity:
		for close_match in entity['close_matches']['value'].split("|"):
			graph.add((owl_entity, skos.closeMatch, URIRef(close_match)))

	graph.add((owl_entity, lexmeta.wikibaseEntity, URIRef(entity['entity']['value'])))

#create entity relations and property-values derived from wikibase statements
for statement in statements:
	if statement['obj_datatype']['value'] == "http://wikiba.se/ontology#String":
		graph.add((URIRef(statement['lexmeta_owl_subj']['value']), URIRef(statement['lexmeta_owl_prop']['value']), Literal(statement['o']['value'])))
	elif statement['obj_datatype']['value'] == "http://wikiba.se/ontology#WikibaseItem" and 'lexmeta_owl_obj' in statement:
		graph.add((URIRef(statement['lexmeta_owl_subj']['value']), URIRef(statement['lexmeta_owl_prop']['value']), URIRef(statement['lexmeta_owl_obj']['value'])))
	elif statement['obj_datatype']['value'] == "http://wikiba.se/ontology#ExternalId" and statement['edge']['value'] == "https://lexbib.elex.is/entity/P2":
		graph.add((URIRef(statement['lexmeta_owl_subj']['value']), lexmeta.wikibaseEntity, URIRef('http://www.wikidata.org/entity/'+statement['o']['value'])))




graph.serialize(destination="D:/GitHub/LexMeta/lexmeta_interim.ttl", format="turtle")

with open("D:/GitHub/LexMeta/lexmeta.ttl", "w", encoding="utf-8") as file:
	file.write("@base <http://w3id.org/meta-share/lexmeta/> .\n")
	with open("D:/GitHub/LexMeta/lexmeta_interim.ttl", "r", encoding="utf-8") as interimfile:
		interim = interimfile.read().replace("lexmeta: a owl:Ontology", "<http://w3id.org/meta-share/lexmeta/> a owl:Ontology").replace("vann:preferredNamespaceUri lexmeta: ","vann:preferredNamespaceUri <http://w3id.org/meta-share/lexmeta/> ")
	file.write(interim)

print("Lexmeta TTL file updated.")
