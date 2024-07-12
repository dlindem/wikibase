import xwbi

lexeme = xwbi.wbi.lexeme.get(entity_id="L1")

print(lexeme.get_json())