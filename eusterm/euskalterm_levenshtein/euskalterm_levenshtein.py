import csv, json, re
from Levenshtein import distance

with open('other_lang_terms.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter="\t")
    lang_terms = {}
    for row in reader:
        if row['concept'] not in lang_terms:
            lang_terms[row['concept']] = {}
        if not re.search(r'[A-Z\.]', row['term']):
            lang_terms[row['concept']][row['term_st']] = row
with open('basque_terms.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter="\t")
    basque_terms = {}
    for row in reader:
        if row['concept'] in lang_terms and not re.search(r'[A-Z\.]', row['eu_term']):
            basque_terms[row['eu_term_st']] = row


result = {}
hiztegiak = {}

for eu_term_st in basque_terms:
    if basque_terms[eu_term_st]['hizt'] not in hiztegiak:
        hiztegiak[basque_terms[eu_term_st]['hizt']] = {'name': basque_terms[eu_term_st]['hiztegia'], 'all': [], 'es': [], 'en': [], 'fr': []}
    equivalents = {'es': [], 'en': [], 'fr': []}

    eu_term = basque_terms[eu_term_st]['eu_term']
    concept = basque_terms[eu_term_st]['concept']

    for term_st in lang_terms[concept]:
        other_term = lang_terms[concept][term_st]['term']
        other_lang = lang_terms[concept][term_st]['lang']
        dist = distance(eu_term, other_term)

        equivalents[other_lang].append({term_st: other_term, 'distance': dist})
        hiztegiak[basque_terms[eu_term_st]['hizt']]['all'].append(dist)
        hiztegiak[basque_terms[eu_term_st]['hizt']][other_lang].append(dist)

    result[eu_term_st] = basque_terms[eu_term_st]
    result[eu_term_st]['equivalents'] = equivalents

for hiztegi in hiztegiak:
    hiztegiak[hiztegi]['all'] = sum(hiztegiak[hiztegi]['all'])/len(hiztegiak[hiztegi]['all'])
    if len(hiztegiak[hiztegi]['es']) > 0:
        hiztegiak[hiztegi]['es'] = sum(hiztegiak[hiztegi]['es'])/len(hiztegiak[hiztegi]['es'])
    else:
        hiztegiak[hiztegi]['es'] = ""
    if len(hiztegiak[hiztegi]['en']) > 0:
        hiztegiak[hiztegi]['en'] = sum(hiztegiak[hiztegi]['en'])/len(hiztegiak[hiztegi]['en'])
    else:
        hiztegiak[hiztegi]['en'] = ""
    if len(hiztegiak[hiztegi]['fr']) > 0:
        hiztegiak[hiztegi]['fr'] = sum(hiztegiak[hiztegi]['fr'])/len(hiztegiak[hiztegi]['fr'])
    else:
        hiztegiak[hiztegi]['fr'] = ""

with open('euskalterm_levenshtein.json', 'w') as csvfile:
    json.dump(result, csvfile, indent=2)
with open('euskalterm_hiztegiak_levenshtein.json', 'w') as csvfile:
    json.dump(hiztegiak, csvfile, indent=2)

f = csv.writer(open("euskalterm_hiztegiak_levenshtein.csv", "w"))

# Write CSV Header, If you dont need that, remove this line
f.writerow(["hiztegia_id", "hiztegia_name", "distance", "distance_es", "distance_en", "distance_fr"])

for hizt in hiztegiak:
    f.writerow([hizt, hiztegiak[hizt]["name"], str(hiztegiak[hizt]['all']), str(hiztegiak[hizt]['es']), str(hiztegiak[hizt]['en']), str(hiztegiak[hizt]['fr'])])



