import qwbi

newlexeme = qwbi.wbi.lexeme.new(lexical_category="Q5", language="Q1")
#newlexeme.lexical_category.set("Q5")

# Lemmas
newlexeme.lemmas.set(language='qu', value='mama')

# claims
statements = {'append':[],'replace':[]}

statements['replace'].append(qwbi.ExternalID(value="L7560", prop_nr="P1"))

lexeme_id = qwbi.itemwrite(newlexeme, statements, clear=False)
