import csv

with open(f'data/alignment_0.csv', 'r') as csvfile:
    csvrows = csv.reader(csvfile, delimiter="\t")

    corpus = {}
    count = 1
    for row in csvrows:

        version_name = row[0]

        tokencount = 1
        while tokencount < len(row):
            if tokencount not in corpus:
                corpus[tokencount] = {}
            corpus[tokencount][version_name] = row[tokencount]
            tokencount += 1

for tokencount in corpus:
    if corpus[tokencount]['wikisource'] == corpus[tokencount]['oeh'] and corpus[tokencount]['wikisource'] == corpus[tokencount]['armiarma']:
        continue
    print(f"{corpus[tokencount]['wikisource']} > {corpus[tokencount]['oeh']} > {corpus[tokencount]['armiarma']}")


