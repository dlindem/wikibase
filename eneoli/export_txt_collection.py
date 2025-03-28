import os, re

collection = """Q1716
Q511
Q491
Q479
Q255
Q2209
Q2210
Q2211
Q2212
Q2213
Q2214
Q2215
Q2216
Q2217
Q2218
Q2219
Q2220
Q2221
Q2222
Q2302
Q2224
Q2225
Q2226
Q2227
Q2228
Q1662
Q2231
Q2229
Q2230
Q2232
Q2233
Q2235
Q2236
Q2237
Q2238
Q2234
Q2093
Q2239
Q2240
Q2242
Q2095
Q411
Q209
Q308
Q307
Q305
Q304
Q303
Q278
Q259
Q257
Q258
Q256
Q252
Q254
Q253
Q2396
Q942
Q1656
Q1606
Q2395
Q2394
Q1603
Q2392
Q1602
Q2388
Q2390
Q2387
Q2047
Q2048
Q2054
Q2055
Q2074
Q2080
Q2075
Q2076
Q2077
Q2049
Q2208
Q2078
Q2056
Q2050
Q2065
Q2045
Q2051
Q2052
Q2207
Q2081
Q2046
Q2073
Q2057
Q2053
Q1639
Q2204
Q1638
Q1640
Q2206
Q2079
Q2044
Q2205
Q2068
Q2033
Q2069
Q2070
Q2066
Q2067
Q2071
Q2072
Q2032
Q2058
Q2062
Q2059
Q2063
Q2060
Q2061
Q2064
Q1625
Q2185
Q2186
Q2189
Q2190
Q2191
Q2192
Q2187
Q2183
Q2184
Q2182
Q2176
Q2177
Q2178
Q2179
Q2180
Q2181
Q2202
Q2086
Q2198
Q2381
Q2200
Q2201
Q2199
Q2193
Q2197
Q2371
Q2370
Q2103
Q2102
Q2101
Q2100
Q2099
Q2098
Q2097
Q2096
Q2094
Q2092
Q2091
Q2043
Q2042
Q2041
Q2040
Q2164
Q2173
Q2172
Q2171
Q2169
Q2168
Q2167
Q2166
Q2165
Q2163
Q2162
Q2160
Q2159
Q2158
Q2157
Q2155
Q2307
Q2359
Q2352
""".split('\n')

for (root, dirs, files) in os.walk('/media/david/FATdisk/ENEOLI/NeoCorpus_TXT_for_SkE/'):
    print(root, dirs, files)
    lang_re = re.search(r'/([a-z]{3})$', root)
    if lang_re and len(files) > 0:
        lang = lang_re.group(1)
        for filename in files:
            text_qid_re = re.search(r'^Q\d+', filename)
            if text_qid_re and text_qid_re.group(0) in collection:
                source = f"/media/david/FATdisk/ENEOLI/NeoCorpus_TXT_for_SkE/{lang}/{filename}"
                target = f"/media/david/FATdisk/ENEOLI/NeoCorpus_TXT_for_SkE/blending_subcorpus/{lang}_{filename}"
                os.system(f"cp {source} {target}")