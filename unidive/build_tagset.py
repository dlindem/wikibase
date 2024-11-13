import csv, json, datetime, re

with open('senses.csv') as file:
    reader = csv.DictReader(file)
    data_list = list(reader)
    senses = sorted(data_list, key=lambda x: x['label'].lower())

    print(senses)

result = {"name": "UniDive Wikibase Senses",
          "description": f"This tagsets contains English lexeme senses from UniDive Wikibase as of {datetime.datetime.now()}.",
          "language": "en",
          "tags": []}

for sense in senses:
    label_re = re.search(r'(.*) (\[L[^\]]+\])', sense['label'])
    label = label_re.group(1)
    sense_id = label_re.group(2)
    if len(label) > 77:
        label = sense['label'][0:77] + '...'
    result['tags'].append({'tag_name': label +' '+ sense_id, 'tag_description': sense['sense']})

with open('senses_tagset.json', 'w') as file:
    json.dump(result, file, indent=2)

