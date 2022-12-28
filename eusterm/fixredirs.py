import euswbi, euswb
import time

print('Will get redirect item data via SPARQL...\n')
query = """
SELECT (strafter(str(?item),"https://eusterm.wikibase.cloud/entity/") as ?source_item) ?prop_nr
	   (strafter(str(?statement),"https://eusterm.wikibase.cloud/entity/statement/") as ?statementid)
	   (strafter(str(?target),"https://eusterm.wikibase.cloud/entity/") as ?target_item)
WHERE
{ ?prop rdf:type owl:ObjectProperty . filter (regex (str(?prop), "https://eusterm.wikibase.cloud/prop/P"))
  bind(strafter(str(?prop), "https://eusterm.wikibase.cloud/prop/") as ?prop_nr)
  bind(iri(concat("https://eusterm.wikibase.cloud/prop/statement/",?prop_nr)) as ?stprop)
 ?item ?prop ?statement. ?statement ?stprop ?redir. ?redir owl:sameAs ?target .
}
"""
print(query)
bindings = euswbi.wbi_helpers.execute_sparql_query(query=query, prefix=euswbi.sparql_prefixes)['results']['bindings']
amount = len(bindings)
print('Found '+str(amount)+' redirects to fix.\n')
count = 0
for row in bindings:
	print('\n'+str(amount-count)+' items left:')
	print('Will update '+row['source_item']['value']+' '+row['prop_nr']['value']+' > '+row['target_item']['value'])
	euswb.setclaimvalue(row['statementid']['value'], row['target_item']['value'], "item")
	count += 1
	time.sleep(0.1)
print('\n Finished.')
