# Honek md-etatik klaseak eta kontzeptuak erauziko ditu, eta fitxategi batean gorde

import json, os, re

klase_guztiak = {}
kontzeptua_guztiak = {}
fitxategiak = os.listdir('pages')
for mdfile in fitxategiak:
    if not mdfile.endswith('.md'):
        continue
    print(f"\nOrain {mdfile} prozesatuko...")
    with (open('pages/'+mdfile, 'r', encoding="utf-8") as file):
        content = file.read()
        klaseak = re.findall(r'#[a-z]+', content)

        for klasea in set(klaseak):

            klasea_garbi = re.search(r'#(.+)',klasea).group(1)
            if klasea_garbi not in klase_guztiak:
                klase_guztiak[klasea_garbi] = [mdfile]
            else:
                klase_guztiak[klasea_garbi].append(mdfile)

        kontzeptuak = re.findall(r'\[\[[^\]]+\]\]', content)

        for kontzeptua in set(kontzeptuak):
            kontzeptua_garbi = re.search(r'\[\[([^\]]+)',kontzeptua).group(1)
            if kontzeptua_garbi not in kontzeptua_guztiak:
                kontzeptua_guztiak[kontzeptua_garbi] = [mdfile]
            else:
                kontzeptua_guztiak[kontzeptua_garbi].append(mdfile)



# begiratu ea kontzeptua guztiek md fitxategia duten

kontzeptuak_md_gabe = []

for kontzeptua in kontzeptua_guztiak:
    if kontzeptua+'.md' not in fitxategiak:
        print(f"Ez du orrialderik: {kontzeptua}")
        kontzeptuak_md_gabe.append(kontzeptua)

with open('klaseak_kontzeptuak.json', 'w', encoding="utf-8") as jsonfile:
    json.dump({'klaseak':klase_guztiak, 'kontzeptuak':kontzeptua_guztiak, 'kontzeptuak_orrialderik_gabe':kontzeptuak_md_gabe}, jsonfile, indent=2)