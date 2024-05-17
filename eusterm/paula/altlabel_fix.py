import sys, os, time, csv, re

sys.path.insert(1, os.path.realpath(os.path.pardir))
os.chdir(os.path.realpath(os.path.pardir))
import euswb


schemeqid = 'Q9547' # Paularena

with open('paula/altlabels.csv', 'r', encoding="utf-8") as csvfile:
    csvrows = csv.DictReader(csvfile, delimiter="\t")

    for row in csvrows:
        print(str(row))
        qid = row['qid']
        aliases = row['labels']
        if aliases:
            euswb.setlabel(qid, "eu", row['labels'], type="alias", set=True)
        else:
            euswb.setlabel(qid, "eu", "", type="alias", set=True)
        time.sleep(1)

