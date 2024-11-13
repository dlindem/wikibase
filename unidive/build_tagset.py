import csv, json, datetime

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
    result['tags'].append({'tag_name': sense['label'], 'tag_description': sense['sense']})

with open('senses_tagset.json', 'w') as file:
    json.dump(result, file, indent=2)

