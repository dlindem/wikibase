import qwbi

newitem = qwbi.wbi.item.new()

newitem.labels.set(language="en", value="verb")

# claims
statements = {'append':[],'replace':[]}

statements['replace'].append(qwbi.ExternalID(value="Q24905", prop_nr="P1"))

lexeme_id = qwbi.itemwrite(newitem, statements, clear=False)
