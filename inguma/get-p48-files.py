import csv
from os import listdir
from datetime import datetime
from urllib.request import urlopen

done_downloads = listdir('D:/Inguma/fulltexts')
#print(str(done_downloads))
failed_downloads = []
with open('D:/Inguma/failed_fulltext_downloads.csv','r',encoding="utf-8") as errorlog:
	failed = csv.DictReader(errorlog, delimiter="\t")
	for fail in failed:
		failed_downloads.append(fail['wikibase_item'].replace('https://wikibase.inguma.eus/entity/','')+".pdf")

with open('D:/Inguma/p48_items_artikuluak.csv', 'r', encoding="utf-8") as csvfile:
	downloads = csv.DictReader(csvfile, delimiter=",")
	count = 0
	for download in downloads:
		count += 1
		durl = download['download']
		items = download['items'].split('|')
		print('\n['+str(count)+'] Now processing: ',durl,str(items))
		if len(items) == 1 and durl.endswith(".pdf"):
			savename = items[0].replace('https://wikibase.inguma.eus/entity/','')+".pdf"
			save_as = "D:/Inguma/fulltexts/"+savename
			if savename in done_downloads:
				print('This download is already done. Skipped.')
				continue
			if savename in failed_downloads:
				print('This download has failed in a previous run. Skipped.')
				continue
			try:
				# Download from URL
				with urlopen(durl, timeout=20) as file:
					content = file.read()
				# Save to file
				with open(save_as, 'wb') as writefile:
					writefile.write(content)

					print('Successfully read and written.')
			except Exception as x:
				print('Error: ',str(x))
				with open('D:/Inguma/failed_fulltext_downloads.csv','a',encoding="utf-8") as errorlog:
					errorlog.write(str(datetime.now())+'\t'+items[0]+'\t'+durl+'\t'+str(x)+'\n')
