from ai import K_VIZINHOS, K_RECS, recomendar_por_cliente, df_comp, knn
import pandas as pd
from scipy.sparse import csr_matrix
import numpy as np

def avaliar_knn_v2(
    df_comp: pd.DataFrame,
    recomendar_fn,                # a função recomendar_por_localidade
    k_vizinhos: int = K_VIZINHOS,
    k_recs: int = K_RECS,
    test_frac: float = 0.1
) -> dict:
    """
    Avalia o KNN reaproveitando a função recomendar_por_localidade.
    — separar test_frac de cada cliente para teste
    — refitar knn no treino, atualizar globais e chamar recomendar_fn
    """

    df = df_comp.copy()
    df['is_test'] = False
    # marca aleatoriamente test_frac das linhas de cada cliente
    for cliente, grp in df.groupby('client'):
        n_test = max(1, int(len(grp) * test_frac))
        idxs = grp.sample(n=n_test, random_state=42).index
        df.loc[idxs, 'is_test'] = True

    df_train = df[~df['is_test']]
    df_test  = df[df['is_test']]

    # constroem pivot de treino e refaz knn
    pivot_train = df_train.pivot_table(
        index='client',
        columns='product',
        values='quantity',
        aggfunc='sum',
        fill_value=0
    )
    clientes = list(pivot_train.index)
    produtos  = list(pivot_train.columns)
    mat_train = csr_matrix(pivot_train.values)

    # refit do KNN global
    knn.fit(mat_train)

    # atualizar as variáveis globais usadas por recomendar_por_localidade
    global pivot, localidades, itens, mat_sparse
    pivot        = pivot_train
    localidades  = clientes
    itens         = produtos
    mat_sparse   = mat_train

    precisions = []
    recalls    = []

    # avalia cada cliente com dados de teste
    for cliente in df_test['client'].unique():
        itens_test = df_test.loc[df_test['client']==cliente, 'product'].unique().tolist()
        if not itens_test:
            continue

        # chama a função de recomendação pura
        recs = recomendar_fn(cliente, k_vizinhos=k_vizinhos, k_recs=k_recs)

        # métricas
        n_relevantes = len(set(recs) & set(itens_test))
        precisions.append(n_relevantes / k_recs)
        recalls.append(n_relevantes / len(itens_test))

    return {
        'precision@K': float(np.mean(precisions)) if precisions else 0.0,
        'recall@K':    float(np.mean(recalls))    if recalls    else 0.0
    }

metrics = avaliar_knn_v2(df_comp, recomendar_por_cliente,
                         k_vizinhos=K_VIZINHOS, k_recs=K_RECS, test_frac=0.1)
print(metrics)
# Ex.: {'precision@K': 0.2188, 'recall@K': 0.3808}
