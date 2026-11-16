with open('data/indice_de_conceptos_normalized.txt', 'r', encoding="utf-8") as file:
    lines = file.read().split('\n')
    result_text = ""
    active_letter = None
    for line in lines:
        if line.startswith("@"):
            active_letter = line[1]
        else:
            if not line.startswith(active_letter) and not line.startswith(active_letter.lower()):
                line = "** " + line
            else:
                line = "* " + line

        result_text += line + "\n"

with open('data/indice_de_conceptos_normalized_indented.txt', 'w', encoding="utf-8") as file:
    file.write(result_text)
