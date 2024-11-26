from collatex import *
import json

# from nltk import align

with open('data/axular_armiarma.txt') as file:
    armiarma = file.read().split("\n\n")
with open('data/axular_wikisource.txt') as file:
    wikisource = file.read().split("\n\n")
with open('data/axular_oeh.txt') as file:
    oeh = file.read().split("\n\n")

print("Start.")
for par in range(len(wikisource)):
    collation = Collation()
    collation.add_plain_witness("wikisource", wikisource[par])
    collation.add_plain_witness("oeh", armiarma[par])
    collation.add_plain_witness("armiarma", armiarma[par])

    alignment_table = collate(collation, near_match=True, segmentation=False, output="tsv")
    print(alignment_table)
    # with open('data/alignment.json', 'w') as jsonfile:
    #     json.dump(json.loads(alignment_table), jsonfile, indent=2)

    with open(f'data/alignment_{par}.csv', 'w') as csvfile:
        csvfile.write(alignment_table)

# alignment_html = collate(collation, near_match=True, segmentation=False, output="html2", layout="horizontal")
# with open('data/alignment.html', 'w') as file:
#     file.write(alignment_html)



