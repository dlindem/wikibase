import requests, time

start = 0

while start < 1100:
    print(f"Getting page with start {start}...")
    r = requests.get(f"https://bdb.bertsozale.eus/web/bilaketa/index?fq[]=jarduera_facet:%22Bertsolaria%22&start={start}")
    with open(f'bertsolariak/{start}-{start+19}-bertsolariak.txt', 'w') as file:
        file.write(r.text)
    start += 20
    time.sleep(1.1)