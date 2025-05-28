#!/usr/bin/env python3
"""
grid_search.py

Executa busca exaustiva (grid search) de hiperparâmetros, garantindo
- geração de dados fake antes de cada avaliação,
- inclusão de K_RECS no grid,
- persistência dos melhores parâmetros em disco, sobrescrevendo somente se melhorar.
"""
import importlib
import itertools
import subprocess
import sys
import json
import os
import ai
from evaluate_v2 import avaliar_knn_v2

# Script para geração de dados fictícios
FAKE_SCRIPT = "fake_customers_generation.py"
# Caminho para salvar os melhores parâmetros
BEST_PARAMS_FILE = "best_params.json"

# Grid de hiperparâmetros a testar
param_grid = {
    'K_VIZINHOS': [5, 10, 20],
    'K_RECS': [5, 10, 15],
    'ALPHA': [1e-4, 1e-3, 1e-2],
    'MIN_QUANTITY': [2, 5, 10],
    'MIN_PRODUCT_SUPPORT': [5, 10],
    'MIN_CLIENT_TRANSACTIONS': [5, 10]
}

# Carrega melhores parâmetros existentes, se houver
if os.path.exists(BEST_PARAMS_FILE):
    with open(BEST_PARAMS_FILE, 'r') as f:
        best_result = json.load(f)
else:
    best_result = {
        'precision@K': 0.0,
        'recall@K': 0.0,
        'params': {}
    }

# Itera sobre todas as combinações de hiperparâmetros
for combo in itertools.product(*param_grid.values()):
    params = dict(zip(param_grid.keys(), combo))
    print(f"Testando parâmetros: {params}")

    # 1) Regenera dados fake
    try:
        subprocess.run([sys.executable, FAKE_SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Falha ao gerar dados fake: {e}")
        sys.exit(1)

    # 2) Atualiza constantes no módulo ai.py
    for name, value in params.items():
        setattr(ai, name, value)

    # 3) Recarrega o módulo ai para aplicar novas configurações e recarregar dados
    ai = importlib.reload(ai)

    # 4) Avalia o modelo com k_vizinhos e k_recs
    metrics = avaliar_knn_v2(
        ai.df_comp,
        ai.recomendar_por_cliente,
        k_vizinhos=ai.K_VIZINHOS,
        k_recs=ai.K_RECS
    )
    precision = metrics.get('precision@K', 0)
    recall = metrics.get('recall@K', 0)
    print(f"--> precision@K: {precision:.4f}, recall@K: {recall:.4f}\n")

    # 5) Atualiza melhor resultado se for superior
    if precision > best_result.get('precision@K', 0):
        best_result = {
            'precision@K': precision,
            'recall@K': recall,
            'params': params.copy()
        }
        # Salva imediatamente em disco
        with open(BEST_PARAMS_FILE, 'w') as f:
            json.dump(best_result, f, indent=2)
        print(f"Novo melhor encontrado! Salvo em '{BEST_PARAMS_FILE}'\n")

# Exibe a melhor configuração encontrada
def main():
    print("Melhor configuração final:")
    print(best_result)

if __name__ == '__main__':
    main()