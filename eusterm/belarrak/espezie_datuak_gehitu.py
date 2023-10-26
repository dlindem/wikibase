import sys, os, json, csv, time, re

sys.path.insert(1, os.path.realpath(os.path.pardir))
os.chdir(os.path.realpath(os.path.pardir))
# import euswb





prop = {
    "Ordena": "P46",
    "Familia": "P47",
    "Generoa": "P48",
    "Espeziea": "P49"
}

fitxategiak = os.listdir('belarrak/pages')
for mdfile in fitxategiak:
    if not mdfile.endswith('.md'):
        continue
    # print(f"Orain prozesatzen: {mdfile}")
    with (open('belarrak/pages/' + mdfile, 'r', encoding="utf-8") as file):
        content = file.read()
        re_orden = re.search(r'\+ \*\*Ordena\*\*[^\[]*\[\[([^\]]+)\]\]', content)
        if re_orden:
            print(f"{mdfile}: Ordena: {re_orden.group(1)}")