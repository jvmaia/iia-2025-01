#!/usr/bin/env python3
"""
ai.py

Implementa recomendações de produtos para clientes usando filtragem colaborativa KNN,
incorporando recência, feedback, filtragem de ruído, transformações TF–IDF e normalização.
Agora suporta sobrescrever os hiperparâmetros a partir de um arquivo JSON de melhores
parâmetros (grid search), via flag -f/--best-params ou ao detectar best_params.json no CWD.
"""

import os
import argparse
import json
import logging
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import normalize

# === Configurações padrão do modelo ===
K_VIZINHOS = 20  # número de vizinhos
K_RECS = 10  # número de recomendações
ALPHA = 0.01  # taxa de decaimento de recência
MIN_PRODUCT_SUPPORT = 5  # min clientes por produto
MIN_CLIENT_TRANSACTIONS = 5  # min transações por cliente
MIN_QUANTITY = 5  # min quantidade para usar interação

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# === Sobrescreve via best_params.json se disponível ===
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-f",
    "--best-params",
    help="Caminho para JSON com melhores parâmetros (precision@K, recall@K, params)",
)
# parse_known_args para não interferir em outros usos de argparse
args, _ = parser.parse_known_args()
# determina arquivo de parâmetros
best_path = args.best_params or os.path.join(os.getcwd(), "grid_search", "best_params.json")
if best_path and os.path.isfile(best_path):
    try:
        with open(best_path, "r", encoding="utf-8") as bf:
            best_data = json.load(bf)
        params = best_data.get("params", {})
        for name in (
            "K_VIZINHOS",
            "K_RECS",
            "ALPHA",
            "MIN_QUANTITY",
            "MIN_PRODUCT_SUPPORT",
            "MIN_CLIENT_TRANSACTIONS",
        ):
            if name in params:
                old = globals()[name]
                globals()[name] = params[name]
                logger.info("Hiperparâmetro %s: %s → %s", name, old, params[name])
        logger.info("Hiperparâmetros carregados de '%s'", best_path)
    except Exception as e:
        logger.warning("Falha ao carregar parâmetro de '%s': %s", best_path, e)

# === Carregamento e preparação dos dados ===
logger.info("Carregando dados de vendas")
df_comp = pd.read_csv("data/sells_data.csv")

logger.info("Removendo interações com quantity < %d", MIN_QUANTITY)
df_comp = df_comp[df_comp["quantity"] >= MIN_QUANTITY]

logger.info("Convertendo datas e calculando recência (ALPHA=%s)", ALPHA)
df_comp["date"] = pd.to_datetime(df_comp["date"])
max_date = df_comp["date"].max()
df_comp["days_since"] = (max_date - df_comp["date"]).dt.days
df_comp["recency_weight"] = 1 / (1 + ALPHA * df_comp["days_since"])
df_comp["weighted_quantity"] = df_comp["quantity"] * df_comp["recency_weight"]

logger.info(
    "Filtrando produtos com suporte < %d e clientes com < %d transações",
    MIN_PRODUCT_SUPPORT,
    MIN_CLIENT_TRANSACTIONS,
)
support = df_comp.groupby("product")["client"].nunique()
popular_products = support[support >= MIN_PRODUCT_SUPPORT].index
df_comp = df_comp[df_comp["product"].isin(popular_products)]
txn_counts = df_comp["client"].value_counts()
active_clients = txn_counts[txn_counts >= MIN_CLIENT_TRANSACTIONS].index
df_comp = df_comp[df_comp["client"].isin(active_clients)]

logger.info("Gerando matriz cliente×produto (weighted_quantity)")
pivot = df_comp.pivot_table(
    index="client", columns="product", values="weighted_quantity", aggfunc="sum", fill_value=0
)

logger.info("Mapeando feedback e incluindo avg_feedback")
feedback_map = {"Excelente": 5, "Bom": 4, "Regular": 3, "Ruim": 2, "Péssimo": 1}
df_comp["feedback_score"] = df_comp["customerFeedback"].map(feedback_map)
feedback_avg = df_comp.groupby("client")["feedback_score"].mean().rename("avg_feedback")
pivot = pivot.merge(feedback_avg, left_index=True, right_index=True)

dense_matrix = pivot.values

logger.info("Aplicando TF–IDF + normalização L2")
tfidf_matrix = TfidfTransformer().fit_transform(dense_matrix)
norm_matrix = normalize(tfidf_matrix, norm="l2", axis=1)

df_sparse = csr_matrix(norm_matrix.toarray())
tt_clientes = pivot.index.tolist()
bursos = pivot.columns.tolist()

logger.info("Treinando KNN (K_VIZINHOS=%d, métrica=cosine)", K_VIZINHOS)
knn = NearestNeighbors(n_neighbors=K_VIZINHOS, metric="cosine", algorithm="brute")
knn.fit(df_sparse)
logger.info("Modelo KNN treinado")


def recomendar_por_cliente(client: str, k_vizinhos: int = K_VIZINHOS, k_recs: int = K_RECS) -> list:
    if client not in tt_clientes:
        logger.error("Cliente não encontrado: %s", client)
        raise ValueError(f"Cliente '{client}' não encontrado.")
    idx = tt_clientes.index(client)
    dists, idxs = knn.kneighbors(df_sparse[idx], n_neighbors=k_vizinhos + 1)
    neighbors = list(idxs[0])
    if idx in neighbors:
        neighbors.remove(idx)
    neighbors = neighbors[:k_vizinhos]
    scores = np.array(df_sparse[neighbors].sum(axis=0)).ravel()
    top = np.argsort(scores)[::-1][:k_recs]
    return [bursos[i] for i in top]


def get_client_purchases(client: str) -> list[dict]:
    if client not in tt_clientes:
        raise ValueError(f"Cliente '{client}' não encontrado.")
    df_c = df_comp[df_comp["client"] == client]
    df_s = df_c.sort_values("quantity", ascending=False)
    return df_s[["product", "quantity"]].to_dict("records")


if __name__ == "__main__":
    sample = tt_clientes[0] if tt_clientes else None
    if sample:
        print(f"Recomendações para {sample}:")
        print(recomendar_por_cliente(sample))
