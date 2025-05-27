"""
Script para geração de dados sintéticos de vendas para um sistema de recomendação.
Este script gera dados simulados de vendas de produtos agrícolas em diferentes localidades do DF.
"""

# Lista de nomes de clientes para geração de dados sintéticos
clients = ["Ana","Beatriz","Camila","Daniela","Elisa","Fernanda","Gabriela","Heloísa","Isabela","Júlia","Juliana","Larissa","Mariana","Natália","Olívia","Patrícia","Rafaela","Sabrina","Tatiane","Vanessa","Yasmin","Mônica","Débora","Cíntia","Érica","André","Bruno","Caio","Diego","Eduardo","Felipe","Gabriel","Henrique","Igor","João","Lucas","Leandro","Marcelo","Nicolas","Otávio","Paulo","Rafael","Sérgio","Tiago","Vinícius","Alexandre","Gustavo","Matheus","Pedro","Rodrigo"]

# Lista de produtos agrícolas disponíveis para venda
products = ['Abacate', 'Abacaxi', 'Abóbora', 'Abóbora italiana', 'Abóbora japonesa - Tetsukabut', 'Abóbora menina', 'Acerola', 'Agrião', 'Alface', 'Alho', 'Atemóia', 'Banana', 'Batata', 'Batata-doce', 'Berinjela', 'Beterraba', 'Brazlândia', 'Brócolis - Cabeça Única', 'Brócolis - Ramoso', 'Cajamanga', 'Caqui', 'Cebola', 'Cebolinha', 'Ceilândia', 'Cenoura', 'Chuchu', 'Coco', 'Coentro', 'Couve', 'Couve-flor', 'Gama', 'Gengibre', 'Goiaba', 'Graviola', 'Jabuticaba', 'Jardim', 'Jiló', 'Laranja', 'Lichia', 'Limão', 'Mamão', 'Mandioca', 'Manga', 'Maracujá', 'Maracujá Pérola', 'Milho doce', 'Milho-verde', 'Mirtilo', 'Morango', 'PAD-DF', 'Paranoá', 'Pepino', 'Pimentão', 'Pipiripau', 'Pitaia', 'Planaltina', 'Quiabo', 'Repolho', 'Rio Preto', 'Sobradinho', 'São Sebastião', 'Tabatinga', 'Tangerina', 'Taquara', 'Tomate', 'Uva', 'Uva Vinífera', 'Vargem Bonita']

# Lista de localidades do DF onde os produtos são vendidos
original_locations = ['Alexandre Gusmão', 'Brazlândia', 'Ceilândia', 'Gama', 'Jardim', 'PAD-DF', 'Paranoá', 'Pipiripau', 'Planaltina', 'Rio Preto', 'Sobradinho', 'São Sebastião', 'Tabatinga', 'Taquara', 'Vargem Bonita']
locations = original_locations.copy()

