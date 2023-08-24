lwb_prefixes = """
PREFIX lwb: <https://lexbib.elex.is/entity/>
PREFIX ldp: <https://lexbib.elex.is/prop/direct/>
PREFIX lp: <https://lexbib.elex.is/prop/>
PREFIX lps: <https://lexbib.elex.is/prop/statement/>
PREFIX lpq: <https://lexbib.elex.is/prop/qualifier/>
PREFIX lpr: <https://lexbib.elex.is/prop/reference/>
PREFIX lno: <https://lexbib.elex.is/prop/novalue/>
PREFIX wikibase: <http://wikiba.se/ontology#>

"""

entity_ns = "https://lexbib.elex.is/entity/"
inverse_prop_relation = "P94" # prop datatype property for declaring inverse properties
wd_sitelinks_prop = "P184" # prop datatype URL for WD-to-WP links, e.g. imported from WD sitelinks

creator_roles = {
	'author': 'P12',
	'editor': 'P13',
	'translator': 'P182'
}

props_wd_wb = {
	'P236': 'P20',
	'P856': 'P44'
}

# Properties with cardinality constraint: max. 1 value
card1props = [
#"P1",
"P2",
"P3",
"P6",
"P8",
"P9",
"P10",
"P11",
"P15",
"P16",
"P17",
"P22",
"P23",
"P24",
"P29",
"P30",
"P32",
"P36",
"P38",
"P40",
"P41",
"P42",
"P43",
"P52",
"P53",
"P54",
"P64",
"P65",
"P66",
"P68",
"P69",
"P70",
"P71",
#"P80",
"P84",
"P85",
"P87",
"P92",
"P93",
"P97",
"P100",
"P101",
"P102",
"P105", # abstract language
"P109",
"P117",
"P128",
"P129",
"P166",
"P167"
]

