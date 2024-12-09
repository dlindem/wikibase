import json, csv, time, os, re
import xwbi

with open ('data/gasteizko_kaleak.csv') as file:
    csvrows = csv.DictReader(file, delimiter=",")
    kaleak = {}
    for row in csvrows:
        kaleak[row['id']] = {'entity': row['kalea'].replace('https://izendegi.wikibase.cloud/entity/',''), 'izena': row['izena']}
    print(f'Loaded kaleak, {len(kaleak)} items.')
    time.sleep(1)

for dir, x, files in os.walk('data/kaleak'):
    for filename in files:
        count = 0
        with open(dir+'/'+filename, errors="ignore") as file:
            filerows = file.read().split('\n')
            for row in filerows:
                zbk_re = re.search (r'^\d+', row)
                if zbk_re:
                    zbk = zbk_re.group(0)
                    kalea = kaleak[zbk]
                    print(f'{zbk}: Found {kalea}')
                    q_re = re.search(r',(Q\d+),', row)
                    if q_re:
                        qid = q_re.group(1)
                        print(f'Found {qid}')
                        count += 1
                        statements = [{'type': 'externalid', 'prop_nr': 'P6', 'value': qid,
                                       'references': [
                                           {'type': 'string', 'prop_nr': 'P13', 'value': filename},
                                           {'type': 'time', 'prop_nr': 'P12', 'value': 'now', 'precision': 11}
                                       ]}
                                      ]
                        xwbi.itemwrite({'qid': kalea['entity'], 'statements': statements})
                        time.sleep(1)
