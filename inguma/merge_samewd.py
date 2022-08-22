# This merges pairs of Q-items with the same P1 (Wikidata Entity) value to one

import iwbi

print('Querying Wikidata for items with the same P1 value')
query = """select ?wd (group_concat(distinct str(?item);SEPARATOR=">") as ?items) where {
  ?item1 idp:P1 ?wd.
  ?item2 idp:P1 ?wd. filter (?item2 != ?item1)
  BIND (strafter(str(?item1),"https://wikibase.inguma.eus/entity/Q") as ?item)
}
group by ?wd ?items
"""
bindings = iwbi.wbi_helpers.execute_sparql_query(query=query, prefix=iwbi.sparql_prefixes)['results']['bindings']
print('Found '+str(len(bindings))+' pairs to be merged.')
if len(bindings) > 0:
	for binding in bindings:
		qidlist = binding['items']['value'].split('>')
		qidnumlist = [eval(i) for i in qidlist]
		print('\n'+str(qidnumlist))
		toqid = "Q"+str(min(qidnumlist)) # toqid is the older item
		fromqid = "Q"+str(max(qidnumlist)) # fromqid is the newer item
		print('Will merge '+fromqid+' to '+toqid)
		presskey = input('Press any key to proceed.')
		print(iwbi.wbi_helpers.merge_items(from_id=fromqid,to_id=toqid, login=iwbi.login_instance))
