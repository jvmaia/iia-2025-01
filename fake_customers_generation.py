"""
fake_customers_generation.py

Gera um dataset de vendas fictícias para teste, considerando:
- Probabilidades diferenciadas para produtos já comprados,
- Preferências regionais (lista de produtos por localidade),
- Quantidades e feedback simulados,
- Datas randômicas dentro de um período.
"""

import random
import pandas as pd
from data.source import CLIENTS, PRODUCTS, ORIGINAL_LOCATIONS, LOCATIONS_PRODUCTS, FEEDBACK_OPTIONS

# === Configurações de geração ===
NUM_ORDERS_PER_CLIENT = 100  # Quantidade de pedidos por cliente
MAX_DATE_OFFSET_DAYS = 365  # Intervalo máximo para datas futuras
OUTPUT_CSV_PATH = "data/sells_data.csv"  # Caminho de saída


def generate_fake_sales() -> list[dict]:
    """
    Gera registros de vendas fictícias:
    - Cada cliente recebe NUM_ORDERS_PER_CLIENT entradas.
    - Produtos com histórico ou típicos da localidade têm maior probabilidade.
    - Quantidades são maiores para produtos regionais.
    - Datas são offset aleatório até MAX_DATE_OFFSET_DAYS dias.

    Retorna:
        Listagem de dicionários prontos para DataFrame.
    """
    sells = []
    base_date = pd.Timestamp.now().normalize()

    for idx, client in enumerate(CLIENTS):
        # Atribui localidade de forma cíclica
        location = ORIGINAL_LOCATIONS[idx % len(ORIGINAL_LOCATIONS)]

        # Histórico de produtos comprados para o cliente
        client_history = []

        for _ in range(NUM_ORDERS_PER_CLIENT):
            # Calcula pesos para escolha de produto
            weights = [
                100
                if p in client_history
                else 25
                if p in LOCATIONS_PRODUCTS.get(location, [])
                else 1
                for p in PRODUCTS
            ]
            product = random.choices(PRODUCTS, weights=weights, k=1)[0]

            # Define quantidade com base em regionalidade
            if product in LOCATIONS_PRODUCTS.get(location, []):
                quantity = random.randint(50, 100)
            else:
                quantity = random.randint(1, 10)

            # Simula data com deslocamento aleatório
            date = (
                base_date
                + pd.Timedelta(days=random.randint(0, MAX_DATE_OFFSET_DAYS))
                + pd.Timedelta(hours=random.randint(0, 23))
                + pd.Timedelta(minutes=random.randint(0, 59))
            )

            # Cria registro e atualiza histórico
            record = {
                "client": client,
                "location": location,
                "product": product,
                "quantity": quantity,
                "customerFeedback": random.choice(FEEDBACK_OPTIONS),
                "date": date,
            }
            sells.append(record)
            client_history.append(product)

    return sells


if __name__ == "__main__":
    # Gera dados e salva em CSV
    df_sales = pd.DataFrame(generate_fake_sales())
    df_sales.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"Geração de dados concluída. Arquivo salvo em '{OUTPUT_CSV_PATH}'.")
