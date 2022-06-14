import qwbi
import csv, time

with open('done-lemma-uploads.csv', 'r', encoding="utf-8") as donefile:
    done_csv = donefile.read().split('\n')
    done_items = {}
    for item in done_csv:
        try:
            done_items[item.split('\t')[0]] = item.split('\t')[1]
        except:
            pass
    # print(str(done_items))
    print('\nThere are '+str(len(done_items))+' already uploaded items.')
    time.sleep(2)

with open('pos-mapping.csv', 'r', encoding="utf-8") as posfile:
    pos_csv = csv.DictReader(posfile, delimiter="\t")
    pos_mapping = {}
    for item in pos_csv:
        pos_mapping[item['literal']] = item['qid']
    # print(str(pos_mapping))
    print('\nThere are '+str(len(pos_mapping))+' POS mappings.')
    time.sleep(2)

with open('lemma-upload.csv', encoding="utf-8") as csvfile: # source file
    rows = csv.DictReader(csvfile, delimiter="\t")

    for row in rows:
        #print(str(row))
        lemma = row['lemma']
        id = row['id']
        if id in done_items:
            continue
        pos = pos_mapping[row['pos']]
        if pos == "Q44": # prevent phonemes from being processed
            continue

        print('Will now upload',id,lemma,pos)

        newlexeme = qwbi.wbi.lexeme.new(lexical_category=pos, language="Q1")

        for lem in lemma.split(";"):
            newlexeme.lemmas.set(language='qu', value=lem.strip())

        # claims
        statements = {'append':[],'replace':[]}

        statements['replace'].append(qwbi.String(value=id, prop_nr="P6"))
        statements['replace'].append(qwbi.Item(value="Q9", prop_nr="P7"))

        lexeme_id = qwbi.itemwrite(newlexeme, statements, clear=False)
        with open('done-lemma-uploads.csv', "a", encoding="utf-8") as donefile:
            donefile.write(id+'\t'+lexeme_id+'\n')
