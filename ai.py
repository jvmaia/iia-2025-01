"""
Sistema de recomendação de produtos agrícolas baseado em similaridade de clientes.
Utiliza o algoritmo de K-Nearest Neighbors (KNN) para encontrar clientes similares
e recomendar produtos com base no histórico de compras desses clientes.
"""

import pandas as pd
from scipy.sparse import csr_matrix
import logging
import numpy as np
from sklearn.neighbors import NearestNeighbors

# Configurações do sistema de recomendação
K_VIZINHOS = 5  # Número de clientes similares a considerar
K_RECS = 10     # Número de recomendações a retornar

# Configuração do sistema de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Carregamento e pré-processamento dos dados
logger.info('Starting data loading process')
df_comp = pd.read_csv('data/sells_data.csv')
logger.info(f'Loaded data with shape: {df_comp.shape}')

# Criação da matriz cliente-produto (pivot table)
# Cada linha representa um cliente, cada coluna um produto
# Os valores são as quantidades totais compradas
logger.info('Creating pivot table')
pivot = df_comp.pivot_table(
    index='client',
    columns='product',
    values='quantity',
    aggfunc='sum',
    fill_value=0
)
logger.info(f'Created pivot table with shape: {pivot.shape}')

# Extração de listas de clientes e produtos
localidades = list(pivot.index)
itens = list(pivot.columns)

# Conversão para matriz esparsa para otimização de memória e processamento
mat_sparse = csr_matrix(pivot.values)
logger.info(f'Converted to sparse matrix with {mat_sparse.nnz} non-zero elements')

# Inicialização do modelo KNN
logger.info('Initializing NearestNeighbors model')
knn = NearestNeighbors(
    n_neighbors=K_VIZINHOS,  # número de vizinhos a considerar
    metric='cosine',         # similaridade por cosseno (adequada para dados esparsos)
    algorithm='brute'        # força bruta é eficiente para datasets pequenos/médios
)
knn.fit(mat_sparse)
logger.info('NearestNeighbors model fitted successfully')

def recomendar_por_cliente(client, k_vizinhos=5, k_recs=10):
    """
    Gera recomendações de produtos para um cliente específico.
    
    Args:
        client (str): Nome do cliente
        k_vizinhos (int): Número de clientes similares a considerar
        k_recs (int): Número de recomendações a retornar
    
    Returns:
        list: Lista dos k_recs produtos mais recomendados
    
    Raises:
        ValueError: Se o cliente não for encontrado no dataset
    """
    localidade = client
    logger.info(f'Starting recommendation process for location: {localidade}')
    
    # Encontra o índice do cliente na matriz
    try:
        idx = localidades.index(localidade)
        logger.info(f'Found location index: {idx}')
    except ValueError:
        logger.error(f"Location not found: {localidade}")
        raise ValueError(f"Localidade '{localidade}' não encontrada.")

    # Encontra os k_vizinhos clientes mais similares
    logger.info(f'Finding {k_vizinhos} nearest neighbors')
    dist, vizinhos = knn.kneighbors(
        mat_sparse[idx],
        n_neighbors=k_vizinhos + 1  # +1 porque inclui o próprio cliente
    )
    vizinhos = vizinhos[0].tolist()
    
    # Remove o próprio cliente da lista de vizinhos
    if idx in vizinhos:
        vizinhos.remove(idx)
    vizinhos = vizinhos[:k_vizinhos]
    logger.info(f'Found {len(vizinhos)} neighbors')
    logger.info(f'Neighbors: {vizinhos}')

    # Calcula a soma das compras dos vizinhos para cada produto
    logger.info('Calculating neighbor purchase sums')
    soma_vizinhos = np.array(mat_sparse[vizinhos].sum(axis=0)).ravel()

    # Seleciona os k_recs produtos mais comprados pelos vizinhos
    logger.info(f'Selecting top {k_recs} recommendations')
    top_idx = np.argsort(soma_vizinhos)[::-1][:k_recs]
    recommendations = [itens[i] for i in top_idx]
    logger.info('Recommendation process completed successfully')
    return recommendations

def get_client_purchases(client):
    """
    Retorna o histórico de compras de um cliente específico.
    
    Args:
        client (str): Nome do cliente
    
    Returns:
        list: Lista de dicionários contendo produto e quantidade comprada
    
    Raises:
        ValueError: Se o cliente não for encontrado no dataset
    """
    if client not in localidades:
        raise ValueError(f"Cliente '{client}' não encontrado.")
    
    client_purchases = df_comp[df_comp['client'] == client].copy()
    client_purchases = client_purchases.sort_values('quantity', ascending=False)
    return client_purchases[['product', 'quantity']].to_dict('records')

# Exemplo de uso do sistema de recomendação
logger.info('Running example recommendation')
print(recomendar_por_cliente('Lucas', k_vizinhos=K_VIZINHOS, k_recs=K_RECS))
