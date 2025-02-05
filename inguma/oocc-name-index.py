# PREFIX
# iwb: < https: // wikibase.inguma.eus / entity / >
# PREFIX
# idp: < https: // wikibase.inguma.eus / prop / direct / >
# PREFIX
# ip: < https: // wikibase.inguma.eus / prop / >
# PREFIX
# ips: < https: // wikibase.inguma.eus / prop / statement / >
# PREFIX
# ipq: < https: // wikibase.inguma.eus / prop / qualifier / >
#
# select
# distinct ?oocc_item ?oocc_title ?pages(strafter(?container, "Obras completas ") as ?bolumen)
# where
# {
# ?oocc_item
# ip: P89 ?oocc_st.
#
# ?oocc_item
# idp: P80 ?pages;
# idp: P54 ?container.
# ?oocc_item
# idp: P10 ?oocc_title.
#
# }
# group
# by ?oocc_item ?oocc_title ?pages ?container
# order
# by ?bolumen

import csv, re, json

with open('data/oocc_bolumen_orrialde.csv') as file:
    csvrows = csv.DictReader(file, delimiter="\t")
    index = {}
    for row in csvrows:
        if row['bolumen'] not in index:
            index[row['bolumen']] = []
        startp = int(re.sub(r'\-\d+', "", row['pages']))
        endp = int(re.sub(r'\d+\-', "", row['pages']))
        index[row['bolumen']].append({'startp': startp, 'endp': endp, 'item': row['oocc_item']})

with open('data/oocc_index.json', 'w') as file:
    json.dump(index, file, indent=2)