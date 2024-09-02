import csv, time, re, os, sys, json, shutil
# from Levenshtein import ratio
import iwbi

from lexbib.config_private import datafolder

# isbntable="""V	Obras completas V. Historia y geografía de la lengua vasca	978-84-9860-335-4
# VI	Obras completas VI. Fonética Histórica Vasca	978-84-9860-336-1
# VIII	Obras completas VIII. Lexicografía. Historia del léxico. Etimología	978-84-9860-478-8
# IX	Obras completas IX. Onomástica	978-84-9860-479-5
# I	Obras completas I. Lingüística histórica	978-84-9860-331-6
# II	Obras completas II. Lingüística general	978-84-9860-332-3
# III	Obras completas III. Paleohispánica	978-84-9860-333-0
# IV	Obras completas IV. Exposiciones generales sobre lengua vasca. Tipología y parentesco lingüístico	978-84-9860-334-7
# X	Obras completas X. Norma y unificación de la lengua. Historia de la vascología. Presente y futuro de la vascología. Reseña de gramáticas, métodos y diccionarios	978-84-9860-480-1
# XI	Obras completas XI. Textos vascos	978-84-9860-481-8
# XIV	Obras completas XIV. Escritos autobiográficos y literarios. Traducciones. Actualidad política y cultural. Entrevistas. Crítica de cine. Cuestiones históricas y culturales	978-84-9860-484-9
# XII	Obras completas XII. "Textos Arcaicos Vascos". N. Landucho,"Dictionarium Linguae Cantabricae (1562)"	978-84-9860-482-5
# VII	Obras completas VII. Fonética y Fonología, Morfosintaxis, Dialectología	978-84-9860-477-1
# XIII	Obras completas XIII. Historia de la Literatura Vasca, Literatura Vasca del siglo XX	978-84-9860-483-2""".split("\n")
#
# isbns = {}
# for isbnline in isbntable:
#     print(isbnline)
#     isbnsplit = isbnline.split("\t")
#     print(isbnsplit)
#     isbns[isbnsplit[0]] = {'title': isbnsplit[1], 'isbn': isbnsplit[2]}
# print(isbns)
#
# pdffolder = "/media/david/FATdisk/Mitxelena OOCC"
# pdffiles = os.listdir(pdffolder+"/2/") + os.listdir(pdffolder+"/ooccfiles/")
# print(pdffiles)
# pdfs = {}
# for file in pdffiles:
#     pdftexttitle = re.search(r' ?([^@]+)', file).group(1)
#     if pdftexttitle not in pdfs:
#         pdfs[pdftexttitle] = [file]
#     else:
#         pdfs[pdftexttitle].append(file)
# with open('data/ooccpdfs.json', 'w') as jsonfile:
#     json.dump(pdfs, jsonfile, indent=2)

with open('data/oocc_id.csv') as csvfile:
    mapping = csv.DictReader(csvfile, delimiter="\t")
    ids = {}
    for row in mapping:
        ids[row['oocc_id']] = row['oocc_item']

foundcount = 0
results = []
result = ""
with open("data/ooccbib.csv") as csvfile:
    bib = csv.DictReader(csvfile, delimiter="\t")
    count = 0
    for line in bib:
        count += 1
        title = None
        pdfname = ""
        ky = ""
        if len(line['year']) == 4:
            year = line['year']
        # if line['pages'] == "": # not in oocc
        #     continue
        if "v" not in line['oocc']:
            continue
        print(line['oocc'])
        text = line['text']
        target_id = line['oocc'].replace("v","")
        if target_id not in ids:
            continue
        target_item = ids[target_id]
        print(f"{line['number']} Found target item {target_item} for {target_id}")
        if line['review'] == "R":
            print("found R")
            title = re.search(r'^[^,]+,[^,]+', text).group(0)
            print(f"{count} found review {line['number']} {title}")
            ky = ":type review"
        elif '"' in text: # book
            title = re.search(r'"([^"]+)"', text).group(1).strip()
            print(f"{count} found book {line['number']} {title}")
        elif '«' in text: # article
            title = re.search(r'«([^»]+)»', text).group(1).strip()
            print(f"{count} found article {line['number']} {title}")
        else:
            title = re.search(r'^[^\[]+', text).group(1)
            print(f"{count} found book {line['number']} {title}")
        print(text)
        statement = {'type': 'string', 'prop_nr':'P89', 'value':line['number'], 'action':'append',
                      'qualifiers':[{'type': 'string', 'prop_nr': 'P75', 'value': text}]}
        iwbi.itemwrite({'qid':target_item, 'statements':[statement]})


#         # if title:
#         #     distances = []
#         #     for pdftitle in pdfs:
#         #         distances.append((pdftitle, ratio(pdftitle, title)))
#         #     distances.sort(key=lambda x: x[1], reverse=True)
#         #     print(distances[:3])
#         #     if distances[0][1] > 0.8 or (line['review'] == "R" and distances[0][1] > 0.7):
#         #
#         #
#         #         pdfnames = pdfs[distances[0][0]]
#         #         if len(pdfnames) == 1:
#         #             try:
#         #                 shutil.move(pdffolder+"/2/"+pdfnames[0], pdffolder+"/ooccfiles/"+pdfnames[0].strip())
#         #             except:
#         #                 pass
#         #             pdfname = "ooccfiles/"+pdfnames[0].strip()
#         #
#         #         else:
#         #             pdfname = "@@@"
#         # if line['oocc'] not in isbns:
#         #     continue
#         # foundcount += 1
#         # print(f"found {foundcount} {title}")
#         # results.append({'oocc_number': line['number'],
#         #                 'title': title,
#         #                 'text': text,
#         #                 'pdfname': pdfname,
#         #                 'review': line['review'],
#         #                 'year': year,
#         #                 'oocc': line['oocc'],
#         #                 'pages': line['pages'],
#         #                 'isbn': isbns[line['oocc']]
#         #                 })
#         # pagesplit = re.search(r'(\d+)\-(\d+)', line['pages'])
#         # if pagesplit:
#         #     sp = pagesplit.group(1)
#         #     ep = pagesplit.group(2)
#         # else:
#         #     if line['pages'] != "":
#         #         sp = line['pages']
#         #         ep = ""
#         #     else:
#         #         sp = ""
#         #         ep = ""
#
#         result += f"TY  - CHAP\n"
#         result += f"TI  - {title}\n"
#         result += f"AU  - Mitxelena Elissalt, Koldo\n"
#         result += f"T2  - {isbns[line['oocc']]['title']}\n"
#         result += f"A2  - Lakarra Andrinua, Joseba Andoni\n"
#         result += f"A2  - Ruiz Arzalluz, Iñigo\n"
#         result += f"DA  - 2011///\n"
#         result += f"PY  - 2011\n"
#         result += f"LA  - es\n"
#         result += f"SP  - {sp}\n"
#         result += f"EP  - {ep}\n"
#         result += f"CY  - Bilbao\n"
#         result += f"PB  - Euskal Herriko Unibertsitateko Argitalpen Zerbitzua\n"
#         result += f"L1  - {pdfname}\n"
#         result += f"SN  - {isbns[line['oocc']]['isbn']}\n"
#         result += f"KW  - {ky}\n"
#         result += f"N1  - <p>OOCC #{line['number']}</p><p>{text}</p><p>{line['oocc']} {line['pages']}</p>\n"
#         result += f"ER  - OOCC #{line['number']}\n\n"
#
# with open('data/ooccresult.json', 'w') as jsonfile:
#     json.dump(results, jsonfile, indent=2)
#
# with open('data/ooccresult.ris', 'w') as file:
#     file.write(result)




