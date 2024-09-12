import csv, time, re

with open('data/MEIG_oocc.csv') as file:
    data = csv.DictReader(file, delimiter="\t")
    oocc_st = {}
    result = ""
    for row in data:
        # pagesplit = re.search(r'(\d+)\-(\d+)', row['pages'])
        # if pagesplit:
        #     sp = pagesplit.group(1)
        #     ep = pagesplit.group(2)
        result += f"TY  - CHAP\n"
        result += f"TI  - {row['bib_itemLabel']}\n"
        result += f"T2  - Euskal idazlan guztiak\n"
        result += f"A1  - Mitxelena, Koldo\n"
        result += f"A2  - Altuna, Patxi\n"
        result += f"A2  - Lakarra, Joseba\n"
        result += f"A2  - Sarasola, Ibon\n"
        result += f"A2  - Urgell, Blanca\n"
        result += f"DA  - 1988///\n"
        result += f"SP  - {row['sp']}\n"
        result += f"EP  - {row['ep']}\n"
        result += f"PY  - 1988\n"
        result += f"VL  - {row['vol']}\n"
    #    result += f"SV  - 10\n"
        result += f"CY  - Donostia\n"
        result += f'PB  - Erein; Euskal Editoreen Elkartea\n'
     #   result += f"LA  - {row['langLabel']}\n"
        result += f"LA  - eu\n"
        result += f"SN  - 978-84-7568-232-7\n"
        result += f"KW  - wikibase-export\n"
        result += f"KW  - :oocc {row['bib_item']}\n"
        result += f"ER  - {row['wb']}\n\n" if row['wb'] else f"ER  - \n\n"

    with open('data/batchresult.ris', 'w') as file:
        file.write(result)

