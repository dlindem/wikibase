#  OOCC índice de nombres (Q45164)

import json, iwbi, time

with open('data/oocc_index_map.json', 'r') as file:
    index = json.load(file)

for entry in index:
    print(f"\n{entry}")
    wb_entity = iwbi.wbi.item.new()
    wb_entity.labels.set(language="eu", value=entry['entity'])
    wb_entity.labels.set(language="en", value=entry['entity'])
    wb_entity.labels.set(language="es", value=entry['entity'])
    wb_entity.claims.add(iwbi.Item(value="Q45164", prop_nr="P32", qualifiers=[iwbi.String(value=entry['entity'], prop_nr="P75")]))
    for bibitem in entry['data']:
        refs = ", ".join(entry['data'][bibitem])
        wb_entity.claims.add(iwbi.Item(value=bibitem, prop_nr="P92", qualifiers=[iwbi.String(value=refs, prop_nr="P80")]), action_if_exists=iwbi.ActionIfExists.APPEND_OR_REPLACE)
    wb_entity.write()
    print(f"Written to https://wikibase.inguma.eus/entity/{wb_entity.id}")
    time.sleep(1)

