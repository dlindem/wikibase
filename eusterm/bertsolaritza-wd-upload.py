from config_private import wb_bot_user, wb_bot_pwd, wd_user, wd_pwd
from wikibaseintegrator import wbi_login, WikibaseIntegrator
from wikibaseintegrator.datatypes.string import String
from wikibaseintegrator.datatypes.externalid import ExternalID
from wikibaseintegrator.datatypes.item import Item
from wikibaseintegrator.datatypes.monolingualtext import MonolingualText
from wikibaseintegrator.datatypes.time import Time
from wikibaseintegrator.datatypes.globecoordinate import GlobeCoordinate
from wikibaseintegrator.datatypes.url import URL
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator import wbi_helpers
from wikibaseintegrator.wbi_enums import ActionIfExists, WikibaseSnakType
from wikibaseintegrator.models.claims import Claims

# setup wbi for wikidata as wdi
wbi_config['MEDIAWIKI_API_URL'] = 'https://www.wikidata.org/w/api.php'
wbi_config['SPARQL_ENDPOINT_URL'] = 'https://www.wikidata.org/sparql'
wbi_config['WIKIBASE_URL'] = 'https://www.wikidata.org'
wbi_config['USER_AGENT'] = "User-Agent: DL2204bot (https://github.com/dlindem/wikibase;david.lindemann@ehu.eus) wikibaseintegrator/0.12.6"
wbi_config['MAXLAG'] = 0


login_instance = wbi_login.Login(user=wd_user, password=wd_pwd)
wbi = WikibaseIntegrator(login=login_instance)

import csv, time, sys

with open('bertsolaritza/gral_wikidatara_labels_descs.csv') as file:
    rows = csv.DictReader(file, delimiter="\t")
    count = 0
    for row in rows:
        count += 1
        print(f"[{count}] Now processing row {row}")
        if row['wikidata'].startswith("Q"):
            wditem = wbi.item.get(wd_item_id=row['wikidata'])
        else:
            wditem = wbi.item.new()
        wditem.claims.add(Item(prop_nr="P361", value="Q136611356")) # part of bertsolaritza terminology
        for lang in ["eu", "en", "es", "fr"]:
            if row[lang+"Label"] != "":
                wditem.labels.set(language=lang, value=row[lang+"Label"])
            if row[lang+"AltLabels"] != "":
                wditem.aliases.set(language=lang, values=row[lang+"altLabels"].split("|"))
            if row[lang+"Def"] != "":
                wditem.descriptions.set(language=lang, values=row[lang+"Desc"])
        wditem.write()
        with open('bertsolaritza/terms_wb_wd.csv', 'a') as outfile:
            outfile.write(f"{row['concept']}\t{wditem.id}\n")
        print(f"Successfully written to https://www.wikidata.org/wiki/{wditem.id}")
        time.sleep(5)
        sys.exit()








