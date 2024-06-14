import json

with open('data/iso-639-1.json') as jsonfile:
    iso1 = json.load(jsonfile)['mapping']
    print(iso1)
with open('data/iso-639-3.json') as jsonfile:
    iso3 = json.load(jsonfile)['mapping']

wikibase_label_languages = [
    "en",
    "fr",
    "eu",
    "de",
    "pt",
    "lt",
    "ro",
    "tr",
    "uk",
    "ru",
    "mk",
    "el",
    "hu",
    "nl",
    "es",
    "it",
    "lv",
    "sq",
    "he",
    "hr",
    "sr",
    "bg"
]

csvtext = "language_name,iso-639-1,iso-639-3,wiki_languagecode,wikibase_item,wikidata_item\n"
for lang in wikibase_label_languages:
    iso3lang = iso1[lang]
    wikilang = iso3[iso3lang]['wikilang']
    langqid = iso3[iso3lang]['wbqid']
    wdqid = iso3[iso3lang]['wdqid']
    enlabel = iso3[iso3lang]['enlabel']
    csvtext += f"{enlabel},{lang},{iso3lang},{wikilang},{langqid},{wdqid}\n"

with open('data/languages_table.csv', 'w') as csvfile:
    csvfile.write(csvtext)


