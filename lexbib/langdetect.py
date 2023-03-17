import json, charade, config

with open('D:/LexBib/bodytxt/bodytxt_collection.json', encoding="utf-8") as infile:
	bodytxtcoll = json.load(infile)
	results = {}
	for item in bodytxtcoll:
		bodytxt = bodytxtcoll[item]['bodytxt']
		encoding = charade.detect(bodytxt.encode())
		if encoding['encoding'] != "utf-8":
			print(item,str(encoding))

