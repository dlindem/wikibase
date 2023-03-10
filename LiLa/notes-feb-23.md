# Notes

## Structure

The file `new_latin_lexemes.json` contains a list of 24,007 items. Here is a sample entry, a verb:

```json
{
    "_lila_id": "86835",
    "wikibase:lemma": "abaestumo",
    "wikibase:lexicalCategory": "Q24905",
    "dct:language": "wd:Q397",
    "P11033": "lemma/86835",
    "P5186": "Q53768605"
  }
```

Here is a noun, with "lemma variants" (see below):

```json
{
    "_lila_id": "86870",
    "wikibase:lemma": "abecedarii",
    "wikibase:lexicalCategory": "Q1084",
    "dct:language": "wd:Q397",
    "P11033": "lemma/86870",
    "P5911": "Q3953983",
    "P5185": "Q1775461",
    "_lemma_variants": [
      "86869",
      "86871"
    ]
  }
```

Most of the time the key defines a property used in the Wikidata scheme and the value the "object" of the triple. There are, however, a couple of properties (starting with `_`) for internal used.

`_lila_id` is just a technical piece of information, that made retrieval easier (without getting it from the LiLa link).

`lemma_variant` is a bit more complicated. We used the property `has_lemma_variant` to connect lemmas that (although different in some morphological trait) could be used interchangeably to lemmatize the same words. 
Basically, they are variants which differ from some morphological trait.

I don't know what Wikidata wants to do with those variants. Sometimes they are very fine-grained. For instance, the word [puella](https://www.wikidata.org/wiki/Lexeme:L282673) (girl) has a very obscure variant (which I have personally never heard!) *pyera* that is registered in [LiLa](http://lila-erc.eu/data/id/lemma/118823). As the two words differ slightly in respect of the inflectional paradigm, they're 2 separated lemmas and thus lemma variants.

What do we do? Do we include all as separate Lexemes in Wikidata? I have seen cases like this even with the first bunch of Lexemes, so I don't really see a problem. However, we might be introducing a few obscure variants in the lot ad maybe it's not so interesting to have *pyera* after all. The problem is that there is basically no way of knowing which variant is interesting without manual revision: it's more than 5,000 itmes...

## Mapping

### General principles

Here is what I did to map the information in this first conversion.

For all new Lexeme we obviously provide:

- the POS
- the label

Nouns and proper nouns also have information on the grammatical gender, which we map to Wikidata.

Most of the Latin Lexemes that are already in Wikidate also have properties from the Whitaker's Words, such as:

