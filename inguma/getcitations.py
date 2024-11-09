import iwbi, time

def get_citations():

    wdns = "http://www.wikidata.org/entity/"
    query = """PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX pr: <http://www.wikidata.org/prop/reference/>
    PREFIX iwb: <https://wikibase.inguma.eus/entity/>
    PREFIX idp: <https://wikibase.inguma.eus/prop/direct/>
    PREFIX ip: <https://wikibase.inguma.eus/prop/>
    PREFIX ips: <https://wikibase.inguma.eus/prop/statement/>
    PREFIX ipq: <https://wikibase.inguma.eus/prop/qualifier/>
        
    select 
    ?aipatzen_duena ?wd_cit_iturri (group_concat(distinct ?wd_cit_xede;SEPARATOR=",") as ?wd_cit_xedeak)
where {
  ?oocc_item ip:P89 ?oocc_st.
  ?oocc_st ips:P89 ?oocc_id.
  ?oocc_st ipq:P75 ?oocc_text.
  ?oocc_item idp:P10 ?oocc_title.
  ?oocc_item idp:P1 ?wd_cit_xede.
  
  ?aipatzen_duena idp:P62 [idp:P88* ?oocc_item].
  ?aipatzen_duena idp:P19 ?data; idp:P37 ?aldizkaria; idp:P17 [rdfs:label ?egileaLabel]. filter(lang(?egileaLabel)="eu")
  ?aipatzen_duena idp:P1 ?wd_cit_iturri. 
  bind(iri(concat(str(wd:),?wd_cit_iturri)) as ?wd_cit_iturri_item)
  bind(iri(concat(str(wd:),?wd_cit_xede)) as ?wd_cit_xede_item)
  filter not exists {
  SERVICE <https://query.wikidata.org/sparql> {
           select ?wd_cit_iturri_item ?wd_cit_xede_item where {?wd_cit_iturri_item wdt:P2860 ?wd_cit_xede_item. } }
  }
 SERVICE wikibase:label { bd:serviceParam wikibase:language "en,eu". }
}  
group by ?aipatzen_duena ?wd_cit_iturri ?wd_cit_xedeak

    """

    bindings = iwbi.wbi_helpers.execute_sparql_query(query=query)['results']['bindings']
    amount = len(bindings)
    print('Found '+str(amount)+' Wikidata entries with citations to write.\n')
    time.sleep(3)
    count = 0
    citations = {}
    for row in bindings:
        count += 1
        iturri = row['wd_cit_iturri']['value']
        xedeak = row['wd_cit_xedeak']['value'].split(",")
        wb_iturri = row['aipatzen_duena']['value']
        print(f"[{count}/{amount}] {wdns}{iturri}: {len(xedeak)} citations to write.")
        citations[iturri] = {'wb_iturri': wb_iturri, 'xedeak':xedeak}
    print("Get citations action completed.")
    time.sleep(3)
    return citations
