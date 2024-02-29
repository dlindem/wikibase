import sys, os, time, csv, re

sys.path.insert(1, os.path.realpath(os.path.pardir))
os.chdir(os.path.realpath(os.path.pardir))
import euswbi, euswb

# load item mappings from file
with open('data/wdmapping.csv') as csvfile:
    mappingcsv = csvfile.read().split('\n')
    itemwd2wb = {}
    itemwb2wd = {}
    for row in mappingcsv:
        mapping = row.split('\t')
        if len(mapping) == 2:
            itemwb2wd[mapping[0]] = mapping[1]
            itemwd2wb[mapping[1]] = mapping[0]

wb_osagaiak = {"abrikotmarmelada": "Q9111",
               "anisesentzia": "Q9112",
               "aranlehorrak,malagakomahaspasak,etaabar": "Q9113",
               "aranpasa": "Q9114",
               "banilla-hauts": "Q9115",
               "benedictine": "Q9116",
               "bizkotxolehor": "Q9117",
               "brotxetakegitekomakil": "Q9118",
               "chanteclairsagar": "Q9119",
               "eskarola": "Q9120",
               "gaztazuri": "Q9121",
               "gelatina-sobre": "Q9122",
               "gelatinarenzaporeberdinekofruta": "Q9123",
               "gula": "Q9124",
               "fideo": "Q9246",
               "haizekruxpeta": "Q9125",
               "hurpattar": "Q9126",
               "kontserbakokardu": "Q9127",
               "kontserbakopiper": "Q9128",
               "kontserbakopiper-mami": "Q9129",
               "kremalodi(esne-gainbikoitz)": "Q9130",
               "lagunentzat": "Q9131",
               "laranjaschweppes": "Q9132",
               "limoischweppes": "Q9133",
               "meloi": "Q9134",
               "meloigozo": "Q9135",
               "mertxika-lehor": "Q9136",
               "molde": "Q9137",
               "ogibeltz": "Q9138",
               "pastel-irinahul": "Q9139",
               "pikulehor": "Q9140",
               "piper": "Q9141",
               "piperberde": "Q9142",
               "pipergorri": "Q9143",
               "pipergorrimorroi": "Q9144",
               "piperminlehor": "Q9145",
               "sagar,mahats,laranja": "Q9146",
               "sukaldekosoka": "Q9147",
               "tartamolde": "Q9148",
               "tipulin": "Q9149",
               "tipulinfresko": "Q9150",
               "txahalgiltzurrun": "Q9151",
               "zartagi": "Q9152"}

with open('pagotxa/pagotxa.csv', 'r', encoding="utf-8") as csvfile:
    csvrows = csv.DictReader(csvfile, delimiter="\t")
    seen_errezetak = {}
    seen_osagaiak = []
    for row in csvrows:
        print(str(row))
        osagai_label = row['label'].strip().lower()

        if row['wikidata'].startswith('Q'):
            wdqid = row['wikidata'].strip()
            # statements.append({'prop_nr': 'P1', 'type': 'externalid', 'value': wdqid})
            wbqid = itemwd2wb[wdqid]
        else:
            wbqid = wb_osagaiak[osagai_label.replace(' ','')]

        if wbqid not in seen_osagaiak:

            aliases = []
            wb_existing_entity = euswbi.wbi.item.get(entity_id=wbqid)
            existing_label = wb_existing_entity.labels.get('eu')
            if existing_label:
                existing_label = str(existing_label).lower()
                if len(existing_label) > 0 and existing_label != osagai_label:
                    aliases.append(existing_label)
            raw_aliases = wb_existing_entity.aliases.get('eu')
            if raw_aliases:
                for alias in raw_aliases:
                    if alias.value.lower() not in aliases:
                        aliases.append(alias.value.lower())
            euswb.setlabel(wbqid, 'eu', osagai_label, type="label")
            if len(aliases) > 0:
                euswb.setlabel(wbqid, 'eu', ('|').join(aliases), type="alias", set=True)
            seen_osagaiak.append(wbqid)

        errezeta = row['errezeta']
        errezeta_id = re.search(r'http://pagotxa.eus/errezeta/([^/]+)', errezeta).group(1)
        label = errezeta_id.replace('-',' ')
        if errezeta_id not in seen_errezetak:
            statements = [{'prop_nr': 'P5', 'type': 'item', 'value': 'Q9153'},
                          {'prop_nr': 'P117', 'type': 'externalid', 'value': errezeta_id}]
            labels = [{'lang': 'eu', 'value': label}]
            errezeta_qid = euswbi.itemwrite({'qid': False, 'statements': statements, 'labels': labels})
            time.sleep(1)
            seen_errezetak[errezeta_id] = errezeta_qid
        else:
            errezeta_qid = seen_errezetak[errezeta_id]
        errezeta_qid = euswbi.itemwrite({'qid': errezeta_qid, 'statements': [{'prop_nr': 'P60', 'type': 'item', 'value': wbqid}]})