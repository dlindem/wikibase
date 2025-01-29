import re, os

emaitzak = "izena\tbdb_id\n"

for file in os.listdir('bertsolariak'):
    with open('bertsolariak/'+file) as txtfile:
        txt = txtfile.read()
    bertsolari_loturak = re.findall(r'<h4><a href="https://bdb.bertsozale.eus/web/haitzondo/view/[^"]+" ?>[^<]+</a></h4>', txt)
    for lotura in bertsolari_loturak:
        bertsolari_re = re.search(r'"(https://bdb.bertsozale.eus/web/haitzondo/view/[^"]+)" ?>([^<]+)</a>', lotura)
        emaitzak += f"{bertsolari_re.group(2)}\t{bertsolari_re.group(1)}\n"#

with open('bertsolariak_bdb.csv', 'w') as csvfile:
    csvfile.write(emaitzak)
