from bots import xwbi
import sys


# new_concepts = "Q976,Q207,Q1086,Q1091,Q1096,Q1107,Q1112,Q1126,Q1118,Q1124,Q1125,Q1082,Q1080,Q1110,Q1116,Q1093,Q1115,Q1108,Q1092,Q1114,Q1085,Q1119,Q1102,Q1117,Q1100,Q1089,Q1120,Q1113,Q1106,Q1083,Q1121,Q1088,Q1094,Q1084,Q1097,Q1122,Q1111,Q1123,Q1103,Q1090,Q1099,Q1109,Q1105,Q1081,Q1098,Q1095,Q1101,Q1087,Q1104".split(",")
# new_concepts = "Q1127,Q1128,Q1129,Q1130,Q1131,Q1132,Q1133,Q1134,Q1135,Q1136,Q1137,Q1138,Q1139,Q1140,Q1141,Q1142,Q1143,Q1144,Q1145,Q1146,Q1147,Q1148,Q1149,Q1150,Q1151,Q1152,Q1153,Q1154,Q1155,Q1156,Q1157,Q1158,Q1159,Q1160,Q1161,Q1162,Q1163,Q1164,Q1165,Q1166,Q1167,Q1168,Q1169,Q1170,Q1171,Q1172,Q1173,Q1174,Q1175,Q1176,Q1177,Q1178".split(",")
# new_concepts = ["Q976"]
# new_concepts = "Q1283,Q1284,Q1285,Q1286,Q1287,Q1288,Q1289,Q1290,Q1291,Q1292,Q1293,Q1294,Q1295,Q1296,Q1297,Q1298,Q1299,Q1300,Q1301,Q1253,Q1254,Q1255,Q1256,Q1257,Q1258,Q1259,Q1260,Q1261,Q1266,Q1236,Q1237,Q1240,Q1244,Q1245,Q1246,Q1247,Q1248,Q1249,Q1250,Q1269,Q1270,Q1272,Q1273,Q1274,Q1276,Q1278,Q1279".split(",")
new_concepts = "Q1082,Q1080,Q1124,Q1115,Q1116,Q1092,Q1114,Q1085,Q1119,Q1102,Q1269,Q1240,Q1117,Q1100,Q1089,Q1120,Q1091,Q1113,Q1106,Q1245,Q1244,Q1246,Q1121,Q1088,Q1094,Q1261,Q1250,Q1248,Q1249,Q1247,Q1253,Q1254,Q1084,Q1122,Q1118,Q1255,Q1097,Q1257,Q1083,Q1111,Q1259,Q1103,Q976,Q1270,Q1107,Q1123,Q1256,Q1272,Q1258,Q1090,Q1099,Q1109,Q1126,Q1098,Q1278,Q1279,Q1105,Q1237,Q1087,Q1081,Q1101,Q1095,Q1125".split(",")


count = 0
for concept_id in new_concepts:
    print(f"\n Now processing {concept_id}. {len(new_concepts)-count} items left.")
    item = xwbi.wbi.item.get(entity_id=concept_id)
    itemjson = item.get_json()
    print(itemjson)
    statements = []
    all_languages_in_data = ["ca"]
    # for labellang in itemjson['labels']:
    #     all_languages_in_data.append(labellang)
    # for altlabellang in itemjson['aliases']:
    #     if altlabellang not in all_languages_in_data:
    #         all_languages_in_data.append(altlabellang)

    itemlabels = []
    itemaliases = []

    # for lang in itemjson['aliases']:
    #     if lang in itemjson['labels'] and lang in itemjson['aliases']:
    #         if itemjson['labels'][lang] in itemjson['aliases'][lang]:
    #             itemjson['aliases'][lang].remove(itemjson['labels'][lang])
    #     for alias in itemjson['aliases'][lang]:
    #         itemaliases.append(alias)

    for lang in all_languages_in_data:
        # if lang in itemjson['aliases'] and not lang in itemjson['labels']:
        #     itemjson['labels'][lang] = itemjson['aliases'][lang][0]
        #     itemlabels.append({'lang': lang, 'value':itemjson['aliases'][lang][0]['value']})

        if lang != "fr": # french was our original, labels are not from wikidata
            qualifiers = [{'prop_nr':'P58', 'type':'string', 'value':'from Wikidata'}]
        else:
            qualifiers = []
        statements.append({'prop_nr':'P57', 'type': 'monolingualtext', 'value':itemjson['labels'][lang]['value'], 'lang':lang,
                           'qualifiers':qualifiers})
    xwbi.itemwrite({'qid': concept_id, 'statements': statements, 'labels':itemlabels, 'aliases':itemaliases})
    count += 1


    