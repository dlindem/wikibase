import time
import re
import json
import csv
from collections import OrderedDict
from datetime import datetime
import sys
import os
import sparql
import json
import lwb
import lwbi
import config

query = """select ?prop ?inverse where 
           {?prop ldp:P94 ?inverse.}"""
r = lwbi.wbi_helpers.execute_sparql_query(query, prefix=config.lwb_prefixes)
inverted_props = []
print(f"\nFound {str(len(r['results']['bindings']))} inverse property pairs.\n")
for binding in r['results']['bindings']:
    inverted_props.append([binding['prop']['value'].replace(config.entity_ns,''),binding['inverse']['value'].replace(config.entity_ns,'')])
print(str(inverted_props))

input('\nPress return for starting to write missing inverse relations...\n')

for pair in inverted_props:
    print("Will now process inverted properties ", str(pair))

    print(f'(1) get items with {pair[0]} set; where an inverse {pair[1]} relation is not present, will add that...\n')
    query = config.lwb_prefixes + """
    
    select distinct ?n ?b 
    
    where {
    
     ?n ldp:"""+pair[0]+""" ?b.
     filter not exists { ?b ldp:"""+pair[1]+""" ?n . }
    
      }
    """
    #print(query)

    url = "https://lexbib.elex.is/query/sparql"
    print("Waiting for SPARQL...")
    sparqlresults = sparql.query(url, query)
    print('\nGot item list from LexBib SPARQL.')

    # go through sparqlresults
    rowindex = 0

    for row in sparqlresults:
        rowindex += 1
        item = sparql.unpack_row(row, convert=None, convert_type={})
        print('\nNow processing item [' + str(rowindex) + ']...')
        print(str(item))
        source_uri = item[0].replace(config.entity_ns, "")
        target_uri = item[1].replace(config.entity_ns, "")

        # if redirect_qid != None:  # target-rel points to redirect item
        #     if redirect_qid.startswith("Q"):
        #         print('Updating ' + target_uri + ' redirect with ' + redirect_qid + '...')
        #         targetclaims = lwb.getclaims(source_uri, pair[0])[1]
        #         if pair[0] in targetclaims:
        #             targetstatement = targetclaims[pair[0]][0]['id']
        #             lwb.setclaimvalue(targetstatement, redirect_qid, "item")
        #             print('Updating relation: ' + source_uri + ' "' + str(target_label) + '" (skos:source) "' + str(
        #                 source_label) + '"...')
        #             lwb.updateclaim(redirect_qid, pair[1], source_uri, "item")
        #     else:
        #         print('Strange: for ' + target_uri + ' I got redirect: ' + redirect_qid)
        # else:
        print(f'Inverting relation: {source_uri} {pair[0]} {target_uri} {pair[1]} {source_uri}')
        lwb.updateclaim(target_uri, pair[1], source_uri, "item")

    # print(
    #     '\n\n________________________________________________________\n\n(2) get orphaned source relations (where the target has been removed)...\n')
    # query = config.lwb_prefixes + """
    # 
    # select distinct ?n ?nLabel ?narstatement ?b ?bLabel
    # 
    # where {
    # 
    #   ?n rdfs:label ?nLabel . FILTER (lang(?nLabel)="eu")
    #   ?b lp:"""+pair[1]+""" ?narstatement .
    #   ?narstatement lps:"""+pair[0]+""" ?n .
    #   filter not exists { ?n ldp:"""+pair[0]+""" ?b . }
    # 
    #   ?b rdfs:label ?bLabel . FILTER (lang(?bLabel)="eu")
    # 
    #   }
    # """
    # print(query)
    # 
    # url = "https://lexbib.elex.is/query/sparql"
    # print("Waiting for SPARQL...")
    # sparqlresults = sparql.query(url, query)
    # print('\nGot term list from LexBib SPARQL.')
    # 
    # # go through sparqlresults
    # rowindex = 0
    # 
    # for row in sparqlresults:
    #     rowindex += 1
    #     item = sparql.unpack_row(row, convert=None, convert_type={})
    #     print('\nNow processing item [' + str(rowindex) + ']\n')
    #     source_uri = item[0].replace("http://lexbib.elex.is/entity/", "")
    #     source_label = item[1]
    #     narstatement = item[2].replace("http://lexbib.elex.is/entity/statement/", "")
    #     target_uri = item[3].replace("http://lexbib.elex.is/entity/", "")
    #     target_label = item[4]
    #     print('Removing orphaned source-rel: "' + target_label + '" (skos:source) "' + source_label + '"...')
    #     lwb.removeclaim(narstatement)