# Dicionário que mapeia cada localidade aos produtos típicos daquela região
locations_products = {'Alexandre Gusmão': ['Goiaba', 'Abacate', 'Tangerina', 'Limão', 'Banana', 'Graviola', 'Maracujá', 'Manga', 'Atemóia', 'Uva', 'Brazlândia', 'Alface', 'Mandioca', 'Brócolis - Cabeça Única', 'Repolho', 'Couve', 'Cebolinha', 'Tomate', 'Chuchu', 'Brócolis - Ramoso', 'Pimentão', 'Brazlândia'],'Brazlândia': ['Goiaba', 'Abacate', 'Limão', 'Tangerina', 'Banana', 'Atemóia', 'Maracujá', 'Manga', 'Uva', 'Cajamanga', 'Ceilândia', 'Morango', 'Alface', 'Repolho', 'Abóbora italiana', 'Mandioca', 'Brócolis - Cabeça Única', 'Chuchu', 'Tomate', 'Pimentão', 'Couve', 'Ceilândia'],'Ceilândia': ['Banana', 'Limão', 'Abacate', 'Tangerina', 'Maracujá', 'Manga', 'Laranja', 'Goiaba', 'Coco', 'Acerola', 'Gama', 'Alface', 'Mandioca', 'Milho-verde', 'Brócolis - Cabeça Única', 'Repolho', 'Brócolis - Ramoso', 'Batata-doce', 'Chuchu', 'Couve', 'Tomate', 'Gama'],'Gama': ['Limão', 'Abacate', 'Banana', 'Tangerina', 'Manga', 'Acerola', 'Pitaia', 'Maracujá', 'Laranja', 'Lichia', 'Jardim', 'Alface', 'Mandioca', 'Milho-verde', 'Coentro', 'Brócolis - Cabeça Única', 'Couve', 'Cebolinha', 'Brócolis - Ramoso', 'Repolho', 'Pimentão', 'Jardim'],'Jardim': ['Maracujá', 'Uva Vinífera', 'Limão', 'Tangerina', 'Graviola', 'Banana', 'Abacate', 'Goiaba', 'Mamão', 'PAD-DF', 'Cenoura', 'Cebola', 'Abóbora japonesa - Tetsukabut', 'Tomate', 'Beterraba', 'Batata-doce', 'Mandioca', 'Repolho', 'Pimentão', 'Berinjela', 'PAD-DF'],'PAD-DF': ['Uva Vinífera', 'Uva', 'Abacate', 'Limão', 'Maracujá', 'Banana', 'Manga', 'Tangerina', 'Mamão', 'Laranja', 'Paranoá', 'Tomate', 'Milho doce', 'Cenoura', 'Cebola', 'Pepino', 'Mandioca', 'Alface', 'Pimentão', 'Repolho', 'Berinjela', 'Paranoá'],'Paranoá': ['Banana', 'Limão', 'Manga', 'Uva', 'Abacate', 'Tangerina', 'Goiaba', 'Maracujá', 'Laranja', 'Maracujá Pérola', 'Pipiripau', 'Alface', 'Milho-verde', 'Mandioca', 'Beterraba', 'Tomate', 'Quiabo', 'Pimentão', 'Repolho', 'Berinjela', 'Chuchu', 'Pipiripau'],'Pipiripau': ['Laranja', 'Banana', 'Limão', 'Lichia', 'Goiaba', 'Abacate', 'Pitaia', 'Maracujá', 'Tangerina', 'Uva', 'Planaltina', 'Batata', 'Mandioca', 'Tomate', 'Pimentão', 'Abóbora', 'Cenoura', 'Pepino', 'Abóbora italiana', 'Berinjela', 'Chuchu', 'Planaltina'],'Planaltina': ['Limão', 'Banana', 'Lichia', 'Abacate', 'Tangerina', 'Manga', 'Uva', 'Maracujá', 'Laranja', 'Goiaba', 'Rio Preto', 'Milho-verde', 'Mandioca', 'Batata-doce', 'Tomate', 'Alface', 'Cebolinha', 'Repolho', 'Pimentão', 'Chuchu', 'Couve', 'Rio Preto'],'Rio Preto': ['Abacate', 'Tangerina', 'Banana', 'Limão', 'Maracujá', 'Jabuticaba', 'Manga', 'Pitaia', 'Graviola', 'Laranja', 'São Sebastião', 'Alho', 'Mandioca', 'Abóbora japonesa - Tetsukabut', 'Batata-doce', 'Beterraba', 'Abóbora', 'Tomate', 'Pimentão', 'Cenoura', 'Repolho', 'São Sebastião'],'São Sebastião': ['Maracujá', 'Manga', 'Banana', 'Limão', 'Maracujá Pérola', 'Tangerina', 'Abacate', 'Laranja', 'Abacaxi', 'Pitaia', 'Sobradinho', 'Cebola', 'Mandioca', 'Alface', 'Abóbora', 'Morango', 'Quiabo', 'Couve', 'Tomate', 'Agrião', 'Repolho', 'Sobradinho'],'Sobradinho': ['Banana', 'Abacate', 'Manga', 'Limão', 'Uva', 'Tangerina', 'Maracujá', 'Mirtilo', 'Laranja', 'Maracujá Pérola', 'Tabatinga', 'Mandioca', 'Alface', 'Repolho', 'Brócolis - Ramoso', 'Tomate', 'Couve', 'Couve-flor', 'Berinjela', 'Pimentão', 'Chuchu', 'Tabatinga'],'Tabatinga': ['Abacate', 'Limão', 'Maracujá', 'Tangerina', 'Banana', 'Goiaba', 'Maracujá Pérola', 'Pitaia', 'Manga', 'Uva', 'Taquara', 'Batata-doce', 'Mandioca', 'Cenoura', 'Cebola', 'Abóbora japonesa - Tetsukabut', 'Beterraba', 'Jiló', 'Repolho', 'Chuchu', 'Tomate', 'Taquara'],'Taquara': ['Banana', 'Tangerina', 'Abacate', 'Maracujá', 'Limão', 'Laranja', 'Manga', 'Pitaia', 'Caqui', 'Acerola', 'Vargem Bonita', 'Mandioca', 'Abóbora menina', 'Pimentão', 'Tomate', 'Abóbora italiana', 'Berinjela', 'Pepino', 'Couve-flor', 'Repolho', 'Chuchu', 'Vargem Bonita'],'Vargem Bonita': ['Banana', 'Abacate', 'Limão', 'Manga', 'Uva', 'Pitaia', 'Tangerina', 'Maracujá', 'Maracujá Pérola', 'Laranja', 'Alface', 'Mandioca', 'Milho-verde', 'Gengibre', 'Couve', 'Brócolis - Cabeça Única', 'Repolho', 'Cebolinha', 'Brócolis - Ramoso', 'Pimentão']}

import random
import pandas as pd

sells_data = []
for client in clients:
    # Para cada cliente, atribui uma localidade aleatória
    if len(locations) == 0:
        locations = original_locations.copy()

    location = random.choice(locations)
    locations.remove(location)
    
    # Gera 100 compras aleatórias para cada cliente
    for _ in range(100):
        # Calcula pesos para a seleção de produtos
        # Produtos já comprados anteriormente têm peso maior (100)
        # Produtos da localidade do cliente têm peso médio (25)
        # Outros produtos têm peso baixo (1)
        weights = []
        previous_products = []
        for sell in sells_data:
            if sell['client'] == client:
                previous_products.append(sell['product'])

        for p in products:
            if p in previous_products:
                weights.append(100)  # Maior probabilidade para produtos já comprados
            elif p in locations_products[location]:
                weights.append(25)   # Probabilidade média para produtos da região
            else:
                weights.append(1)    # Baixa probabilidade para outros produtos

        # Seleciona um produto com base nos pesos calculados
        product = random.choices(products, weights=weights, k=1)[0]
        
        # Define a quantidade comprada
        # Produtos da região têm quantidades maiores (50-100)
        # Outros produtos têm quantidades menores (0-10)
        quantity = random.randint(0, 10)
        if product in locations_products[location]:
            quantity = random.randint(50, 100)

        # Adiciona a venda aos dados
        sells_data.append({
            'client': client,
            'location': location,
            'product': product,
            'quantity': quantity
        })

# Salva os dados gerados em um arquivo CSV
df = pd.DataFrame(sells_data)
df.to_csv('data/sells_data.csv', index=False)

