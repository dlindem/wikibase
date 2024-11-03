import csv, wdwbi, time

with open ('data/uztaro-merge-wd.csv') as csvfile:
    rows = csv.DictReader(csvfile, delimiter="\t")
    for row in rows:
        print(f"\nWill merge {row}")
        try:
            wdwbi.wbi_helpers.merge_items(from_id=row['source'], to_id=row['destination'], ignore_conflicts="descriptions", login=wdwbi.login_instance)
            print("Success.")
        except:
            print("Failed.")
        time.sleep(0.5)
