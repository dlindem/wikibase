import lwbi




print(f"\nWill get list of LCR with no existing P181 value, and assign the earliest distr pub year as P181.")

query = """
select distinct ?period ?periodLabel ?lcr ?lcrLabel  (min(xsd:integer(year(?distdate))) as ?distyear) where {
 ?lcr ldp:P5 lwb:Q4; ldp:P183 ?period .
  filter not exists {?lcr ldp:P181 ?existing_date.}
  ?lcr ldp:P55 ?dist.
  ?dist ldp:P15 ?distdate
  SERVICE wikibase:label { bd:serviceParam wikibase:language "eu,en". }
} group by ?period ?periodLabel  ?lcr ?lcrLabel  ?distyear
order by ?period ?lcr   

 """
print("Waiting for LexBib v3 SPARQL...")
bindings = lwbi.wbi_helpers.execute_sparql_query(query=query, prefix=lwbi.sparql_prefixes)['results']['bindings']
print('Found '+str(len(bindings))+' results to process.\n')
count = 0
for item in bindings:
	lcr = item['lcr']['value'].replace("https://lexbib.elex.is/entity/","")
	minyear = item['distyear']['value']
	timestr = "+" + minyear + "-01-01T00:00:00Z"
	print(timestr)
	lwbi.itemwrite({'qid':lcr,'statements':[{'type':'time', 'precision':9, 'value':timestr, 'prop_nr':'P181'}]})