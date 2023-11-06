import re, os, json

errezetak = []

files = os.listdir('data')
for file in files:
    with open(f"data/{file}") as htmlfile:
        content = htmlfile.read().replace('\n','')
        errezeta_blocks = content.split(r'class="rcps-post-title">')
        del errezeta_blocks[0]
        for errezeta_block in errezeta_blocks:
            title_url = re.search(r'^<a href="([^"]+)"[^<]+</a>', errezeta_block).group(1)
            if not title_url.startswith('http'):
                continue
            errezeta = {'title_url': title_url}
            print(title_url)
            osagaiak = []
            osagaiak_re = re.search(r'Osagaiak(.+)',errezeta_block)
            if osagaiak_re:
                osagaiak_block = osagaiak_re.group(1).split('Errezeta')[0]
                osagaiak_sep = re.sub(r'\|+','|', re.sub(r'<[^<]+>', '|', re.sub('</?a[^<]+>','', osagaiak_block))).split('|')
                index = 0
                while index < len(osagaiak_sep):
                    osagai = osagaiak_sep[index]
                    if len(osagai) > 1 and not re.search('<',osagai) and not re.search('&', osagai):
                        osagaiak.append(osagaiak_sep[index])
                    index += 1
            else:
                osagaiak = False
                #for x in re.findall(r'<li>.*</li>', osagaiak_block):
            errezeta['osagaiak'] = osagaiak
            errezetak.append(errezeta)


with open('errezetak.json', 'w') as jsonfile:
    json.dump(errezetak, jsonfile, indent=2)

with open('errezetak.csv', 'w') as csvfile:
    for errezeta in errezetak:
        line = errezeta['title_url']
        if errezeta['osagaiak']:
            for osagai in errezeta['osagaiak']:
                line += f"\t\"{osagai}\""
        line += '\n'
        csvfile.write(line)