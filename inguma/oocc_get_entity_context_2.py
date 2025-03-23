# Query for entity context locations
#

# #title: concepts part of "OOCC índice de nombres", and their OOCC references
# PREFIX iwb: <https://wikibase.inguma.eus/entity/>
# PREFIX idp: <https://wikibase.inguma.eus/prop/direct/>
# PREFIX ip: <https://wikibase.inguma.eus/prop/>
# PREFIX ips: <https://wikibase.inguma.eus/prop/statement/>
# PREFIX ipq: <https://wikibase.inguma.eus/prop/qualifier/>
#
# select ?entity (group_concat (distinct str(?label);SEPARATOR="|") as ?labels) ?aipu ?oocc_item ?oocc_pages ?ref_pages ?pdf
# where {
#   ?entity idp:P32 iwb:Q45164; rdfs:label|skos:altLabel ?label.
#   ?entity ip:P92 ?aipu. ?aipu ips:P92 ?oocc_item; ipq:P80 ?ref_pages.
#   filter not exists {?aipu ipq:P93 ?text.}
#   ?oocc_item ip:P71 [ipq:P72 ?pdf]; idp:P80 ?oocc_pages.
#  } group by ?entity ?labels ?aipu ?oocc_item ?oocc_pages ?ref_pages ?pdf
# limit 1000

import re, csv, sys, time, json

with open('data/oocc_entity_context_missing.json', 'r') as file:
    missing = json.load(file)

import requests, iwb

print("Getting data from Wikibase...")
# r = requests.get("https://wikibase.inguma.eus/query/sparql?format=json&query=%23title%3A%20concepts%20part%20of%20%22OOCC%20%C3%ADndice%20de%20nombres%22%2C%20and%20their%20OOCC%20references%0APREFIX%20iwb%3A%20%3Chttps%3A%2F%2Fwikibase.inguma.eus%2Fentity%2F%3E%0APREFIX%20idp%3A%20%3Chttps%3A%2F%2Fwikibase.inguma.eus%2Fprop%2Fdirect%2F%3E%0APREFIX%20ip%3A%20%3Chttps%3A%2F%2Fwikibase.inguma.eus%2Fprop%2F%3E%0APREFIX%20ips%3A%20%3Chttps%3A%2F%2Fwikibase.inguma.eus%2Fprop%2Fstatement%2F%3E%0APREFIX%20ipq%3A%20%3Chttps%3A%2F%2Fwikibase.inguma.eus%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20%3Fentity%20(group_concat%20(distinct%20str(%3Flabel)%3BSEPARATOR%3D%22%7C%22)%20as%20%3Flabels)%20%3Faipu%20%3Foocc_item%20%3Foocc_pages%20%3Fref_pages%20%3Fpdf%0Awhere%20%7B%0A%20%20%3Fentity%20idp%3AP32%20iwb%3AQ45164%3B%20rdfs%3Alabel%7Cskos%3AaltLabel%20%3Flabel.%0A%20%20%3Fentity%20ip%3AP92%20%3Faipu.%20%3Faipu%20ips%3AP92%20%3Foocc_item%3B%20ipq%3AP80%20%3Fref_pages.%0A%20%20%0A%20%20%3Foocc_item%20ip%3AP71%20%5Bipq%3AP72%20%3Fpdf%5D%3B%20idp%3AP80%20%3Foocc_pages.%0A%20%7D%20group%20by%20%3Fentity%20%3Flabels%20%3Faipu%20%3Foocc_item%20%3Foocc_pages%20%3Fref_pages%20%3Fpdf%20%0Alimit%2020000%20")
r = requests.get("https://wikibase.inguma.eus/query/sparql?format=json&query=%23title%3A%20concepts%20part%20of%20%22OOCC%20%C3%ADndice%20de%20nombres%22%2C%20and%20their%20OOCC%20references%0APREFIX%20iwb%3A%20%3Chttps%3A%2F%2Fwikibase.inguma.eus%2Fentity%2F%3E%0APREFIX%20idp%3A%20%3Chttps%3A%2F%2Fwikibase.inguma.eus%2Fprop%2Fdirect%2F%3E%0APREFIX%20ip%3A%20%3Chttps%3A%2F%2Fwikibase.inguma.eus%2Fprop%2F%3E%0APREFIX%20ips%3A%20%3Chttps%3A%2F%2Fwikibase.inguma.eus%2Fprop%2Fstatement%2F%3E%0APREFIX%20ipq%3A%20%3Chttps%3A%2F%2Fwikibase.inguma.eus%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20%3Fentity%20(group_concat%20(distinct%20str(%3Flabel)%3BSEPARATOR%3D%22%7C%22)%20as%20%3Flabels)%20%3Faipu%20%3Foocc_item%20%3Foocc_pages%20%3Fref_pages%20%3Fpdf%0Awhere%20%7B%0A%20%20%3Fentity%20idp%3AP32%20iwb%3AQ45164%3B%20rdfs%3Alabel%7Cskos%3AaltLabel%20%3Flabel.%0A%20%20%3Fentity%20ip%3AP92%20%3Faipu.%20%3Faipu%20ips%3AP92%20%3Foocc_item%3B%20ipq%3AP80%20%3Fref_pages.%0A%20%20filter%20not%20exists%20%7B%3Faipu%20ipq%3AP93%20%3Ftext.%7D%0A%20%20%3Foocc_item%20ip%3AP71%20%5Bipq%3AP72%20%3Fpdf%5D%3B%20idp%3AP80%20%3Foocc_pages.%0A%20%7D%20group%20by%20%3Fentity%20%3Flabels%20%3Faipu%20%3Foocc_item%20%3Foocc_pages%20%3Fref_pages%20%3Fpdf%20%0Alimit%2020000%20")
bindings = r.json()['results']['bindings']

