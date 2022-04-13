import requests, json, time
import config_private

mappings = {
"persons":
{
	"classqid": "Q5",
	"classdesc": "Pertsona bat",
	"id": "extra:",
	"name": "str:P6",
	"surname": "str:P8",
	"secondSurname": "extra:", # extra
	"cleanName": "ext:P3",
	"oRCIDCode": "ext:P39",
	"generoa": "item:gender"
},
"item:gender":
{
	"emakumezkoa": "P50_Q31",
	"gizonezkoa": "P50_Q32",
	"beste generoak": "P50_Q33"

},
"productions":
{
	"classqid": "Q8",
	"id": "extra:",
    "title": "mon:eu:P10",
    "cleanTitle": "str:P12",
    "type": "item:ingumaProdType",
    "year": "extra:",
    "shu": "item:UDC",
    "url": "url:P24",
    "organizationId": "", # this is done in get_orgs
    "issue": "str:P26",
    "firstPage": "str:P27",
    "lastPage": "str:P28",
    "bookTitle": "str:P54",
    "writerName": "extra:", # FEHLT
    "isbn": "extra:", # extra
    "doi": "extra:" # extra
},
"organizations":
{
	#"classqid": "Q6", # instance-of statement is done using "type"
	"id": "extra:",
    "name": "str:P56",
    "type": "item:ingumaOrgType",
    "address": "extra:",
    "web": "url:P41",
    "issn": "extra:",
    "cleanName": "str:P11",
},
"knowledge-areas":
{
	"classqid":"Q11",
	"id": "extra:",
	"knowledgeArea": "" # add_labels will use this
},
"item:ingumaProdType": # Inguma records of type value "None" here are (for the moment) ignored
{
	'phd': "P58_Q13",
	'article': "P58_Q9",
	'course': None,
	'introduction': None,
	'book': "P58_Q10",
	'translation': None,
	'conference': None,
	'subject': None,
	'research': None
},
"item:ingumaOrgType": # this is translated to class Q6 (org) or class Q7 (journal)
{
"magazine": "P5_Q7",
"publisher": "P5_Q6",
"other": "P5_Q6",
"university": "P5_Q6"
},
"item:UDC":
{
	"0": "P53_Q6535",
	"01": "P53_Q6536",
	"02": "P53_Q6537",
	"03": "P53_Q6538",
	"05": "P53_Q6539",
	"06": "P53_Q6540",
	"07": "P53_Q6541",
	"08": "P53_Q6542",
	"09": "P53_Q6543",
	"1": "P53_Q6544",
	"11": "P53_Q6545",
	"13": "P53_Q6546",
	"14": "P53_Q6547",
	"15": "P53_Q6548",
	"16": "P53_Q6549",
	"17": "P53_Q6550",
	"2": "P53_Q6551",
	"3": "P53_Q6552",
	"30": "P53_Q6553",
	"31": "P53_Q6554",
	"32": "P53_Q6555",
	"33": "P53_Q6556",
	"34": "P53_Q6557",
	"35": "P53_Q6558",
	"36": "P53_Q6559",
	"37": "P53_Q6560",
	"39": "P53_Q6561",
	"4": "P53_Q6562",
	"41": "P53_Q6563",
	"42": "P53_Q6564",
	"43": "P53_Q6565",
	"44": "P53_Q6566",
	"5": "P53_Q6567",
	"51": "P53_Q6568",
	"52": "P53_Q6569",
	"53": "P53_Q6570",
	"54": "P53_Q6571",
	"55": "P53_Q6572",
	"56": "P53_Q6573",
	"57": "P53_Q6574",
	"58": "P53_Q6575",
	"59": "P53_Q6576",
	"6": "P53_Q6577",
	"61": "P53_Q6578",
	"62": "P53_Q6579",
	"63": "P53_Q6580",
	"64": "P53_Q6581",
	"65": "P53_Q6582",
	"66": "P53_Q6583",
	"67": "P53_Q6584",
	"68": "P53_Q6585",
	"69": "P53_Q6586",
	"7": "P53_Q6587",
	"71": "P53_Q6588",
	"72": "P53_Q6589",
	"73": "P53_Q6590",
	"74": "P53_Q6591",
	"75": "P53_Q6592",
	"76": "P53_Q6593",
	"77": "P53_Q6594",
	"78": "P53_Q6595",
	"79": "P53_Q6596",
	"8": "P53_Q6597",
	"81": "P53_Q6598",
	"82": "P53_Q6599",
	"9": "P53_Q6600",
	"90": "P53_Q6601",
	"91": "P53_Q6602",
	"92": "P53_Q6603",
	"93": "P53_Q6604"
}
}

def get_production_authors(prod_id):
	r = ""
	while '200' not in str(r):
		print('Now downloading author info for production '+str(prod_id))
		r = requests.get('https://www.inguma.eus/rest/production-persons?search={"productionId":'+str(prod_id)+'}', auth=requests.auth.HTTPBasicAuth(config_private.inguma_api_user,config_private.inguma_api_pwd))
		#print(str(r))

		#print(r.json())
		#time.sleep(1)
		authors = {}
		try:
			print('Number of authors: '+str(len(r.json())))
			for index in range(len(r.json())):
				authors[str(index+1)] = str(r.json()[index]['personId'])
			return authors
		except:
			if '204'in str(r):
				print('Response "No content".')
				return {}
			print('Error downloading authors. Will retry in 2 sec...')
			time.sleep(2)

def get_production_knowlareas(prod_id):
	r = ""
	while '200' not in str(r):
		print('Now downloading knowledge area info for production '+str(prod_id))
		r = requests.get('https://www.inguma.eus/rest/knowledge-area-productions?search={"productionId":'+str(prod_id)+'}', auth=requests.auth.HTTPBasicAuth(config_private.inguma_api_user,config_private.inguma_api_pwd))
		#print(str(r))

		#print(r.json())
		#time.sleep(1)
		areas = []
		try:
			print('Number of knowledge areas: '+str(len(r.json())))
			for index in r.json():
				areas.append(index['knowledgeAreaId'])
			return areas
		except:
			if '204'in str(r):
				print('Response "No content".')
				return []
			print('Error downloading areas. Will retry in 2 sec...')
			time.sleep(2)

def get_ingumagroup(groupname):
	result = {}
	page = 0
	r = ""
	while page == 0 or len(r.json()) == 250:
		page += 1

		r = ""
		while '200' not in str(r):
			print('Now downloading slice '+str(page)+'...')
			r = requests.get('https://www.inguma.eus/rest/'+groupname+'?limit=250&page='+str(page), auth=requests.auth.HTTPBasicAuth(config_private.inguma_api_user,config_private.inguma_api_pwd))
			# print(str(r))
			print('Length of this slice: '+str(len(r.json())))
			#print(r.json())
			time.sleep(1)
		for entry in r.json():
			result[entry['id']] = entry

	with open('D:/Inguma/content/'+groupname+'.json', 'w') as jsonfile:
		json.dump(result, jsonfile, indent=2)
	return(result)

# result = get_ingumagroup('persons')
# result = get_ingumagroup('productions')
# result = get_ingumagroup('affiliations')
# result = get_ingumagroup('knowledge-areas')
# result = get_ingumagroup('organizations')
