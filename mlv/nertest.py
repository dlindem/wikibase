import spacy

nlp = spacy.load('es_core_news_sm')
nlp.add_pipe("entityLinker", last=True)

with open('data/nertest.txt') as file:
    text = file.read()

doc = nlp(text)

for ent in doc.ents:
    if ent.label_ == "PER":
        print(ent.text, ent.start_char, ent.end_char, ent.label_)

# returns all entities in the whole document
all_linked_entities = doc._.linkedEntities
# iterates over sentences and prints linked entities
for sent in doc.sents:
    sent._.linkedEntities.pretty_print()
