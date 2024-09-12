import iwb, csv, time

with open('data/oocc_st.csv') as file:
    data = csv.DictReader(file, delimiter="\t")
    oocc_st = {}
    for row in data:
        oocc_st[row['oocc_id']] = {'qid': row['oocc_item'], 'st': row['oocc_st']}

errors = []
with open('data/mitx_oocc.csv') as file:
    data = csv.DictReader(file, delimiter="\t")
    for row in data:
        if row['oocc'] == "":
            continue
        try:
            target_itemdata = oocc_st[row['oocc']]
            print(f"For {row['oocc']} found {target_itemdata} and will write this Qid to the P89 statement: {row['mitx_item']}")
            iwb.setqualifier(target_itemdata['qid'], "P89", target_itemdata['st'], "P91", row['mitx_item'], 'externalid')
            time.sleep(0.5)
        except:
            errors.append(row['oocc'])




print(errors)