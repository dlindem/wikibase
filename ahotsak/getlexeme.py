import json
import awbi

lexeme = awbi.wbi.lexeme.get(entity_id='L2340')
ljson = lexeme.get_json()

print(str(ljson))
