import sys, os, time, csv, re

sys.path.insert(1, os.path.realpath(os.path.pardir))
os.chdir(os.path.realpath(os.path.pardir))
import euswbi

lexlangprops = {'es':'P93', 'en': 'P94', 'fr': 'P109'}
desclangprops = {'eu': 'P13', 'es':'P95', 'en': 'P96'}
schemeqid = 'Q8144'

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

# Leu,pos,alias,Deu,Les,Lfr,Len,wd,source_url,source_title

with open('bertsolaritza/bertsolaritza.csv', 'r', encoding="utf-8") as csvfile:
    csvrows = csv.DictReader(csvfile, delimiter=",")

    for row in csvrows:
        statements = []
        wbqid = False
        if row['wd'].startswith('Q'):
            wdqid = row['wd'].strip()
            statements.append({'prop_nr': 'P1', 'type': 'externalid', 'value': wdqid})
            if wdqid in itemwd2wb:
                wbqid = itemwd2wb[wdqid]

        leu = row['Leu'].strip()
        source_url = row['source_url'].strip()
        if source_url.startswith('http'):
            statements.append({'prop_nr': 'P9', 'type': 'url', 'value': source_url})

        source_title = row['source_title'].strip()
        if len(source_title) > 1:
            statements.append({'prop_nr': 'P11', 'type': 'string', 'value': source_title})

        statements.append({'prop_nr': 'P6', 'type': 'item', 'value': schemeqid})
        statements.append({'prop_nr': 'P8', 'type': 'string', 'value': leu})
        labels = [{'lang': 'eu', 'value': leu}]
        aliases = []
        if len(row['alias']) > 1:
            for alias in row['alias'].split(","):
                aliases.append({'lang':'eu','value':alias.strip()})
                statements.append({'prop_nr': 'P8', 'type': 'string', 'value': alias})
        else:
            aliases.append({'lang':'eu','value':''})
        for lang in lexlangprops:
            langcol = 'L'+lang
            if len(row[langcol]) > 1:
                labels.append({'lang':lang, 'value':row[langcol]})
                statements.append({'prop_nr': lexlangprops[lang], 'type': 'string', 'value': row[langcol]})

        if len(row['pos']) > 1:
            for posqid in row['pos'].split(","):
                statements.append({'prop_nr': 'P110', 'type': 'item', 'value': posqid.strip()})

        if len(row['Deu']) > 1:
            desc = re.sub('\. ?$', '', row['Deu']).strip()
            descriptions = [{'lang': 'eu', 'value': desc}]
            statements.append({'prop_nr': 'P13', 'type': 'string', 'value': desc})
        else:
            descriptions = [{'lang':'eu','value':''}]




        wbqid = euswbi.itemwrite(
            {'qid': wbqid, 'statements': statements, 'labels': labels, 'aliases': aliases, 'descriptions': descriptions})
        time.sleep(1)