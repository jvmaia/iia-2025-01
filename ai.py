"""
ai.py

Implementa recomendações de produtos para clientes usando filtragem colaborativa KNN,
incorporando recência, feedback, filtragem de ruído, transformações TF–IDF e normalização.
"""

import pandas as pd
from scipy.sparse import csr_matrix
import logging
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import normalize

# === Configurações do modelo ===
K_VIZINHOS = 20  # Quantidade de vizinhos similares a considerar
K_RECS = 10  # Número de itens a recomendar
ALPHA = 0.01  # Taxa de decaimento para ponderação de recência
MIN_PRODUCT_SUPPORT = 5  # Número mínimo de clientes que compraram um produto
MIN_CLIENT_TRANSACTIONS = 5  # Número mínimo de transações por cliente
MIN_QUANTITY = 5  # Quantidade mínima para considerar interação válida

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# === Carregamento e preparação dos dados ===
logger.info("Carregando dados de vendas")
df_comp = pd.read_csv("data/sells_data.csv")

# Filtra interações de quantidade muito baixa
logger.info(f"Removendo interações com quantity < {MIN_QUANTITY}")
df_comp = df_comp[df_comp["quantity"] >= MIN_QUANTITY]

# Converte datas e calcula peso de recência
logger.info("Convertendo datas e calculando recência")
df_comp["date"] = pd.to_datetime(df_comp["date"])
max_date = df_comp["date"].max()
df_comp["days_since"] = (max_date - df_comp["date"]).dt.days
# Peso de recência decai com o tempo
df_comp["recency_weight"] = 1 / (1 + ALPHA * df_comp["days_since"])
# Aplica o peso ao volume comprado
df_comp["weighted_quantity"] = df_comp["quantity"] * df_comp["recency_weight"]

# === Filtragem de ruído geral ===
logger.info("Filtrando produtos esparsos e clientes com poucas transações")
support = df_comp.groupby("product")["client"].nunique()
popular_products = support[support >= MIN_PRODUCT_SUPPORT].index
df_comp = df_comp[df_comp["product"].isin(popular_products)]
txn_counts = df_comp["client"].value_counts()
active_clients = txn_counts[txn_counts >= MIN_CLIENT_TRANSACTIONS].index
df_comp = df_comp[df_comp["client"].isin(active_clients)]

# === Construção da matriz de características ===
logger.info("Gerando pivot table de cliente x produto (weighted_quantity)")
pivot = df_comp.pivot_table(
    index="client", columns="product", values="weighted_quantity", aggfunc="sum", fill_value=0
)

# Mapeia feedback qualitativo para escore numérico e adiciona média por cliente
logger.info("Mapeando feedback e adicionando avg_feedback")
feedback_map = {"Excelente": 5, "Bom": 4, "Regular": 3, "Ruim": 2, "Péssimo": 1}
df_comp["feedback_score"] = df_comp["customerFeedback"].map(feedback_map)
feedback_avg = df_comp.groupby("client")["feedback_score"].mean().rename("avg_feedback")
pivot = pivot.merge(feedback_avg, left_index=True, right_index=True)

# Converte pivot para matriz densa
dense_matrix = pivot.values

# Aplica TF–IDF para ajustar importância de produtos
logger.info("Aplicando TF-IDF nas features")
tfidf = TfidfTransformer()
tfidf_matrix = tfidf.fit_transform(dense_matrix)

# Normaliza vetores cliente para norma L2
logger.info("Normalizando vetores de cliente")
norm_matrix = normalize(tfidf_matrix, norm="l2", axis=1)

# Converte para matriz esparsa para o KNN
dense_norm = norm_matrix.toarray()  # OK para tamanhos moderados
df_sparse = csr_matrix(dense_norm)

# Atualiza variáveis globais
tt_clientes = pivot.index.tolist()
bursos = pivot.columns.tolist()

# === Treinamento do modelo KNN ===
logger.info("Treinando modelo NearestNeighbors")
knn = NearestNeighbors(n_neighbors=K_VIZINHOS, metric="cosine", algorithm="brute")
knn.fit(df_sparse)
logger.info("Modelo treinado com sucesso")

# === Funções de recomendação e histórico ===


def recomendar_por_cliente(client: str, k_vizinhos: int = K_VIZINHOS, k_recs: int = K_RECS) -> list:
    """
    Recomenda produtos para um cliente com base em vizinhos mais similares.

    Args:
        client: identificador do cliente.
        k_vizinhos: número de clientes vizinhos a considerar.
        k_recs: número de itens recomendados.

    Returns:
        Lista de produtos recomendados.
    """
    if client not in tt_clientes:
        logger.error(f"Cliente não encontrado: {client}")
        raise ValueError(f"Cliente '{client}' não encontrado.")

    idx = tt_clientes.index(client)
    dist, viz_idx = knn.kneighbors(df_sparse[idx], n_neighbors=k_vizinhos + 1)
    vizinhos_list = viz_idx[0].tolist()
    if idx in vizinhos_list:
        vizinhos_list.remove(idx)
    vizinhos_list = vizinhos_list[:k_vizinhos]

    scores = np.array(df_sparse[vizinhos_list].sum(axis=0)).ravel()
    top_idx = np.argsort(scores)[::-1][:k_recs]
    return [bursos[i] for i in top_idx]


def get_client_purchases(client: str) -> list[dict]:
    """
    Retorna o histórico de compras de um cliente.
    """
    if client not in tt_clientes:
        raise ValueError(f"Cliente '{client}' não encontrado.")
    df_client = df_comp[df_comp["client"] == client]
    df_sorted = df_client.sort_values("quantity", ascending=False)
    return df_sorted[["product", "quantity"]].to_dict("records")


# Exemplo de execução
if __name__ == "__main__":
    sample = tt_clientes[0] if tt_clientes else None
    if sample:
        print(recomendar_por_cliente(sample))
