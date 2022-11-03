import gspread
from oauth2client.service_account import ServiceAccountCredentials

def csv2sheet(title=None, csvpath=None):

	scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
			 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

	credentials = ServiceAccountCredentials.from_json_keyfile_name('awesome-sphere-367416-3a07f9137ac1.json', scope)
	gc = gspread.authorize(credentials)

	spreadsheet = gc.create(title)
	spreadsheet.share('david.lindemann.soraluze@gmail.com', perm_type='user', role='writer')
	print('Created and shared google sheet: '+title)
	with open(csvpath, 'r') as file_obj:
		csv_content = file_obj.read()
		gc.import_csv(spreadsheet.id, data=csv_content)
		print('Successfully imported csv into google sheet.')

csv2sheet(title="wp2dict_es_Nutricion", csvpath="output/Nutrici%C3%B3n.es.csv")
