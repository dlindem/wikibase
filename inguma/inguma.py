import requests, json, time
import config_private

mappings = {
"persons":
	{
	"id": "str:P49",
	"name": "str:P6",
	"surname": "str:P8",
	"secondSurname": "str:P9",
	"cleanName": "ext:P3",
	"oRCIDCode": "ext:P39",
	"generoa": "item:gender"
},
"item:gender":
	{
	"emakumezkoa": "P50_Q31",
	"gizonezkoa": "P50_Q32",
	"beste generoak": "P50_Q33"
	}
}


def getingumagroup(groupname):
	result = []
	page = -1
	r = ""
	while page == -1 or len(r.json()) == 250:
		page += 1

		r = ""
		while '200' not in str(r):
			print('Now downloading slice '+str(page)+'...')
			r = requests.get('https://www.inguma.eus/rest/'+groupname+'?limit=250&page='+str(page), auth=requests.auth.HTTPBasicAuth(config_private.inguma_api_user,config_private.inguma_api_pwd))
			print(str(r))
			print('Length of this slice: '+str(len(r.json())))
			#print(r.json())
			time.sleep(1)
		result += r.json()

	with open('D:/Inguma/'+groupname+'.json', 'w') as jsonfile:
		json.dump(result, jsonfile, indent=2)
	return(result)

#result = getingumagroup('persons')
