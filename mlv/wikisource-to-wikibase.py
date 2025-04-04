import json, sys, time
import config
import xwbi

project_name = "Larramendi_1737_Azkoitiko_Sermoia" # token bildumaren fitxategi-izenean erabiltzeko
texttitle = 'Azkoitiko Sermoia' # tokena deskribatzen duen entitatearen deskribapenean erabiltzeko
wikisource_main_ns_pagename= 'Azkoitiko_Sermoia' # URLean erabiltzeko, adib., aingurarekin, https://eu.wikisource.org/wiki/Azkoitiko_Sermoia#1
textitem = 'Q453' # Testua deskribatzen duen entitatea
print("Getting existing text via Sparql...")
# check for existing tokens of this text
query = """select ?token_zbk ?token ?token_forma
where {
 ?token xdp:P28 xwb:"""+textitem+""" ;
        xdp:P147 ?token_forma ;
        xdp:P148 ?token_zbk ;
       
} order by xsd:float(?token_zbk)"""
r = xwbi.wbi_helpers.execute_sparql_query(query, prefix=config.sparql_prefixes)

print(f"\nFound {str(len(r['results']['bindings']))} existing tokens for this text ({textitem})\n")
existing_tokens = {}
for binding in r['results']['bindings']:
	# print(f"{binding['token_zbk']['value']}: {binding['token']['value'].replace(config.entity_ns,'')} {binding['token_forma']['value']}")
	existing_tokens[binding['token_zbk']['value']] = {'qid':binding['token']['value'].replace(config.entity_ns,''),
														   'token':binding['token_forma']['value']}

# input("Press Enter to proceed to write data to wikibase.")

with open(f"data/{project_name}_tokens.json", "r", encoding="utf-8") as jsonfile:
    numbered_tokens = json.load(jsonfile)

split_token = 0
for number in numbered_tokens:
	# print(f"\nWill now process #{number}: {numbered_tokens[number]}")
	if number in existing_tokens:
		if existing_tokens[number]['token'] == numbered_tokens[number]['token']:
			qid = existing_tokens[number]['qid']
			print(f"Token #{number} is already on Wikibase as {qid} with the same form. OK!")
			continue
		elif existing_tokens[number]['token'] in numbered_tokens[number]['token']:
			merged_splits = existing_tokens[number]['token']
			split_count = 0
			while merged_splits != numbered_tokens[number]['token']:
				split_count += 1
				split_index = '.' + str(split_count)
				if number+split_index in existing_tokens:
					merged_splits += existing_tokens[number+split_index]['token']
				if split_count > 9:
					print(f"Error. Tried to build #{number} '{numbered_tokens[number]['token']}' from following split tokens but failed.")
					print("Fix this.")
					sys.exit()
			print(f"Token #{number} has been split on Wikibase, but could be built from the split products with the same form: {merged_splits} - OK!")
			continue
		print(f"Error. Token #{number} '{numbered_tokens[number]['token']}' is already on Wikibase but as '{existing_tokens[number]['token']}' (https://monumenta.wikibase.cloud/entity/{existing_tokens[number]['qid']})")
		input("Fix this.")
		sys.exit()
	else:
		qid = False


	wikiteka_aingura = wikisource_main_ns_pagename+'#'+numbered_tokens[number]['parag']
	statements = [{'prop_nr': 'P5', 'type':'item', 'value': 'Q15'}] # instance of corpus token
	statements.append({'prop_nr': 'P148', 'type': 'string', 'value': str(number)})  # token zenbakia hurrenkeran
	statements.append({'prop_nr': 'P147', 'type':'string', 'value': numbered_tokens[number]['token']}) # jatorrizko forma
	statements.append({'prop_nr': 'P28', 'type': 'item', 'value': textitem}) # honen parte
	statements.append({'prop_nr': 'P177', 'type': 'externalID', 'value': wikiteka_aingura})  # wikisource page url

	xwbi.itemwrite({'qid':qid, 'labels':[{'lang': 'eu', 'value': numbered_tokens[number]['token']}],
								'descriptions': [{'lang': 'eu', 'value': '#'+number+' '+texttitle}],
								'statements': statements}) # write to new Q-item
	time.sleep(0.2)


