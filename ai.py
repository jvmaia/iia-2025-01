import pandas as pd
from scipy.sparse import csr_matrix
import logging

K_VIZINHOS = 5
K_RECS = 10
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Data loading and preprocessing
logger.info('Starting data loading process')
df_comp = pd.read_csv('data/sells_data.csv')
logger.info(f'Loaded data with shape: {df_comp.shape}')

# Create pivot table
logger.info('Creating pivot table')
pivot = df_comp.pivot_table(
    index='client',
    columns='product',
    values='quantity',
    aggfunc='sum',
    fill_value=0
)
logger.info(f'Created pivot table with shape: {pivot.shape}')

localidades = list(pivot.index)
itens = list(pivot.columns)
mat_sparse = csr_matrix(pivot.values)
logger.info(f'Converted to sparse matrix with {mat_sparse.nnz} non-zero elements')

from sklearn.neighbors import NearestNeighbors

logger.info('Initializing NearestNeighbors model')
# usando distância de similaridade de cosseno (mais apropriado para perfis esparsos)
knn = NearestNeighbors(
    n_neighbors=K_VIZINHOS,        # número de vizinhos a considerar
    metric='cosine',      # métrica
    algorithm='brute'     # força bruta é OK para matrizes esparsas pequenas/médias
)
knn.fit(mat_sparse)
logger.info('NearestNeighbors model fitted successfully')

import numpy as np

def recomendar_por_localidade(localidade, k_vizinhos=5, k_recs=10):
    logger.info(f'Starting recommendation process for location: {localidade}')
    
    # 1. encontra índice da localidade
    try:
        idx = localidades.index(localidade)
        logger.info(f'Found location index: {idx}')
    except ValueError:
        logger.error(f"Location not found: {localidade}")
        raise ValueError(f"Localidade '{localidade}' não encontrada.")

    # 2. calcula distâncias e índices dos k_vizinhos+1 (inclui ela mesma)
    logger.info(f'Finding {k_vizinhos} nearest neighbors')
    dist, vizinhos = knn.kneighbors(
        mat_sparse[idx],
        n_neighbors=k_vizinhos + 1
    )
    vizinhos = vizinhos[0].tolist()
    # remove a própria localidade
    if idx in vizinhos:
        vizinhos.remove(idx)
    vizinhos = vizinhos[:k_vizinhos]
    print(dir(vizinhos))
    logger.info(f'Found {len(vizinhos)} neighbors')
    logger.info(f'Neighbors: {vizinhos}')

    # 3. soma as compras dos vizinhos
    logger.info('Calculating neighbor purchase sums')
    soma_vizinhos = np.array(mat_sparse[vizinhos].sum(axis=0)).ravel()

    # 5. seleciona os top-k_recs itens
    logger.info(f'Selecting top {k_recs} recommendations')
    top_idx = np.argsort(soma_vizinhos)[::-1][:k_recs]
    recommendations = [itens[i] for i in top_idx]
    logger.info('Recommendation process completed successfully')
    return recommendations

# Exemplo de uso:
logger.info('Running example recommendation')
print(recomendar_por_localidade('Lucas', k_vizinhos=K_VIZINHOS, k_recs=K_RECS))
