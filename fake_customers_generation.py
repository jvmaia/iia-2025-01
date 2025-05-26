# Gerar clientes fakes para teste

clients = ["Ana","Beatriz","Camila","Daniela","Elisa","Fernanda","Gabriela","Heloísa","Isabela","Júlia","Juliana","Larissa","Mariana","Natália","Olívia","Patrícia","Rafaela","Sabrina","Tatiane","Vanessa","Yasmin","Mônica","Débora","Cíntia","Érica","André","Bruno","Caio","Diego","Eduardo","Felipe","Gabriel","Henrique","Igor","João","Lucas","Leandro","Marcelo","Nicolas","Otávio","Paulo","Rafael","Sérgio","Tiago","Vinícius","Alexandre","Gustavo","Matheus","Pedro","Rodrigo"]

products = ['Abacate', 'Abacaxi', 'Abóbora', 'Abóbora italiana', 'Abóbora japonesa - Tetsukabut', 'Abóbora menina', 'Acerola', 'Agrião', 'Alface', 'Alho', 'Atemóia', 'Banana', 'Batata', 'Batata-doce', 'Berinjela', 'Beterraba', 'Brazlândia', 'Brócolis - Cabeça Única', 'Brócolis - Ramoso', 'Cajamanga', 'Caqui', 'Cebola', 'Cebolinha', 'Ceilândia', 'Cenoura', 'Chuchu', 'Coco', 'Coentro', 'Couve', 'Couve-flor', 'Gama', 'Gengibre', 'Goiaba', 'Graviola', 'Jabuticaba', 'Jardim', 'Jiló', 'Laranja', 'Lichia', 'Limão', 'Mamão', 'Mandioca', 'Manga', 'Maracujá', 'Maracujá Pérola', 'Milho doce', 'Milho-verde', 'Mirtilo', 'Morango', 'PAD-DF', 'Paranoá', 'Pepino', 'Pimentão', 'Pipiripau', 'Pitaia', 'Planaltina', 'Quiabo', 'Repolho', 'Rio Preto', 'Sobradinho', 'São Sebastião', 'Tabatinga', 'Tangerina', 'Taquara', 'Tomate', 'Uva', 'Uva Vinífera', 'Vargem Bonita']

original_locations = ['Alexandre Gusmão', 'Brazlândia', 'Ceilândia', 'Gama', 'Jardim', 'PAD-DF', 'Paranoá', 'Pipiripau', 'Planaltina', 'Rio Preto', 'Sobradinho', 'São Sebastião', 'Tabatinga', 'Taquara', 'Vargem Bonita']
locations = original_locations.copy()

