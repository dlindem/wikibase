import sys
import os
import sparql
#sys.path.insert(1, os.path.realpath(os.path.pardir))
import lwb
import config

props_to_check = [
	"P127"
# "P12",
# "P13",
# "P72",
# "P73"
]

for prop in props_to_check:
	print('\n________________________________\nNow processing property '+prop)
	print('Will get redirect item data via SPARQL...\n')
	query = """

	PREFIX lp: <https://lexbib.elex.is/prop/>
	PREFIX lps: <https://lexbib.elex.is/prop/statement/>

	select ?item ?statement ?redir ?target where {

	  ?item lp:"""+prop+""" ?statement .
	  ?statement lps:"""+prop+""" ?redir .
	  ?redir owl:sameAs ?target. }

	"""
	print(query)

	url = "https://lexbib.elex.is/query/sparql"
	sparqlresults = sparql.query(url,query)
	print('\nGot data from LexBib SPARQL.')

	#go through sparqlresults
	rowindex = 0

	for row in sparqlresults:
		rowindex += 1
		item = sparql.unpack_row(row, convert=None, convert_type={})
		print('\nNow processing item ['+str(rowindex)+']...')
		#print(str(item))
		qid = item[0].replace("https://lexbib.elex.is/entity/","")
		statement = item[1].replace("https://lexbib.elex.is/entity/statement/","")
		redir = item[2].replace("https://lexbib.elex.is/entity/","")
		target = item[3].replace("https://lexbib.elex.is/entity/","")
		print('Will update '+qid+' '+prop+': '+redir+ ' > '+target)
		lwb.setclaimvalue(statement, target, "item")
