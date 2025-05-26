import csv
with open("major_crops.csv", 'r') as file:
    reader=csv.DictReader(file)
    content = [i for i in reader]

previous_dct = None
new_content = []
for i in range(len(content)):
    dct = content[i]
    if dct and dct['\ufeffLocalidade / Cultura'] == 'Subtotal':
        current_local = previous_dct['\ufeffLocalidade / Cultura']
    else:
        previous_dct = dct
    new_content.append({**dct, '\ufeffLocalidade / Cultura': current_local +'|'+ dct['\ufeffLocalidade / Cultura']})

import copy as cpy

with open("major_crops_formatada.csv", 'w') as file:
    writer=csv.DictWriter(
        file,
        fieldnames=['\ufeffLocalidade / Cultura','Área Plantada (hectares)','Participação no DF (%)','Producão (toneladas)','Participação no DF (%).1','Produtores','Participação']
    )
    for i in new_content:
        copy = cpy.deepcopy(i)
        for field in i:
            if field not in writer.fieldnames:
                print(f'deleting {field}')
                del copy[field]
                print(copy)
        print(copy)
        writer.writerow(copy)