import iwb, csv, time

with open('data/oocc_jat.csv') as file:
    data = csv.DictReader(file, delimiter="\t")
    for row in data:
        iwb.setqualifier(row['oocc_item'], "P89", row['oocc_st'], "P91", row['jatorrizkoa'], 'externalid')
        time.sleep(0.5)
