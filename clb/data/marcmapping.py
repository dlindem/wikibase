mapping = {
    "151": [{'target': 'cslex', 'value':{'sub': 'a', 'ind1': ' ', 'ind2': ' '}}],
    "751": [{'target': 'enlex', 'value':{'sub': 'a', 'ind1': '0', 'ind2': '7'}}],
    "034": [{'target': 'geo_ew', 'value':{'sub': 'd', 'ind1': ' ', 'ind2': ' '}}, {'target': 'geo_ns', 'value':{'sub': 'f', 'ind1': ' ', 'ind2': ' '}}],
    "080": [{'target': 'udc', 'value':{'sub': 'a', 'ind1': ' ', 'ind2': ' '}}],
    "150": [{'target': 'cslex', 'value':{'sub': 'a', 'ind1': ' ', 'ind2': ' '}}],
    "450": [{'target': 'csaltlex', 'value':{'sub': 'a', 'ind1': ' ', 'ind2': ' '}}],
    "750": [{'target': 'enlex', 'value':{'sub': 'a', 'ind1': '0', 'ind2': '7'}}],
    "550": [{'target': 'broader', 'condition':{'sub':'w', 'value':'g'}, 'value':{'sub': '7', 'ind1': ' ', 'ind2': ' '}},
            {'target': 'narrower', 'condition':{'sub':'w', 'value':'h'}, 'value':{'sub': '7', 'ind1': ' ', 'ind2': ' '}},
            {'target': 'related', 'condition':{'nosub':'w'}, 'value':{'sub': '7', 'ind1': ' ', 'ind2': ' '}}],
    "155": [{'target': 'cslex', 'value':{'sub': 'a', 'ind1': ' ', 'ind2': ' '}}],
    "755": [{'target': 'enlex', 'value':{'sub': 'a', 'ind1': '0', 'ind2': '7'}}]
}

# These are the MARC mapping rules, valid for CLB MARC data.
# dictionary key is the MARC field code ("tag" attribute of controlfield and datafield elements)

# dictionarie value contains a list of actions, each of which contains:
# 'target' (mandatory): can be mapped to wikibase properties, or used to trigger a specially defined process
# 'value' (mandatory): indicates indicator values and subfield code where the value to write can be found
# 'condition' (optional): a dict with either 'sub' or 'nosub' as key:
# 'sub': subfield with code must contain value for action to be valid (e.g. for 550 'narrower term' / 'broader term')
# 'nosub': subfield with code must not exist for action to be valid (e.g. for 550 'related term')
