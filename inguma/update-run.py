import inguma_upload as itb

print('________________________________________________________')
print('Will run functions selected (uncommented) in the script.\n')
# This can be run e.g. after merging items in Inguma Wikibase (when inguma database id <> wikibase Qid mapping changes)

# print(itb.update_mapping('persons'))
# print(itb.update_mapping('productions'))
# print(itb.update_mapping('affiliations'))
# print(itb.update_mapping('knowledge-areas'))
# print(itb.update_mapping('organizations'))

print('All selected qidmapping files updated.')

# This can be run e.g. after merging items in Inguma Wikibase (when inguma database id <> wikibase Qid mapping changes)

# print(itb.update_group('affiliations'))
# print(itb.update_group('knowledge-areas'))
# print(itb.update_group('organizations'))
# print(itb.update_group('persons'))
print(itb.update_group('productions'))

print('All selected groups uplodaded.')
