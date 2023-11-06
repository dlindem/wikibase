import euswb
import csv

with open('data/fix_st.csv') as file:
    data = csv.DictReader(file, delimiter=",")
    for row in data:
        print(str(row))
        euswb.setclaimvalue(row['uz_st'], row['uzei_id'].replace("musika", "feminismoa"), "String")