locations_products = {'Alexandre Gusmão': ['Goiaba', 'Abacate', 'Tangerina', 'Limão', 'Banana', 'Graviola', 'Maracujá', 'Manga', 'Atemóia', 'Uva', 'Brazlândia', 'Alface', 'Mandioca', 'Brócolis - Cabeça Única', 'Repolho', 'Couve', 'Cebolinha', 'Tomate', 'Chuchu', 'Brócolis - Ramoso', 'Pimentão', 'Brazlândia'],'Brazlândia': ['Goiaba', 'Abacate', 'Limão', 'Tangerina', 'Banana', 'Atemóia', 'Maracujá', 'Manga', 'Uva', 'Cajamanga', 'Ceilândia', 'Morango', 'Alface', 'Repolho', 'Abóbora italiana', 'Mandioca', 'Brócolis - Cabeça Única', 'Chuchu', 'Tomate', 'Pimentão', 'Couve', 'Ceilândia'],'Ceilândia': ['Banana', 'Limão', 'Abacate', 'Tangerina', 'Maracujá', 'Manga', 'Laranja', 'Goiaba', 'Coco', 'Acerola', 'Gama', 'Alface', 'Mandioca', 'Milho-verde', 'Brócolis - Cabeça Única', 'Repolho', 'Brócolis - Ramoso', 'Batata-doce', 'Chuchu', 'Couve', 'Tomate', 'Gama'],'Gama': ['Limão', 'Abacate', 'Banana', 'Tangerina', 'Manga', 'Acerola', 'Pitaia', 'Maracujá', 'Laranja', 'Lichia', 'Jardim', 'Alface', 'Mandioca', 'Milho-verde', 'Coentro', 'Brócolis - Cabeça Única', 'Couve', 'Cebolinha', 'Brócolis - Ramoso', 'Repolho', 'Pimentão', 'Jardim'],'Jardim': ['Maracujá', 'Uva Vinífera', 'Limão', 'Tangerina', 'Graviola', 'Banana', 'Abacate', 'Goiaba', 'Mamão', 'PAD-DF', 'Cenoura', 'Cebola', 'Abóbora japonesa - Tetsukabut', 'Tomate', 'Beterraba', 'Batata-doce', 'Mandioca', 'Repolho', 'Pimentão', 'Berinjela', 'PAD-DF'],'PAD-DF': ['Uva Vinífera', 'Uva', 'Abacate', 'Limão', 'Maracujá', 'Banana', 'Manga', 'Tangerina', 'Mamão', 'Laranja', 'Paranoá', 'Tomate', 'Milho doce', 'Cenoura', 'Cebola', 'Pepino', 'Mandioca', 'Alface', 'Pimentão', 'Repolho', 'Berinjela', 'Paranoá'],'Paranoá': ['Banana', 'Limão', 'Manga', 'Uva', 'Abacate', 'Tangerina', 'Goiaba', 'Maracujá', 'Laranja', 'Maracujá Pérola', 'Pipiripau', 'Alface', 'Milho-verde', 'Mandioca', 'Beterraba', 'Tomate', 'Quiabo', 'Pimentão', 'Repolho', 'Berinjela', 'Chuchu', 'Pipiripau'],'Pipiripau': ['Laranja', 'Banana', 'Limão', 'Lichia', 'Goiaba', 'Abacate', 'Pitaia', 'Maracujá', 'Tangerina', 'Uva', 'Planaltina', 'Batata', 'Mandioca', 'Tomate', 'Pimentão', 'Abóbora', 'Cenoura', 'Pepino', 'Abóbora italiana', 'Berinjela', 'Chuchu', 'Planaltina'],'Planaltina': ['Limão', 'Banana', 'Lichia', 'Abacate', 'Tangerina', 'Manga', 'Uva', 'Maracujá', 'Laranja', 'Goiaba', 'Rio Preto', 'Milho-verde', 'Mandioca', 'Batata-doce', 'Tomate', 'Alface', 'Cebolinha', 'Repolho', 'Pimentão', 'Chuchu', 'Couve', 'Rio Preto'],'Rio Preto': ['Abacate', 'Tangerina', 'Banana', 'Limão', 'Maracujá', 'Jabuticaba', 'Manga', 'Pitaia', 'Graviola', 'Laranja', 'São Sebastião', 'Alho', 'Mandioca', 'Abóbora japonesa - Tetsukabut', 'Batata-doce', 'Beterraba', 'Abóbora', 'Tomate', 'Pimentão', 'Cenoura', 'Repolho', 'São Sebastião'],'São Sebastião': ['Maracujá', 'Manga', 'Banana', 'Limão', 'Maracujá Pérola', 'Tangerina', 'Abacate', 'Laranja', 'Abacaxi', 'Pitaia', 'Sobradinho', 'Cebola', 'Mandioca', 'Alface', 'Abóbora', 'Morango', 'Quiabo', 'Couve', 'Tomate', 'Agrião', 'Repolho', 'Sobradinho'],'Sobradinho': ['Banana', 'Abacate', 'Manga', 'Limão', 'Uva', 'Tangerina', 'Maracujá', 'Mirtilo', 'Laranja', 'Maracujá Pérola', 'Tabatinga', 'Mandioca', 'Alface', 'Repolho', 'Brócolis - Ramoso', 'Tomate', 'Couve', 'Couve-flor', 'Berinjela', 'Pimentão', 'Chuchu', 'Tabatinga'],'Tabatinga': ['Abacate', 'Limão', 'Maracujá', 'Tangerina', 'Banana', 'Goiaba', 'Maracujá Pérola', 'Pitaia', 'Manga', 'Uva', 'Taquara', 'Batata-doce', 'Mandioca', 'Cenoura', 'Cebola', 'Abóbora japonesa - Tetsukabut', 'Beterraba', 'Jiló', 'Repolho', 'Chuchu', 'Tomate', 'Taquara'],'Taquara': ['Banana', 'Tangerina', 'Abacate', 'Maracujá', 'Limão', 'Laranja', 'Manga', 'Pitaia', 'Caqui', 'Acerola', 'Vargem Bonita', 'Mandioca', 'Abóbora menina', 'Pimentão', 'Tomate', 'Abóbora italiana', 'Berinjela', 'Pepino', 'Couve-flor', 'Repolho', 'Chuchu', 'Vargem Bonita'],'Vargem Bonita': ['Banana', 'Abacate', 'Limão', 'Manga', 'Uva', 'Pitaia', 'Tangerina', 'Maracujá', 'Maracujá Pérola', 'Laranja', 'Alface', 'Mandioca', 'Milho-verde', 'Gengibre', 'Couve', 'Brócolis - Cabeça Única', 'Repolho', 'Cebolinha', 'Brócolis - Ramoso', 'Pimentão']}

# para cada cliente, adicionar uma localidade aleatória e gerar 50 pedidos com alimentos diferentes
# para produtos da mesma localidade, adicionar uma quantidade aleatória entre 1 e 10 mais alta

import random

sells_data = []
for client in clients:
    if len(locations) == 0:
        locations = original_locations.copy()

    location = random.choice(locations)
    locations.remove(location)
    for _ in range(100):
        # caso ja tenha comprado o produto anteriormente, aumentar a probabilidade de comprar novamente
        weights = []
        previous_products = []
        for sell in sells_data:
            if sell['client'] == client:
                previous_products.append(sell['product'])

        for p in products:
            if p in previous_products:
                weights.append(100)
            elif p in locations_products[location]:
                weights.append(25)
            else:
                weights.append(1)

        product = random.choices(products, weights=weights, k=1)[0]
        quantity = random.randint(0, 10)
        if product in locations_products[location]:
            quantity = random.randint(50, 100)

        sells_data.append({
            'client': client,
            'location': location,
            'product': product,
            'quantity': quantity
        })

print(sells_data)

# salvar em csv
import pandas as pd

df = pd.DataFrame(sells_data)
df.to_csv('data/sells_data.csv', index=False)

