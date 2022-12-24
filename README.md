# wikibase
 This repo is for sharing scripts and open content sources we use to populate wikibase instances with data, and to interact with Wikidata. Each folder contains a setup for the [WikibaseIntegrator (WBI)](https://github.com/LeMyst/WikibaseIntegrator) named ?wbi.py, which is used for interaction with a wikibase. If the folder contains also a module named ?wb.py, that is the old self-cooked bot I used before and still deploy sometimes; that sends [single api calls](https://www.mediawiki.org/wiki/API:Main_page) for just every single action using media wiki client [mwclient](https://mwclient.readthedocs.io/en/latest/), is though much slower, and also does not have the nice built-in retry (when getting 502 response, etc.) WBI has.

 Any feedback or contribution to improve the code towards something more generic is warmly welcome (you will find clumsy code, and some things could be done in much smarter ways ;-), I hope it provides at least useful reference to how things can be done).

### CLB-LOD Wikibase (Czech Literary Bibliography MARC data)

 https://clb-lod.wikibase.cloud

### Inguma Wikibase (Basque scientific articles metadata)

https://wikibase.inguma.eus

### Quichwabase (Quechua lexical data)

https://qichwa.wikibase.cloud

### Ahotsak Wikibase (Basque lexical data)

 https://datuak.ahotsak.eus
 
 Older code related to Ahotsak wikibase is found at https://github.com/dlindem/ahotsak-wikibase.

### LexBib Wikibase (Knowledge Graph of the domain of Lexicography and Dictionary Research)

 https://lexbib.elex.is

 Older code related to LexBib wikibase is found at https://github.com/elexis-eu/elexifinder.

### Eusterm Wikibase (Used in a course on Basque Terminology at UPV/EHU)

 https://eusterm.wikibase.cloud

### Kurdish Wikibase (Kurdish lexical data)

 https://kurdish.wikibase.cloud
