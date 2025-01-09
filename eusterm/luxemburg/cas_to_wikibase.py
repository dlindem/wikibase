import cassis, sys

with open('data/Luxemburgo3.txt/TypeSystem.xml', 'rb') as f:
    typesystem = cassis.load_typesystem(f)

with open('data/Luxemburgo3.txt/admin.xmi', 'rb') as f:
   cas = cassis.load_cas_from_xmi(f, typesystem=typesystem)

   print(f"Found text with length {len(cas.sofa_string)}.")


sys.exit()
token_index = dict.fromkeys(range(len(cas.sofa_string)), None)

for cas_token in cas.select("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"):
    cas_token_text = cas_token.get_covered_text()
    # print(f"CAS >> {cas_token_text} >> begin: {cas_token.begin}, end: {cas_token.end}, id: {cas_token.id}")
    offset = cas_token.begin
    while offset <= cas_token.end:
        token_index[offset] = cas_token.id
        offset += 1

# print(token_index)

for cas_wikibase_lexeme in cas.select("webanno.custom.WikibaseLexeme"):
    lexeme_begin = cas_wikibase_lexeme.begin
    lexeme_uri = cas_wikibase_lexeme.WikibaseLexeme
    token_uri = token_index[lexeme_begin]
    print(f"Lexeme {lexeme_uri} annotation belongs to {token_uri}. Begin offset is {lexeme_begin}.")


