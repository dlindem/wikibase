import json

with open('aeronautika_dic.json', 'r') as f:
    data = json.load(f)

table = f'"link"\t"lemma"\t"definition"\t"english"\t"spanish"\t"french"\n'
for item in data:
    for lang in ['en', 'fr', 'es']:
        if lang not in item['multi_sins']:
            item['multi_sins'][lang] = [""]
    table += f"{item['link']}\t{item['lemma']}\t{item['def']}\t{item['multi_sins']['en'][0]}\t{item['multi_sins']['es'][0]}\t{item['multi_sins']['fr'][0]}\n"

with open("aeronautika_table.csv", "w") as file:
    file.write(table)
