import requests, re, sys

links = """https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=1
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=96
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=122
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=130
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=162
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=247
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=267
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=282
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=315
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=356
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=362
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=423
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=446
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=479
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=497
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=516
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=570
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=571
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=605
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=631
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=634
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=635
https://www.euskaltzaindia.eus/index.php?option=com_xslt&view=frontpage&layout=lth_list&Itemid=474&search=637"""
entries = ""
for link in links.split("\n"):
    print(link)
    r = requests.get(link)
    page = r.text
    raw_entries = re.findall(r'<a class="list-group-item bullet" href="(https://www.euskaltzaindia.eus/index.php?[^"]+)">([^<]+)</a>', page)
    print(raw_entries)
    for raw_entry in raw_entries:
        entries += raw_entry[0] + "\t" + re.sub(r'[\n\r\t]', '', raw_entry[1]) + "\n"

with open("entries.csv", "w") as file:
    file.write(entries)