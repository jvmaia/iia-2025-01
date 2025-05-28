from ai import K_VIZINHOS, K_RECS, recomendar_por_cliente, df_comp, knn
import pandas as pd
from scipy.sparse import csr_matrix
import numpy as np


def avaliar_knn_v2(
    df_comp: pd.DataFrame,
    recomendar_fn,
    k_vizinhos: int = K_VIZINHOS,
    k_recs: int = K_RECS,
    test_frac: float = 0.1,
) -> dict:
    """
    Avalia o desempenho do modelo KNN considerando recência e feedback:
      - Separa uma fração de interações de cada cliente para teste.
      - Reajusta o KNN nos dados de treino (ponderados por recência e com feedback médio).
      - Gera recomendações e calcula precision@K e recall@K.
    """
    # Cópia dos dados e marcação de amostras de teste
    df = df_comp.copy()
    df["is_test"] = False
    for cliente, grp in df.groupby("client"):
        n_test = max(1, int(len(grp) * test_frac))
        idxs = grp.sample(n=n_test, random_state=42).index
        df.loc[idxs, "is_test"] = True

    # Separação em treino e teste
    df_train = df[~df["is_test"]]
    df_test = df[df["is_test"]]

    # Pivot dos dados de treino: utiliza weighted_quantity (recência) e adiciona avg_feedback
    pivot_train = df_train.pivot_table(
        index="client", columns="product", values="weighted_quantity", aggfunc="sum", fill_value=0
    )
    feedback_avg = df_train.groupby("client")["feedback_score"].mean().rename("avg_feedback")
    pivot_train = pivot_train.merge(feedback_avg, left_index=True, right_index=True)

    # Converte para matriz esparsa e refaz o KNN
    clientes = pivot_train.index.to_list()
    produtos = pivot_train.columns.to_list()
    mat_train = csr_matrix(pivot_train.values)
    knn.fit(mat_train)

    # Atualiza globais usados por recomendar_por_cliente
    global pivot, localidades, itens, mat_sparse
    pivot = pivot_train
    localidades = clientes
    itens = produtos
    mat_sparse = mat_train

    precisions, recalls = [], []
    # Avaliação de cada cliente no teste
    for cliente in df_test["client"].unique():
        itens_test = df_test.loc[df_test["client"] == cliente, "product"].unique().tolist()
        if not itens_test:
            continue
        recs = recomendar_fn(cliente, k_vizinhos=k_vizinhos, k_recs=k_recs)
        hits = set(recs) & set(itens_test)
        precisions.append(len(hits) / k_recs)
        recalls.append(len(hits) / len(itens_test))

    return {
        "precision@K": float(np.mean(precisions)) if precisions else 0.0,
        "recall@K": float(np.mean(recalls)) if recalls else 0.0,
    }


if __name__ == "__main__":
    metrics = avaliar_knn_v2(df_comp, recomendar_por_cliente)
    print(metrics)  # Exemplo: {'precision@K': 0.2188, 'recall@K': 0.3808}
