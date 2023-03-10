import config_private
import mwclient
import csv, time, json

site = mwclient.Site('qichwa.wikibase.cloud')
def get_token():
	global site

	# kwb login via mwclient
	while True:
		try:
			login = site.login(username=config_private.wb_bot_user, password=config_private.wb_bot_pwd)
			break
		except Exception as ex:
			print('qwb login via mwclient raised error: '+str(ex))
			time.sleep(60)
	# get token
	csrfquery = site.api('query', meta='tokens')
	token = csrfquery['query']['tokens']['csrftoken']
	print("Got fresh CSRF token for Qichwabase.")
	return token
token = get_token()

with open('data/done-sense-descriptions.csv', 'r', encoding="utf-8") as donefile:
    done_csv = donefile.read().split('\n')
    done_items = {}
    for item in done_csv:
        try:
            done_items[item.split('\t')[0]] = item.split('\t')[1]
        except:
            pass
    # print(str(done_items))
    print('\nThere are '+str(len(done_items))+' already uploaded items.')
    time.sleep(2)

with open('data/done-sense-descriptions-it-fr.csv', 'r', encoding="utf-8") as donefile:
    done_csv = donefile.read().split('\n')
    done_descs = {}
    for item in done_csv:
        try:
            done_descs[item.split('\t')[0]] = item.split('\t')[1]
        except:
            pass
    # print(str(done_descs))
    print('\nThere are '+str(len(done_descs))+' already uploaded sense descriptions.\n')
    time.sleep(2)

with open('data/MASTER_french_italian_upload.csv', encoding="utf-8") as csvfile: # source file
    rows = csv.DictReader(csvfile, delimiter="\t")

    for row in rows:

        id = row['ID']
        if id not in done_items:
            continue
        if id in done_descs:
            print('Skipping previously processed item', id)
            continue

        print('\nWill now upload french and italian to',id,done_items[id],'\n',str(row))

        sensedata = {"glosses": {}}

        if len(row['English'].strip())>0:
            sensedata['glosses']['en'] = {"value":row['English'].strip(), "language":"en"}
        if len(row['Deutsch'].strip())>0:
            sensedata['glosses']['de'] = {"value": row['Deutsch'].strip(), "language": "de"}
        if len(row['Español'].strip())>0:
            sensedata['glosses']['es'] = {"value": row['Español'].strip(), "language": "es"}
        if len(row['Italiano'].strip())>0:
            sensedata['glosses']['it'] = {"value": row['Italiano'].strip(), "language": "it"}
        if len(row['Français'].strip())>0:
            sensedata['glosses']['fr'] = {"value": row['Français'].strip(), "language": "fr"}

        print(str(sensedata))

        done = 0
        while done < 1:
            try:
                senseedit = site.post('wbleditsenseelements', token=token, format="json", senseId=done_items[id]+'-S1', bot=1,
                                      data=json.dumps(sensedata))
            except Exception as ex:
                if 'Invalid CSRF token.' in str(ex):
                    print('Wait a sec. Must get a new CSRF token...')
                    token = get_token()
                else:
                    print(str(ex))
                    time.sleep(4)
                    done += 0.2
                continue
            # print(str(sensecreation))
            if senseedit['success'] == 1:
                print('Sense edit success.')
                done = 2
            else:
                print(str(senseedit))
                print('Sense edit failed, will try again...')
                time.sleep(2)
                done += 0.2
        if done != 2:
            input('senseedit failed 5 times.')
            continue

        with open('data/done-sense-descriptions-it-fr.csv', "a", encoding="utf-8") as donefile:
            donefile.write(id + '\t' + done_items[id] + '\n')
        print('Finished writing to ' + done_items[id])
        time.sleep(1)

