import csv, re, time, json, sys, xwbi

pos_wd2mlv = {"Q1084": "Q51",
              "Q24905": "Q52",
              "Q7233569": "Q53",
              "Q12259986": "Q54",
              "Q34698": "Q55",
              "Q83034": "Q56",
              "Q4889706": "Q57",
              "Q12262560": "Q58",
              "Q380057": "Q59",
              "Q63116": "Q60",
              "Q102047": "Q61",
              "Q161873": "Q62",
              "Q1909485": "Q63",
              "Q36224": "Q64"}

mlvdict = {}
with open('data/MLV-lexemak.csv', 'r', encoding='utf-8') as mlvfile: # alphabetical order: lemma
    mlvcsv = csv.DictReader(mlvfile, delimiter=",")
    for row in mlvcsv:
        mlvdict[row['lemma']] = row

with open('data/WD-lexemak.csv', 'r', encoding='utf-8') as wdfile:
    wddict = csv.DictReader(wdfile, delimiter=",")
    # wddict = {}
    # for row in wdcsv:
    #     if row['lemma'] in wddict:
    #             wddict[row['lemma']].append(row)
    #         else:
    #             wddict[row['lemma']] = [row]
    preceding = None
    for wdrow in wddict:
        print('\nNow processing WD:',str(wdrow))
        if wdrow['lemma'] not in mlvdict or wdrow['category'] not in pos_wd2mlv:
            with open('data/wd_not_oeh_lemma.jsonl', 'a', encoding='utf-8') as logfile:
                logfile.write(json.dumps(wdrow) + '\n')
                print(f"Lemma '{wdrow['lemma']}' not on MLV... Skipped.")
                continue
        print(f"Will process matching lemma string '{wdrow['lemma']}'")
        if wdrow['lemma'] != preceding: # new lemma
            if preceding: # write pending info from preceding wd lemma sign group
                xwbi.basque_lexeme_write({'lid':mlv_lid, 'statements': lexemestatements, 'senses': lexemesenses})
                # print(str({'lid':mlv_lid, 'statements': lexemestatements, 'senses': lexemesenses}))
            # reset for new
            preceding = wdrow['lemma']
            mlv_lid = mlvdict[wdrow['lemma']]['mlv_lid']
            lexemestatements = [{'prop_nr':'P1', 'type':'externalid', 'value':wdrow['wd_lid'], 'qualifiers':[{'prop_nr':'P153', 'type':'item', 'value':pos_wd2mlv[wdrow['category']]}]}]
            seen_wd_lid = [wdrow['wd_lid']]
            lexemesenses = []
        else:
            if wdrow['wd_lid'] not in seen_wd_lid:
                seen_wd_lid.append(wdrow['wd_lid'])
                lexemestatements.append({'prop_nr':'P1', 'type':'externalid', 'value':wdrow['wd_lid'], 'qualifiers':[{'prop_nr':'P153', 'type':'item', 'value':pos_wd2mlv[wdrow['category']]}]})
        # write sense info
        lexemesenses.append({'lang':'eu', 'definition':wdrow['definition'], 'statements':[{'prop_nr':'P1', 'type':'externalid', 'value':wdrow['sense'], 'qualifiers':[{'prop_nr':'P153', 'type':'item', 'value':pos_wd2mlv[wdrow['category']]}]}]})








