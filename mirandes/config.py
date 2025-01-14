import json


# config related to the wikibase to connect to
wikibase_name = "Lhenguabase"
wikibase_url = 'https://lhenguabase.wikibase.cloud'
entity_ns = "https://lhenguabase.wikibase.cloud/entity/"
api_url = 'https://lhenguabase.wikibase.cloud/w/api.php'
sparql_endpoint = 'https://lhenguabase.wikibase.cloud/query/sparql'
sparql_prefixes = """
PREFIX xwb: <https://lhenguabase.wikibase.cloud/entity/>
PREFIX xdp: <https://lhenguabase.wikibase.cloud/prop/direct/>
PREFIX xp: <https://lhenguabase.wikibase.cloud/prop/>
PREFIX xps: <https://lhenguabase.wikibase.cloud/prop/statement/>
PREFIX xpq: <https://lhenguabase.wikibase.cloud/prop/qualifier/>
PREFIX xpr: <https://lhenguabase.wikibase.cloud/prop/reference/>
PREFIX xno: <https://lhenguabase.wikibase.cloud/prop/novalue/>

"""
# label_languages = "eu es en fr".split(" ") # two-letter wiki language codes of those you want to have labels and descriptions (e.g. when importing from Wikidata)
# store_qid_in_extra = True # if set True, Wikibase BibItem Qid will be stored in the Zotero item's EXTRA field (otherwise, set to False)
# store_qid_in_attachment = True # if set True, a URI attachment will be created for the Zotero item, leading to the Wikibase entity
#
# # essential properties, to be defined here manually:
# prop_wikidata_entity = "P1" # externalId-prop for "Wikidata entity"
# prop_zotero_item = "P17" # externalId-prop for linking items to your Zotero group collection. formatter URL will be "https://www.zotero.org/groups/[group_num]/[group_name]/items/$1/item-details"
# prop_zotero_PDF = "P62" # externalId-prop for linking items to its full text PDF stored as Zotero attachment. formatter URL will be "https://www.zotero.org/groups/[group_num]/[group_name]/items/$1/item-details"
# prop_instanceof = "P5" # datatype WikibaseItem, Wikidata P31
# prop_itemtype = "P78" # datatype WikibaseItem, bibliographical item type (used for pointing to the Zotero item type, e.g. 'journal article')
# prop_formatterurl = "P2" # datatype String, Wikidata P1630
# prop_formatterurirdf = "P3" # datatype String, Wikidata P1921
# prop_inverseprop = "P73" # datatype Property, Wikidata P1696
# prop_series_ordinal = "P32" # datatype String, Wikidata P1545, used e.g. in crator statements
# prop_source_literal = "P36" # datatype String, used as qualifier, e.g. in creator statements
# prop_given_name_source_literal = "P38" # datatype String, used as qualifier in creator statements
# prop_family_name_source_literal = "P39" # datatype String, used as qualifier in creator statements
# prop_isbn_10 = "P20" # datatype ExternalId, Wikidata P967. Used for 10-digit-ISBN identifiers. Most conveniently with formatter URL "https://worldcat.org/isbn/$1"
# prop_isbn_13 = "P19" # datatype ExternalId, Wikidata P212. Used for 13-digit-ISBN identifiers. Most conveniently with formatter URL "https://worldcat.org/isbn/$1"
# # essential ontology classes, to be defined here manually:
# class_bibitem = "Q4" # bibliographical records
# class_bibitem_type = "Q6" # bibliographical item type (journal article, book, etc.)
# class_creator_role = "Q7" # creator role properties (e.g. author, translator)
# class_journal = "Q8" # periodicals
# class_language = "Q9" # natural languages
# class_ontology_class = "Q1" # class that groups all ontology classes
# class_organization = "Q10" # organizations (can be creators, publishers,...)
# class_person = "Q5" # natural persons (humans)
# # regex patterns for identifiers found in Zotero EXTRA field (e.g. Worldcat stores OCLC identifiers there; other use cases are PMID, etc.)
# # In this dictionary, keys are the patterns, values are the Wikibase ExternalId properties to map the identifier to.
# identifier_patterns = {
#     r"^OCLC: ([0-9]+)": "P55" # the OCLC property should have as formatter URL: "https://worldcat.org/oclc/$1"
# }
#
#
# # wb_bot_user and wb_bot_pwd are stored in config.private.py
#
# # config related to Zotero:
#
# zotero_group_id = 5165329 # integer not string
# zotero_export_tag = "wikibase-export" # exact form of the Zotero tag you use for marking records to be exported
# zotero_on_wikibase_tag = "on-wikibase" # form of the Zotero tag written to successfully exported items
# # zotero_api_key is stored in config.private.py
#
#
#
# # DO NOT EDIT THE FOLLOWING SECTIONS
# # import mappings
# def load_mapping(mappingname):
#     print(f"Will load mapping: {mappingname}.json")
#     with open(f"bots/mappings/{mappingname}.json", 'r', encoding='utf-8') as jsonfile:
#         return json.load(jsonfile)
# def dump_mapping(mappingjson):
#     print(f"Will dump mapping: {mappingjson['filename']}")
#     with open(f"bots/mappings/{mappingjson['filename']}", 'w', encoding='utf-8') as jsonfile:
#         json.dump(mappingjson, jsonfile, indent=2)

# bot functions for the datatypes greyed out are not implemented
datatypes_mapping = {
    'ExternalId' : 'external-id',
    'WikibaseForm' : 'wikibase-form',
 #   'GeoShape' : 'geo-shape',
    'GlobeCoordinate' : 'globe-coordinate',
    'WikibaseItem' : 'wikibase-item',
    'WikibaseLexeme' : 'wikibase-lexeme',
 #   'Math' : 'math',
    'Monolingualtext' : 'monolingualtext',
 #   'MusicalNotation' : 'musical-notation',
    'WikibaseProperty' : 'wikibase-property',
 #   'Quantity' : 'quantity',
    'WikibaseSense' : 'wikibase-sense',
    'String' : 'string',
 #   'TabularData' : 'tabular-data',
    'Time' : 'time',
    'Url' : 'url'
}

card1props = []