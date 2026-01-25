import json

with open ('content/persons.json') as file:
    persons = json.load(file)
    amount = None
    full_list = []
    for person in persons:
        if not amount:
            amount = person
            full_list += range(int(amount)+1)
            print(full_list)
        full_list.remove(int(person))
full_list.remove(0)
print(full_list)
print(len(full_list))

values_string = '{'
for entry in full_list:
    values_string += f'"persons:{entry}" '
values_string += "}"
print(values_string)
