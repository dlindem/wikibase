import csv, re, time, sys, xwbi

def write_lexeme(lemma):
    attempts = 0
    while attempts < 7:
        attempts += 1
        try:
            lexeme = xwbi.wbi.lexeme.new(lexical_category='Q16', language='Q207') # POS undef, Basque
            lexeme.lemmas.set(language='eu', value=lemma)
            claim_qualifiers = xwbi.Qualifiers()
            claim_qualifiers.add(xwbi.String(prop_nr='P154', value=lemma)) # OEH search string
            claim = xwbi.Item(prop_nr='P6', value="Q200", qualifiers=claim_qualifiers) # described in OEH
            lexeme.claims.add(claim)
            lexeme.write()
            print('successfully written to '+lexeme.id)
            time.sleep(0.2)
            return lexeme.id
        except Exception as ex:
            print(str(ex))
            print('Will try again in 3 sec...')
            time.sleep(3)
    print('\nExit after 7 failed writing attempts.')
    sys.exit()



with open('data/OEH-lemak_orig_utf8.csv', encoding='utf-8') as infile:
    oeh = csv.DictReader(infile, delimiter="\t")
    with open('data/OEH-lemak-mapping.csv', 'w', encoding='utf-8') as outfile:
        outfile.write('line\tlid\tadib\theadword\tnormalized\taftercomma\n')
        seen_normlemma = {}

        for inrow in oeh:
            row = inrow
            skip = False
            row['normalized'] = ""
            row['aftercomma'] = ""
            print(f"\n[line {row['line']}] Now processing {row['headword']}...")
            if re.search(r'[A-Z]', row['headword']):
                print('Skip: Contains capital letter, is subentry')
                row['lid'] = "subentry"
                skip = True
            if row['lid'].startswith('L'):
                print('Skip: Has Lid already.')
                seen_normlemma[row['normalized']] = row['lid']
                skip = True
            if not skip:
                # remove homograph numbers and spaces around
                row['normalized'] = re.sub(r'[0-9]+', '', row['headword']).strip()
                if "," in row['normalized']:
                    splitrow = row['normalized'].split(',')
                    row['normalized'] = splitrow.pop(0).strip()
                    row['aftercomma'] = "|".join(splitrow).strip()
                if " " in row['normalized'] or "-" in row['normalized']:
                    print('Skip: Found space or hyphen: multiword.')
                    row['lid'] = "multiword_mainentry"
                    skip = True
            if not skip:
                print('Will process normalized headword-string: '+row['normalized'])
                lemma = row['normalized']
                if lemma in seen_normlemma:
                    row['lid'] = seen_normlemma[lemma]
                    print(f"{lemma} was written before to {row['lid']}, will write that mapping to file.")
                else:
                    print(f"{lemma}: Will write new lexeme.")
                    row['lid'] = write_lexeme(lemma)
                    seen_normlemma[lemma] = row['lid']
            outfile.write(f"{row['line']}\t{row['lid']}\t{row['adib']}\t{row['headword']}\t{row['normalized']}\t{row['aftercomma']}\n")






