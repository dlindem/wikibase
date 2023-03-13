
import csv, time, json

with open('data/qichwabase_monosemous.json', 'r', encoding="utf-8") as jsonfile:
    bindings = json.load(jsonfile)['results']['bindings']

languages = ['es', 'en', 'de', 'it', 'fr']

with open('data/monosemous_worksheet.csv', 'w', encoding="utf-8") as csvfile: # source file

    currententry = None
    glosses = {}
    csvfile.write('sense uri\tlemma\tcategory\tspanish\tenglish\tgerman\tfrench\titalian\texample_type\texample_source\texample_text')
    for binding in bindings:
        if binding['sense']['value'] != currententry:
            currententry = binding['sense']['value']
            print('Now processing sense',binding['sense']['value'])
            for lang in languages:
                if lang in glosses:
                    csvfile.write('\t'+glosses[lang])
                else:
                    csvfile.write('\t')
            glosses = {}
            csvfile.write('\n'+binding['sense']['value']+'\t'+binding['lemma']['value']+'\t'+binding['poslabel']['value'])
        glosses[binding['glosslang']['value']] = binding['gloss']['value']

print('Finished.')
