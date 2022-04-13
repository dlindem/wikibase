import json


groupname = "productions"
key = "writerName"

print('\nWill count values of key "'+key+'" in group "'+groupname+'":')
with open('D:/Inguma/content/'+groupname+'.json', 'r') as jsonfile:
	group = json.load(jsonfile)

	values = {}
	for entry in group:
		#print(entry)
		if group[entry][key] not in values:
			values[group[entry][key]] = 1
		else:
			values[group[entry][key]] += 1

print(str(values))

with open('D:/Inguma/'+groupname+'_'+key+'_values.json', 'w') as jsonfile:
	json.dump(values, jsonfile, indent=2)
