import csv, os, json

fullTextFolder = 'D:/Inguma/fulltexts'

present_files = os.listdir(fullTextFolder)

# load bibitems list
merged_text = ""
success_count = 0
with open('D:/Inguma/grobid_adibidea/filtered_bibitems.csv', 'r', encoding="utf-8") as csvfile:
	source = csv.DictReader(csvfile)
	for row in source:
		bibitem = row['q_id']
		if bibitem+"_txt.json" not in present_files:
			print(bibitem + ' txt json not found in fulltext folder.')
			continue
		with open (fullTextFolder+'/'+bibitem+"_txt.json", "r", encoding="utf-8") as jsonfile:
			bibitem_json = json.load(jsonfile)
			merged_text += bibitem+'\n'+bibitem_json['body']+"\n\n"
			success_count += 1
with open('D:/Inguma/grobid_adibidea/filtered_bibitems_bodies.txt', 'w', encoding="utf-8") as txtfile:
	txtfile.write(merged_text)
print('\nDone. Merged '+str(success_count)+' text bodies to one txt file.')
