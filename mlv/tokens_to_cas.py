import cassis as cass
import xwbi, config

doc_qid = "Q453"
tokenquery = """select ?token ?token_zbk ?token_forma

        where {
          ?token xdp:P5 xwb:Q15 ;
                xdp:P28 xwb:""" + doc_qid + """;
                xdp:P148 ?token_zbk ;
                xdp:P147 ?token_forma .
          
        } group by ?token ?token_zbk ?token_forma 
        order by xsd:float(?token_zbk)"""

bindings = xwbi.wbi_helpers.execute_sparql_query(query=tokenquery, prefix=config.sparql_prefixes)['results']['bindings']
print('Found ' + str(len(bindings)) + ' results to process.\n')
print(bindings)



with open('data/sermoia_cas/TypeSystem.xml', 'rb') as f:
    typesystem = cass.load_typesystem(f)

with open('data/sermoia_cas/larramendi_sermoia.xmi', 'rb') as f:
   cas = cass.load_cas_from_xmi(f, typesystem=typesystem)

with open('data/larramendi_sermoia.txt', 'r') as txtfile:
    text = txtfile.read()

cas2 = cass.Cas(typesystem=typesystem)
cas2.sofa_string = text

Token = typesystem.get_type('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token')

for cas_token in cas.select("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"):
    cas_token_text = cas_token.get_covered_text()
    print(f"CAS >> {cas_token_text} >> begin: {cas_token.begin}, end: {cas_token.end}")
    if len(bindings) == 0:
        print("Finished with wikibase data.")
        cas2_token = Token(begin=cas_token.begin, end=cas_token.end)
        cas2.add(cas2_token)
    else:
        if cas_token_text == bindings[0]['token_forma']['value']:
            token_uri = bindings[0]['token']['value']
            print(f"Hurra: {token_uri}")
            cas2_token = Token(begin=cas_token.begin, end=cas_token.end, id=token_uri)
            cas2.add(cas2_token)


            del bindings[0]

        else:
            print(bindings[0]['token_forma']['value'])
            print("PROBLEM")

cas2.to_xmi('data/sermoia_cas/larramendi_sermoia_wikibase.xmi')
cas2.to_json('data/sermoia_cas/larramendi_sermoia_wikibase.json')






