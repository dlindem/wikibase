import requests, sys, re, time, json

with open('aeronautika_links.txt') as f:
    links = f.readlines()

results = []
errors = []
count = 0
for link in links:
    try:
        count += 1
        print(f"\n{count}/{len(links)}. {link}")
        result = {"link": link.strip(), "lemma": link.replace("https://zthiztegia.elhuyar.eus/terminoa/eu/", "").strip(), "eu_sins": [], "multi_sins": {}, "def": None}
        time.sleep(1.5)
        r = requests.get(link)
        page = r.text.replace("\n", "").replace("\r", "").replace("\t", "")
        def_re = re.search(r'<div class="desc"><p>(.+)', page)
        defi = def_re.group(1).split("</p>")[0]
        print(defi)
        defi = re.sub(r'</?a[^>]*>', '', defi)
        print(defi)
        result['def'] = defi


        eu_sin_re = re.findall(r'<dd class="synonyms -eu">sin\.(.+)', page)
        if eu_sin_re:
            for eu_sin in eu_sin_re:
                eu_sin = eu_sin.split("</dd>")[0]
                print(eu_sin)
                eu_sin = re.search(r'>([^<]+)</a>', eu_sin).group(1)
                print(eu_sin)
                result['eu_sins'].append(eu_sin)


        multi_sins = page.split('<li class="synonyms')
        multi_sins.pop(0)
        for multi_sin in multi_sins:

            lang = re.search(r'^[^\w]*(\w+)[^\w]', multi_sin).group(1)
            sin = re.search(r'>([^<]+)</a>', multi_sin).group(1)
            print(lang, sin)
            if lang not in result['multi_sins']:
                result['multi_sins'][lang] = [sin]
            else:
                result['multi_sins'][lang].append(sin)

        print(result)
        results.append(result)
    except:
        errors.append(link)
        continue

with open('aeronautika_dic.json', 'w') as f:
    json.dump(results, f)
with open('errors.json', 'w') as f:
    json.dump(errors, f)
