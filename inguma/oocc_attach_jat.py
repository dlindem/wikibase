import iwb, csv, time, re

# PREFIX
# iwb: < https: // wikibase.inguma.eus / entity / >
# PREFIX
# idp: < https: // wikibase.inguma.eus / prop / direct / >
# PREFIX
# ip: < https: // wikibase.inguma.eus / prop / >
# PREFIX
# ips: < https: // wikibase.inguma.eus / prop / statement / >
# PREFIX
# ipq: < https: // wikibase.inguma.eus / prop / qualifier / >
#
# select ?oocc_item ?oocc_st ?oocc_id(
#     group_concat(?lehen_arg) as ?lehen_argi) ?oocc_text ?jatorrizko_argitalpena ?jat_date ?jat_tit
# where
# {
# ?oocc_item
# ip: P89 ?oocc_st.
# ?oocc_st
# ips: P89 ?oocc_id.
# ?oocc_st
# ipq: P75 ?oocc_text.
# bind(replace(?oocc_text, "(.*)(19[0-9][0-9])(.*)", "$2") as ?lehen_arg)
# ?oocc_item
# idp: P10 ?oocc_title.
#
# filter
# not exists
# {?oocc_st
# ipq: P91 ?jatorria.}
#
# ?jatorrizko_argitalpena
# idp: P88 ?oocc_item;
# idp: P19 ?jat_date;
# idp: P10 ?jat_tit.
#
# }
# group
# by ?oocc_item ?oocc_st ?oocc_id ?lehen_argi ?oocc_text ?jatorrizko_argitalpena ?jat_date ?jat_tit
# order
# by
# xsd: integer(?oocc_id)


with open('data/oocc_st.csv') as file:
    data = csv.DictReader(file, delimiter=",")


    errors = []

    for row in data:

        jat_qid = row['jatorrizko_argitalpena'].replace("https://wikibase.inguma.eus/entity/","")
        oocc_st = row['oocc_st'].replace("https://wikibase.inguma.eus/entity/statement/","")
        qidre = re.search(r"statement/(Q\d+)", row['oocc_st'])
        oocc_qid = qidre.group(1)
        try:

            print(f"For {oocc_st} will write this Qid to the P91 quali: {jat_qid}")
            iwb.setqualifier(oocc_qid, "P89", oocc_st, "P91", jat_qid, 'externalid')
            time.sleep(0.5)
        except:
            errors.append(row['oocc_st'])




print(errors)