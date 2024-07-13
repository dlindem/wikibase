import re, time, iwbi

with open('data/bibliografia_Koldo_Mitxelena_corrected.txt') as file:
    rows = file.read().split("\n")

labur = {
    "ASJU": {'type': 'item', 'prop_nr': 'P37', 'value':'Q13228'},
    "BAP": {'type': 'item', 'prop_nr': 'P37', 'value':'Q13212'},
    "FLV": {'type': 'item', 'prop_nr': 'P37', 'value':'Q13175'}
   # "LH": {'type': 'item', 'prop_nr': 'P32', 'value':'Q40013'}
}

mitxelena = {}

for row in rows:
    print(f"Row: {row}")
    if re.search(r'YEAR_(\d+)', row):
        year = re.search(r'YEAR_(\d+)', row).group(1)
        print(f"\nStart processing year {year}.")
    elif row.startswith("!"):

        bibnum = re.search(r'!(\d+)§', row).group(1)
        if int(bibnum) < 22:
            continue
        bibtext = row.split('§')[1]
        if not bibtext.startswith("%"): # Mitxelena entry
            statements = [
                {'type': 'item', 'prop_nr': 'P5', 'value':'Q8'}, # instance of bibitem
                {'type': 'string', 'prop_nr': 'P70', 'value':bibnum},
                {'type': 'item', 'prop_nr': 'P17', 'value':'Q201'}, # author KM
                {'type': 'time', 'prop_nr': 'P19', 'value':'+'+year+'-01-01T00:00:00Z', 'precision':9} # date
            ]
            for lab in labur:
                if lab in bibtext:
                    statements.append(labur[lab])

            labels = [{'lang': 'eu', 'value': bibtext[:250]}]

            print(f"statements: {statements}")
            print(f"labels: {labels}")
            qid = iwbi.itemwrite({'qid':False, 'statements':statements, 'labels':labels})
            time.sleep(1)