found = 0
total = 0

result = "claim_id\tentity\tcontext\n"
# with open ('data/oocc_entity_context_refs.csv') as file:
#     csvdata = csv.DictReader(file, delimiter="\t")
seen_item = None
for row in bindings:
    total += 1
    print(f"\n[{total}] {row}")
    # time.sleep(0.1)



    oocc_startp = int(re.search(r'^\d+', row['oocc_pages']['value']).group(0))
    try:
        oocc_endp = int(re.search(r'\-(\d+)$', row['oocc_pages']['value']).group(1))
    except:
        oocc_endp = oocc_startp
    ref_pages = re.findall(r': (\d+)', row['ref_pages']['value'])
    ref_volume = re.search(r'^[VIX]+', row['ref_pages']['value']).group(0)
    if ref_volume != "VI":
        continue
    time.sleep(0.2)

    for ref_page_str in ref_pages:
        ref_page = int(ref_page_str)
        print(f"Will check for context: page {ref_page}")
        if not (oocc_startp <= ref_page and ref_page <= oocc_endp):
            input("This row is not OK: ref pages not in oocc item pages range. ENTER to continue.")
            continue
        pdfpage = ref_page - oocc_startp + 1
        entity_names = row['labels']['value'].split("|")

        path = f"/home/david/Zotero/storage/{row['pdf']['value']}/"
        print(f"Will try to find '{entity_names}' in PDF at {path} (page {ref_page})")

        with open (f"{path}.zotero-ft-cache") as txtfile:
            pages = txtfile.read().split("\n\n")
            # page = pages[oocc_startp - ref_page -1]
            # if oocc_endp > oocc_startp:
            #     page += pages[oocc_startp - ref_page]
            count = oocc_startp - 1
            seen_page = None
            for rawpage in pages:
                count += 1
                if count != ref_page and not re.search(rf'@@{ref_page}', rawpage) and not re.search(rf'@@{ref_page+1}', rawpage): # @@pagenum (FHV)
                    continue
                page = "\n" + re.sub(r'([A-Z0-9]+)\. ', r'\1· ', rawpage)
                page = re.sub(r'(,? \(?[a-z])\. ', r'\1· ', page)
                page = re.sub(r'(,? \(?pp)\. ', r'\1· ', page)
                page = re.sub(r'c([A-Z])', r'\1', page)
                page = re.sub(r'([0-9])d', r'\1', page)
                # print(page)
                # print(str(count))
                # if re.search(rf"\n\x0c?{ref_page}", page) or re.search(rf"{ref_page}\x0c?\n", page):
                contexts = []
                seen_shortnames = []
                for entity_name in entity_names:
                    entity_short = entity_name
                    too_shorts = ["de", "San", "du", "De", "Du"]
                    for too_short in too_shorts:
                        entity_short = re.sub(rf'^{too_short} ', '', entity_short)
                    entity_short = re.sub(r"(^[^ \.]+).*", r"\1", entity_short)
                    if entity_short not in seen_shortnames:
                        seen_shortnames.append(entity_short)
                        label_contexts = re.findall(rf'[\.;\?\d\n]\)?,? ?([^\.;\n]*{entity_short}\.?[^;\.\n]*[;\.\n])', page)
                        contexts += label_contexts
                print(f"Shortnames checked: {seen_shortnames}")
                if len(contexts) == 0:
                    print("No context found.")
                    if row['entity']['value'] not in missing:
                        missing[row['entity']['value']] = row
                    continue
                for context in contexts:

                    print(f"**Context at oocc_page {count}, where it should be: {ref_page}\n{context}")

                    context = context.replace("\n"," ").strip()
                    context = re.sub(r"^\. ?", "", context.replace("· ",". "))
                    context = re.sub(r"  +", " ", context)
                    context = f"[{ref_volume}: {ref_page_str}] " + context[:990]
                    guid = row["aipu"]["value"].replace("https://wikibase.inguma.eus/entity/statement/","")
                    result += f'{guid}\t{entity_name}\t{context}\n'

                    qid = re.search(r'^Q\d+', guid).group(0)

                    if row['entity']['value'] != seen_item:
                        iwb.setqualifier(qid, "P92", guid, "P93", context, "string", replaceall=True)
                        seen_item = row['entity']['value']
                    else:
                        iwb.setqualifier(qid, "P92", guid, "P93", context, "string", replaceall=False)
                    time.sleep(0.25)
                    if seen_page != ref_page:
                        found += 1
                        seen_page = ref_page
        # if not seen_page:
        #     input()
with open('data/oocc_entity_context_texts.csv', 'w') as file:
    file.write(result)
with open('data/oocc_entity_context_missing.json', 'w') as file:
    json.dump(missing, file, indent=2)



           # print(pages)
           #  for page in pages:
           #      if re.search(rf"\n\x0c?{pagenum}", page) or re.search(rf"{pagenum}\x0c?\n", page):
           #          print(page)
           #          for context in re.findall(rf'\. ([^\.\d]+ {name}[^\.]+\.)', page):
           #              print(f"\n***\n{context}")


print(f"Finished. Found {found} in {total}")