- the frequency class from Whitaker (e.g. `Q86850539`); the Lexemes are made instances (`P31`) of the frequency class;
- time period (`P2348`) links to a periodization defined by Whitaker (e.g. [Whitaker's Latin age type: all ages](https://www.wikidata.org/wiki/Q87433822));
- country (P17) is always set to "international" (where it *is* set)
- then there is a bibliography quotation to the Oxford Latin Dictionary (`Q822282`), via "described by source" (`P1343`)
- a few lexemes also have syntactical notes, like "transitive", "dative case" or "deponent" via the property [require grammatical feature](https://www.wikidata.org/wiki/Property:P5713) (`P5713`)

(See for instance [agglomero](https://www.wikidata.org/wiki/Lexeme:L256712)).

We can't give these info, as we don't have frequency classes, bibliographical links to dictionary (except maybe the Lewis and Short, `Q300453`). Neither do we have the type of syntactic features of `P5713`.

What we do have, which could be easily mapped to Wikidata, on the other hand, is the [inflection type](http://lila-erc.eu/ontologies/lila/hasInflectionType). The inflection paradigm could be used to generate the forms. 
A handful of Latin lexemes (36, to be specific, like e.g. [transitus](https://www.wikidata.org/wiki/Lexeme:L38541)) already have some information about the inflection class. We can easily map the rest to 
the right instances of Wikidata [inflection class](https://www.wikidata.org/wiki/Q56633378).

### Python code

Here is the Python code I used to map the POS, gender and inflection class from LiLa to Wikidata.

#### Part of speech

```python
pos_mapping = {
"http://lila-erc.eu/ontologies/lila/adjective": 'Q34698',
'http://lila-erc.eu/ontologies/lila/adverb': 'Q380057',
"http://lila-erc.eu/ontologies/lila/interjection": 'Q83034',
'http://lila-erc.eu/ontologies/lila/noun': 'Q1084',
'http://lila-erc.eu/ontologies/lila/proper_noun': 'Q147276',
"http://lila-erc.eu/ontologies/lila/verb": 'Q24905',
"http://lila-erc.eu/ontologies/lila/coordinating_conjunction": "Q36484",
"http://lila-erc.eu/ontologies/lila/subordinating_conjunction": "Q36484",
"http://lila-erc.eu/ontologies/lila/numeral": "Q63116",
"http://lila-erc.eu/ontologies/lila/adposition": "Q4833830",
"http://lila-erc.eu/ontologies/lila/determiner": "Q576271",
"http://lila-erc.eu/ontologies/lila/pronoun": "Q36224",
"http://lila-erc.eu/ontologies/lila/particle": "Q184943"
}
```

#### Gender

This is the mapping of the LEMLAT codes in LiLa's database:

```python

gender_lemlat_map = {
    'f' : 'Q1775415',
    'm' : 'Q1775461',
    'n' : 'Q499327',
    '*': 'Q100919075',
    '2': 'Q100919075',
    '1': 'Q100919075'
}

```

Feminine, Masculine and Neuter map without any problem The other cases are a bit more complicated. Classes `1`, `2` and `*` (for nouns) describe words where more genders are attested. I used [`Q110222158`](https://www.wikidata.org/wiki/Q100919075) (ambiguous gender) as those words are actually words attested with various gender. [Unstable gender](https://www.wikidata.org/wiki/Q110222158) might also be possible, I guess.

## Inflectional classes

As property, I use:

* `P5911` (Paradigm class): for nouns and other nominals
* `P5186` (Conjugation class): for verbs

We have 36 classes, so the mapping is long: I have a full csv file with it. Our distintion is more fine grained but most of the typical declensions and conjugations have an easy equivalence with Wikidata entities.

There are, however, a few major difficult cases! Contrary to what happens in LiLa, adjectives, invariables, pronouns and others don't have an inflectional class in Wikidata. That is to say: while there is an instance of "Inflectional paradigm" corresponding to the usual grammatical category [first declension](https://www.wikidata.org/wiki/Q3921592) which we can use with `P5911`, there is none for "first class adjective".

Or, in fact, there is one, but it's rather obscure! We could use the Wikidata IDs for the Wikipedia pages listed in the Italian page [Grammatica Latina](https://it.wikipedia.org/wiki/Grammatica_latina). The morphology discussion links to pages that are connected to the Wikidata IDs for the most used inflectional cases. So, for instance the first declension ([prima declinazione](https://it.wikipedia.org/wiki/Grammatica_latina#Prima_declinazione)) provides a link for the same topic in detail, which in turn corresponds to the Wikidata ID used to describe some Latin lexemes via `P5911`.

That means, I think, that we could apply the same logic and make use of:

* first-class adjectives [Q3606519](https://www.wikidata.org/wiki/Q3606519)
* second-class adjectives [Q3606520](https://www.wikidata.org/wiki/Q3606520)
* pronominal [Q3923913](https://www.wikidata.org/wiki/Q3923913)

The problem is that those Wikidata entities don't have much information attached...

### Deponent verbs

Latin deponent verbs are described as such in Wikidata and we would be able to get this information as well. But I am not really sure of the best approch for doing this.

There is an entity labelled [deponent verb](https://www.wikidata.org/wiki/Q262501) in Wikidata. For Latin,so far, only the [P5713](https://www.wikidata.org/wiki/Property:P5713) ('requires grammatical feature') has been used to mark deponent verbs (e.g. [sequor](https://www.wikidata.org/wiki/Lexeme:L284621)).

Other languages (Swedish, Danish, Bokmål Norwegian) make use of the P31 property ('is instace of'). Considering that `P5713` is normally used for syntactic restrictions (e.g. fr. *bien que* requires the subjunctive), I think that the Scandinavian approach is much more correct!

What shall we do?
