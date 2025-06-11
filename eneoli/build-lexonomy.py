import xml.etree.ElementTree as xml
from xml.dom import minidom
import csv, time

mapping = {
           "lemma": "headword",
           "language": "language",
           "POS": "partOfSpeech",
           "collection": "collection",
           "neologism_of_the_week": "eneoli_URL",
           "lex innov process": "lex_innov_type",
           "neologism type": "neologism_type",
           "derived from lexemes": "derived_from_lexeme",
           "gloss": "definition",
           "Wikidata concept": "wikidata_concept",
           "register": "register",
           "usage note": "usage_note"}

root = xml.Element('dictionary')

with open('data/lexonomy_data/datasheet4lexonomy.csv') as file:
    rows = csv.DictReader(file, delimiter="\t")

    for row in rows:
        # time.sleep(0.5)
        print(f"\nNow processing row: {row}")
        entry = xml.Element('entry')
        root.append(entry)

        # children of entry
        for column_name in mapping:
            child = xml.SubElement(entry, mapping[column_name])
            child.text = row[column_name].strip()

        # attestations
        for att_nr in [1, 2, 3]:
            if len(row[f"attestation {att_nr} text"]) > 1:
                att = xml.SubElement(entry, 'attestation')
                text = xml.SubElement(att, 'text')
                text.text = row[f"attestation {att_nr} text"].strip()
                date = xml.SubElement(att, 'date')
                date.text = row[f"attestation {att_nr} year"].strip()
                source = xml.SubElement(att, 'source_URL')
                source.text = row[f"attestation {att_nr} source"].strip()



reparsed = minidom.parseString(xml.tostring(root, 'utf-8')).toprettyxml(indent="\t")
print(str(reparsed))
outfile = 'data/lexonomy_data/dictionary.xml'
with open(outfile, "w", encoding="utf-8") as file:
    file.write(reparsed)
print('\n\nWritten to ' + outfile)
