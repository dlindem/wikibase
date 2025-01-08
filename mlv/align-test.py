from collatex import *
import os


collection = 'emakumeen_alde'
versions = {}
first = None
for file in os.listdir('data/'+collection):
    filename = file.replace(".txt" , "")
    if not first:
        first = filename
    with open('data/'+collection+'/'+file) as txtfile:
        versions[filename] = txtfile.read()


collation = Collation()
for version in versions:
    collation.add_plain_witness(version, versions[version])

alignment_table = collate(collation, near_match=True, segmentation=False, output="tsv")
print(alignment_table)

with open(f'data/alignment_{collection}.csv', 'w') as csvfile:
    csvfile.write(alignment_table)

alignment_html = collate(collation, near_match=True, segmentation=False, output="html", layout="vertical")
with open(f'data/alignment_{collection}.html', 'w') as htmlfile:
    htmlfile.write(alignment_html)



