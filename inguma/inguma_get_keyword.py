import re, os

keyword = "Mitxelena"

path = '/media/david/FATdisk/Inguma/ASJU_PDF/tei/'
for filename in os.listdir(path):
    with open(path+filename, 'r', encoding="utf-8") as file:
        filetext = file.read()
    regex = re.search(keyword, filetext)
    if regex:
        print(filename)
        os.system(f"cp {path}{filename} /home/david/Documents/GitHub/wikibase/inguma/data/asju/tei/{filename}")

