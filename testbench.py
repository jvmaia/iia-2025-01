#!/usr/bin/env python3
import os
import sys
import subprocess
import ast
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurações
SCRIPTS = ["fake_customers_generation.py", "ai.py", "evaluate_v2.py"]
TESTBENCH_DIR = "testbench"
BEST_FILE = os.path.join(TESTBENCH_DIR, "best_metrics.json")
N_RUNS = 100
MAX_RETRIES = 3


def setup_testbench():
    """Limpa ou cria o diretório de logs e carrega melhor run anterior."""
    if os.path.exists(TESTBENCH_DIR):
        for f in os.listdir(TESTBENCH_DIR):
            os.remove(os.path.join(TESTBENCH_DIR, f))
    else:
        os.makedirs(TESTBENCH_DIR)

    if os.path.exists(BEST_FILE):
        with open(BEST_FILE, "r") as bf:
            best = json.load(bf)
            best_precision = best.get("precision@K", 0.0)
    else:
        best, best_precision = {}, 0.0

    print("Iniciando o Testbench...")
    print(f"Executando {N_RUNS} runs com até {MAX_RETRIES} tentativas cada...\n")
    return best, best_precision


def extract_metrics_from_log(path):
    """Lê o log inteiro e retorna o dict de métricas ou None se não encontrar."""
    with open(path, "r") as log:
        lines = log.read().splitlines()
    for line in reversed(lines):
        try:
            cand = ast.literal_eval(line.strip())
            if isinstance(cand, dict) and "precision@K" in cand and "recall@K" in cand:
                return cand
        except Exception:
            continue
    return None


def run_single(i):
    """
    Executa a sequência de scripts para a run i,
    com até MAX_RETRIES em caso de falha na extração de métricas.
    """
    log_path = os.path.join(TESTBENCH_DIR, f"run_{i:02d}.log")

    for tentativa in range(1, MAX_RETRIES + 1):
        # Remove log antigo, se existir
        if os.path.exists(log_path):
            os.remove(log_path)

        # Executa cada script, redirecionando stdout/stderr para o log
        with open(log_path, "w") as log:
            for script in SCRIPTS:
                subprocess.run([sys.executable, script], stdout=log, stderr=log)

        # Tenta extrair métricas
        mets = extract_metrics_from_log(log_path)
        if mets is not None:
            return i, mets

        # Se falhou, aguarda e tenta de novo
        print(f"Run {i:02d} falhou na tentativa {tentativa}, refazendo...", flush=True)
        time.sleep(1)

    # Se ainda falhar após MAX_RETRIES, retorna zeros
    print(f"Run {i:02d} falhou após {MAX_RETRIES} tentativas; registrando zeros.", flush=True)
    return i, {"precision@K": 0.0, "recall@K": 0.0}


def main():
    best, best_precision = setup_testbench()
    results = []

    max_workers = os.cpu_count() or 1
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_single, i) for i in range(1, N_RUNS + 1)]
        for future in as_completed(futures):
            i, mets = future.result()
            prec = mets.get("precision@K", 0.0)
            results.append((i, prec, mets))
            # Atualiza melhor run
            if prec > best_precision:
                best_precision = prec
                best = {"run": i, **mets}
                with open(BEST_FILE, "w") as bf:
                    json.dump(best, bf, indent=2, ensure_ascii=False)

    # Imprime resumo
    sorted_res = sorted(results, key=lambda x: x[1], reverse=True)
    print("\nResumo dos resultados (ordenado por precision@K):")
    for rank, (run_id, prec, mets) in enumerate(sorted_res, 1):
        print(
            f"{rank:2d}. Run {run_id:02d} – precision@K: {prec:.4f}, recall@K: {mets.get('recall@K', 0.0):.4f}"
        )
    print(f"\nMelhor run: {best['run']:02d} com precision@K={best_precision:.4f}")


if __name__ == "__main__":
    main()
