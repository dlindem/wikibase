import inguma_upload, inguma

print('________________________________________________________\n')
print('Will run functions selected (uncommented) in the script.\n')
# The following functions can be run e.g. after merging items in Inguma Wikibase (when inguma database id <> wikibase Qid mapping changes)

print(inguma_upload.update_mapping('persons'))
print(inguma_upload.update_mapping('productions'))
# print(inguma_upload.update_mapping('affiliations'))
# print(inguma_upload.update_mapping('knowledge-areas'))
# print(inguma_upload.update_mapping('organizations'))
#
# print('All selected qidmapping files updated.')
#
# # The following functions upload the inguma sql groups
#
#
# print(inguma_upload.update_group('affiliations'))
# print(inguma_upload.update_group('knowledge-areas'))
# print(inguma_upload.update_group('organizations'))
# print(inguma_upload.update_group('persons')) #, rewrite = True))

print(inguma_upload.update_group('productions')) #, rewrite = True))

print('All selected groups uplodaded.')

# # The following only updates the inguma sql local caché, and does not upload
#
# groups_to_get = ['persons', 'affiliations', 'knowledge-areas', 'organizations']
# groups_to_get = ['productions']
# for group in groups_to_get:
# 	content = inguma.get_ingumagroup(group)
# 	if content:
# 		print("Got and saved inguma", group)
