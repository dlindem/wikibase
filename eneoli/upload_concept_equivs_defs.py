import csv, time, sys, json, xwbi

from wikibaseintegrator.wbi_enums import ActionIfExists

language = "eu"
validator_qids = ["Q676"]
pref_row= "preflabel"
alt_row= "altlabel"
def_row = "def"

validator_qualifiers = []
for validator_qid in validator_qids:
    validator_qualifiers.append(xwbi.Item(prop_nr="P64", value=validator_qid))

count = 1
with open('data/new_basque_equivs_defs.csv') as file:
    data = csv.DictReader(file, delimiter="\t")
    for row in data:
        count += 1
        if count <= 11:
            continue
        wb_concept = xwbi.wbi.item.get(entity_id=row["qid"])
        print(f"[csv row {count}] now processing: https://eneoli.wikibase.cloud/entity/{row['qid']}")
        time.sleep(1)

        if row[pref_row] != "":
            wb_concept.claims.add(xwbi.MonolingualText(prop_nr="P57", text=row[pref_row].strip(), language=language, qualifiers=validator_qualifiers), action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
            wb_concept.labels.set(language=language, value=row[pref_row].strip())

        if row[alt_row] != "":
            wb_concept.claims.add(xwbi.MonolingualText(prop_nr="P57", text=row[alt_row].strip(), language=language, qualifiers=validator_qualifiers), action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
            wb_concept.aliases.set(language=language, values=[row[alt_row].strip()])

        if row[def_row] != "":
            wb_concept.descriptions.set(language=language, value=row[def_row].strip())

        wb_concept.write()






# count = 0
# for binding in bindings:
# 	count += 1
# 	concept_changes = False
# 	wb_concept = binding['concept']['value'].replace('https://eneoli.wikibase.cloud/entity/','')
# 	wd_concept = binding['wd']['value']
# 	print(f"\n[{count}] Now processing Wikibase concept {binding['concept']['value']} (Wikidata {wd_concept})...")
# 	existing_equivlangs = binding['existing_equivlangs']['value'].split(' ')
#
# 	# if "zh-hans" in existing_equivlangs:
# 	# 	existing_equivlangs.append("zh")
# 	existing_desclangs = binding['existing_desclangs']['value'].split(' ')
# 	#
# 	# if "zh-hans" in existing_desclangs:
# 	# 	existing_desclangs.append("zh")
#
# 	statements = []
# 	labels = []
# 	wd_labels = json.loads("["+binding['wd_labels']['value']+"]")
# 	wd_labels = sorted(wd_labels, key=itemgetter('lang'))
# 	zh_hans = False
# 	hr = False
#
# 	for wd_label in wd_labels:
# 		warning = "from Wikidata"
# 		macrolang = wd_label['lang'].split("-")[0]
# 		if macrolang in working_wikilangs and macrolang not in existing_equivlangs:
# 			concept_changes = True
#
# 			# if wd_label['lang'] == "zh" and not zh_hans:
# 			# 	zh_hans_label = lc_cn.convert(wd_label['value'])
# 			# 	print(f'Transformed to zh-hans: "{zh_hans_label}"@zh-hans')
# 			# 	wd_label['value'] = zh_hans_label
# 			# 	wd_label['lang'] = 'zh-hans'
# 			# 	zh_hans = True
# 			# elif wd_label['lang'] == "sr" and not hr:
# 			# 	hr_label = cyrtranslit(wd_desc['value'])
# 			# 	print(f"Found Serbian, transformed to '{hr_label} for HR'")
# 			# 	wd_label['value'] = hr_label
# 			# 	wd_label['lang'] = 'hr'
# 			# 	warning = "from Wikidata (Serbian)"
# 			if wd_label['lang'] in wikilangs_to_write:
# 				print(f'Found a new equivalent to draft: "{wd_label['value']}"@{wd_label['lang']}')
# 				statements.append({'type': 'monolingualtext','prop_nr': 'P57', 'value': wd_label['value'], 'lang': wd_label['lang'], 'qualifiers': [{'prop_nr':'P58', 'value': warning, 'type': 'string'}]})
# 				labels.append({'value': wd_label['value'], 'lang': wd_label['lang']})
#
# 	descriptions = []
# 	wd_descs = json.loads("["+binding['wd_descs']['value']+"]")
# 	wd_descs = sorted(wd_descs, key=itemgetter('lang'))
# 	zh_hans = False
# 	hr = False
# 	for wd_desc in wd_descs:
#
# 		macrolang = wd_desc['lang'].split("-")[0]
# 		if macrolang in working_wikilangs and macrolang not in existing_desclangs:
# 			concept_changes = True
#
# 			# if wd_desc['lang'] == "zh" and not zh_hans:
# 			# 	zh_hans = True
# 			# 	zh_hans_desc = lc_cn.convert(wd_desc['value'])
# 			# 	descriptions.append({'value': zh_hans_desc, 'lang': 'zh-hans'})
# 			# 	print(f'Transformed to zh-hans: "{zh_hans_desc}"@zh-hans')
# 			# 	wd_desc['value'] = zh_hans_desc
# 			# 	wd_desc['lang'] = 'zh-hans'
# 			# elif wd_desc['lang'] == "sr" and not hr:
# 			# 	hr_desc = cyrtranslit(wd_desc['value'])
# 			# 	print(f"Found Serbian, transformed to '{hr_desc} for HR'")
# 			# 	wd_desc['value'] = hr_desc
# 			# 	wd_desc['lang'] = 'hr'
# 			# elif wd_desc['lang'] == 'hr':
# 			# 	hr = True
# 			if wd_desc['lang'] in wikilangs_to_write:
# 				print(f'Found a new description to draft: "{wd_desc['value']}"@{wd_desc['lang']}')
# 				descriptions.append({'value': wd_desc['value'], 'lang': wd_desc['lang']})
#
#
# 	if concept_changes:
# 		xwbi.itemwrite({'qid': wb_concept, 'statements': statements, 'labels': labels, 'descriptions': descriptions})
# 		time.sleep(1)
# 	else:
# 		print("Nothing new to write to this concept entry.")
#
#
#
#
