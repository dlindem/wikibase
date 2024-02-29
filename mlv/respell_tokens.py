import re, time
import urllib.request
import xwbi

loaded_arau = None
ruledict = None
def load_respell_rules(arau=None):
    global loaded_arau
    loaded_arau = arau
    req = urllib.request.urlopen(f"https://monumenta.wikibase.cloud/wiki/Arau:{arau}?action=raw")
    wikitext = req.read().decode()
    ruledict = {}
    for regex_line in re.findall(r'\*[^\n]+', wikitext):
        regex_pair = re.search(r'\*([^,]+),([^\n]+)', regex_line)
        ruledict[regex_pair.group(1)] = regex_pair.group(2)
    print(ruledict)
    input('\nLoaded rule dictionary: '+arau+'. Press Enter.')
    return ruledict

def respell(token=None, arau=None):
    print('Will respell: '+token)
    global loaded_arau
    global ruledict
    if loaded_arau != arau:
        ruledict = load_respell_rules(arau=arau)
    for rule in ruledict:
        interim = re.sub(rf"{rule}", rf"{ruledict[rule]}", token)
        if len(interim) > 0:
            token = interim
    print(' ...to '+token)
    return token

def respell_tokens(docqid=None, arau=None):
    query = """PREFIX xwb: <https://monumenta.wikibase.cloud/entity/>\nPREFIX xdp: <https://monumenta.wikibase.cloud/prop/direct/>\nPREFIX xp: <https://monumenta.wikibase.cloud/prop/>\nPREFIX xps: <https://monumenta.wikibase.cloud/prop/statement/>\nPREFIX xpq: <https://monumenta.wikibase.cloud/prop/qualifier/>\nPREFIX xpr: <https://monumenta.wikibase.cloud/prop/reference/>\nPREFIX xno: <https://monumenta.wikibase.cloud/prop/novalue/>\n
    select ?token ?forma where {
          ?token xdp:P5 xwb:Q15 ;
                xdp:P28 xwb:"""+docqid+""";
                xdp:P147 ?forma.}"""
    print("Waiting for tokens from SPARQL...")
    bindings = \
        xwbi.wbi_helpers.execute_sparql_query(query=query)['results']['bindings']
    print('Found ' + str(len(bindings)) + ' results to process.\n')
    for row in bindings:
        print('\n'+str(row))
        tokenqid = row['token']['value'].replace('https://monumenta.wikibase.cloud/entity/', '')
        tokenform = row['forma']['value']
        respelled_form = respell(token=tokenform, arau=arau)
        xwbi.itemwrite({'qid': tokenqid, 'statements': [{'type':'string', 'prop_nr':'P181', 'value':respelled_form,
                                                        'qualifiers':[{'type':'externalid', 'prop_nr':'P182', 'value': arau}]}]})
        time.sleep(0.6)

respell_tokens(docqid="Q453", arau="Larramendi_1")

