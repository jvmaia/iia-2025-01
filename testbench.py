#!/usr/bin/env python3
import os
import sys
import subprocess
import ast
import json
import time
import signal
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constantes
SCRIPTS = ["fake_customers_generation.py", "ai.py", "evaluate_v2.py"]
MAX_RETRIES = 3


def parse_args():
    parser = argparse.ArgumentParser(
        description="Executa o testbench N vezes, gera logs e métricas."
    )
    parser.add_argument(
        "--n_runs", "-n", type=int, default=100, help="Número de iterações do testbench"
    )
    return parser.parse_args()


def setup_testbench(directory, total):
    """Prepara o diretório de logs e limpa iterações antigas."""
    if os.path.exists(directory):
        for f in os.listdir(directory):
            os.remove(os.path.join(directory, f))
    else:
        os.makedirs(directory)
    print(
        f"[BOOT] Testbench configurado: {total} iterações com até {MAX_RETRIES} tentativas cada."
    )


def extract_metrics(path):
    """Lê o log e retorna o dict de métricas mais recente."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in reversed(f.read().splitlines()):
            try:
                d = ast.literal_eval(line.strip())
                if isinstance(d, dict) and "precision@K" in d:
                    return d
            except (SyntaxError, ValueError):
                continue
    return None


def run_single(idx, directory, total):
    """Executa SCRIPTS na iteração idx; retorna (idx, metrics, tentativas)."""
    log_path = os.path.join(directory, f"iteracao_{idx:02d}.log")
    for attempt in range(1, MAX_RETRIES + 1):
        if os.path.exists(log_path):
            os.remove(log_path)
        with open(log_path, "w") as log:
            for script in SCRIPTS:
                subprocess.run([sys.executable, script], stdout=log, stderr=log)
        metrics = extract_metrics(log_path)
        if metrics:
            return idx, metrics, attempt
        time.sleep(1)
    return idx, {"precision@K": 0.0, "recall@K": 0.0}, MAX_RETRIES


def main():
    args = parse_args()
    total = args.n_runs
    directory = f"testbench_{total}"

    # sinal para interrupção
    stop = False

    def handler(sig, frame):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, handler)

    setup_testbench(directory, total)
    start_time = time.time()
    best = {"iteracao": None, "precision@K": 0.0, "recall@K": 0.0}
    results = []

    executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 1)
    futures = {executor.submit(run_single, i, directory, total): i for i in range(1, total + 1)}

    try:
        for future in as_completed(futures):
            if stop:
                raise KeyboardInterrupt
            idx, metrics, tries = future.result()
            results.append({"iteracao": idx, **metrics, "tentativas": tries})

            # Métricas em tempo real (única linha)
            done = len(results)
            precision = metrics["precision@K"]
            recall = metrics["recall@K"]
            elapsed = time.time() - start_time
            attempts = sum(r["tentativas"] for r in results)
            efficiency = (done / attempts) * 100 if attempts else 0.0

            print(
                f"[EXEC] Iteração {idx}/{total} | precision@K={precision:.4f} | recall@K={recall:.4f} | Eficiência={efficiency:.2f}% | Custo={elapsed:.2f}s",
                end="\r",
                flush=True,
            )

            if precision > best["precision@K"]:
                best = {"iteracao": idx, **metrics}

    except KeyboardInterrupt:
        executor.shutdown(wait=False, cancel_futures=True)
        completed = len(results)
        print(
            f"\n[HALT] Após {completed} iterações. Salvando métricas e renomeando diretório...",
            flush=True,
        )

        # salvar métricas parciais
        elapsed = time.time() - start_time
        attempts = sum(r["tentativas"] for r in results)
        efficiency = (completed / attempts) * 100 if attempts else 0.0
        partial = {
            "best": best,
            "elapsed_time": elapsed,
            "efficiency": efficiency,
            "results": results,
        }
        with open(os.path.join(directory, "metrics.json"), "w") as out:
            json.dump(partial, out, indent=2, ensure_ascii=False)

        # renomear pasta
        new_name = f"testbench_{completed}"
        if os.path.exists(new_name):
            new_name += f"_{int(time.time())}"
        os.rename(directory, new_name)
        print(f"[SAVE] Diretório para '{new_name}'.", flush=True)
        sys.exit(1)

    executor.shutdown()

    # Resumo final
    elapsed = time.time() - start_time
    attempts = sum(r["tentativas"] for r in results)
    efficiency = (total / attempts) * 100 if attempts else 0.0

    print(
        f"\n[DONE] Melhor iteração {best['iteracao']:02d} – precision@K={best['precision@K']:.4f} | recall@K={best['recall@K']:.4f}"
    )
    print(f"[DONE] Custo total={elapsed:.2f}s | Eficiência={efficiency:.2f}%")

    # salvar métricas finais
    final = {"best": best, "elapsed_time": elapsed, "efficiency": efficiency, "results": results}
    with open(os.path.join(directory, "metrics.json"), "w") as out:
        json.dump(final, out, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
