#!/usr/bin/env python3
"""
grid_search.py

Busca exaustiva de hiperparâmetros com N runs por combinação (padrão=10),
paralelizado via threading e isolando cada run em seu próprio workspace.
Ao final, salva métricas de tempo detalhadas.
"""

import os
import sys
import subprocess
import ast
import json
import time
import signal
import argparse
import shutil
import logging
import threading
import queue
import itertools
import re


# ANSI colors for level tags
class Colors:
    RESET = "\033[0m"
    INFO = "\033[32m"
    WARNING = "\033[33m"
    ERROR = "\033[31m"


# Hyperparameter grid
PARAM_GRID = {
    "K_VIZINHOS": [5, 10, 20],
    "K_RECS": [5, 10, 15],
    "ALPHA": [1e-4, 1e-3, 1e-2],
    "MIN_QUANTITY": [2, 5, 10],
    "MIN_PRODUCT_SUPPORT": [5, 10],
    "MIN_CLIENT_TRANSACTIONS": [5, 10],
}

FAKE_SCRIPT = "fake_customers_generation.py"
AI_SCRIPT = "ai.py"
EVAL_SCRIPT = "evaluate_v2.py"
SOURCE_IN = "data/source.py"


# Logging setup
class LevelColorFormatter(logging.Formatter):
    LEVEL_COLOR = {
        logging.INFO: Colors.INFO,
        logging.WARNING: Colors.WARNING,
        logging.ERROR: Colors.ERROR,
        logging.CRITICAL: Colors.ERROR,
    }

    def format(self, record):
        ts = time.strftime("%H:%M:%S", self.converter(record.created))
        lvl = record.levelname
        color = self.LEVEL_COLOR.get(record.levelno, Colors.RESET)
        msg = record.getMessage()
        return f"[{ts}] [{color}{lvl}{Colors.RESET}] {msg}"


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(LevelColorFormatter())
logger = logging.getLogger("grid_search")
logger.setLevel(logging.INFO)
logger.handlers = [handler]

# Global stop event
stop_event = threading.Event()


def parse_args():
    p = argparse.ArgumentParser(description="Grid search de hiperparâmetros")
    p.add_argument(
        "--out", "-o", default="grid_search", help="Diretório base para logs e resultados"
    )
    p.add_argument(
        "--reps", "-r", type=int, default=10, help="Número de runs por combinação (padrão: 10)"
    )
    return p.parse_args()


def setup_base_dir(base):
    if os.path.isdir(base):
        shutil.rmtree(base)
    os.makedirs(os.path.join(base, "logs"))
    logger.info("Base directory preparado em '%s/'", base)


def load_global_best(base):
    path = os.path.join(base, "best_params.json")
    if os.path.isfile(path):
        return json.load(open(path, "r", encoding="utf-8"))
    return {"precision@K": 0.0, "recall@K": 0.0, "params": {}, "time": 0.0}


def save_best(best, base):
    path = os.path.join(base, "best_params.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(best, f, indent=2, ensure_ascii=False)
    logger.info("→ Novo melhor salvo em '%s'", path)


def patch_ai_script(ws, params):
    text = open(AI_SCRIPT, "r", encoding="utf-8").read()
    for k, v in params.items():
        pattern = rf"^{k}\s*=.*$"
        repl = f"{k} = {repr(v)}"
        text = re.sub(pattern, repl, text, flags=re.MULTILINE)
    open(os.path.join(ws, "ai.py"), "w", encoding="utf-8").write(text)


def extract_metrics(logfile):
    try:
        lines = open(logfile, "r", encoding="utf-8", errors="ignore").read().splitlines()
    except Exception as e:
        logger.error("Erro ao ler log '%s': %s", logfile, e)
        return None
    for line in reversed(lines):
        t = line.strip()
        if t.startswith("{") and t.endswith("}"):
            try:
                d = ast.literal_eval(t)
            except (SyntaxError, ValueError) as e:
                logger.error("Erro ao avaliar linha '%s' em '%s': %s", t, logfile, e)
                continue
            if isinstance(d, dict) and "precision@K" in d:
                return d
    return None


def run_rep(combo_idx, rep_idx, params, base):
    """Executa fake + eval em workspace isolado e retorna métricas e tempo."""
    ws = os.path.join(base, "logs", f"combo_{combo_idx:03d}", f"run_{rep_idx:02d}")
    os.makedirs(ws, exist_ok=True)
    data_dir = os.path.join(ws, "data")
    os.makedirs(data_dir, exist_ok=True)
    shutil.copy(os.path.abspath(SOURCE_IN), os.path.join(data_dir, "source.py"))
    patch_ai_script(ws, params)
    shutil.copy(os.path.abspath(FAKE_SCRIPT), os.path.join(ws, FAKE_SCRIPT))
    shutil.copy(os.path.abspath(EVAL_SCRIPT), os.path.join(ws, EVAL_SCRIPT))

    logp = os.path.join(ws, "run.log")
    start = time.time()
    with open(logp, "w", encoding="utf-8") as log:
        subprocess.run([sys.executable, FAKE_SCRIPT], cwd=ws, stdout=log, stderr=log, check=True)
    with open(logp, "a", encoding="utf-8") as log:
        subprocess.run([sys.executable, EVAL_SCRIPT], cwd=ws, stdout=log, stderr=log, check=True)

    mets = extract_metrics(logp) or {"precision@K": 0.0, "recall@K": 0.0}
    elapsed = time.time() - start
    return combo_idx, rep_idx, mets["precision@K"], mets["recall@K"], elapsed


def print_progress(combo_idx, done, reps, avg_p, avg_r, avg_t):
    msg = (
        f"[Combo {combo_idx:03d}] {done}/{reps} runs — "
        f"avg-prec@K={avg_p:.4f}, avg-rec@K={avg_r:.4f}, avg-time={avg_t:.1f}s"
    )
    print(f"{Colors.INFO}{msg}{Colors.RESET}", end="\r", flush=True)


def main():
    args = parse_args()
    base = args.out
    reps = args.reps
    setup_base_dir(base)

    best = load_global_best(base)
    combos = list(itertools.product(*PARAM_GRID.values()))
    total = len(combos)
    logger.info("Total combos: %d. Runs por combo: %d", total, reps)

    # Prepare task queue
    task_q = queue.Queue()
    for idx, combo in enumerate(combos, start=1):
        params = dict(zip(PARAM_GRID.keys(), combo))
        for rep in range(1, reps + 1):
            task_q.put((idx, rep, params))

    # Result storage
    results = {i: [] for i in range(1, total + 1)}
    completed = 0
    expected = total * reps

    # Worker thread
    def worker():
        while not stop_event.is_set():
            try:
                combo_idx, rep_idx, params = task_q.get(block=False)
            except queue.Empty:
                return
            try:
                out = run_rep(combo_idx, rep_idx, params, base)
                result_q.put(out)
            except Exception as e:
                logger.error("Erro combo %d run %d: %s", combo_idx, rep_idx, e)
            finally:
                task_q.task_done()

    # Result queue
    result_q = queue.Queue()

    # Start threads
    n_workers = os.cpu_count() or 1
    threads = []
    for _ in range(n_workers):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)

    # Handle Ctrl+C
    def sigint_handler(sig, frame):
        stop_event.set()
        print()
        logger.warning("Ctrl+C detectado — aguardando runs em andamento...")

    signal.signal(signal.SIGINT, sigint_handler)

    # Collect results
    while completed < expected and not stop_event.is_set():
        try:
            combo_idx, rep_idx, p, r, t = result_q.get(timeout=0.5)
        except queue.Empty:
            continue
        completed += 1
        lst = results[combo_idx]
        lst.append((p, r, t))
        done = len(lst)
        avg_p = sum(x for x, _, _ in lst) / done
        avg_r = sum(y for _, y, _ in lst) / done
        avg_t = sum(z for *_, z in lst) / done
        print_progress(combo_idx, done, reps, avg_p, avg_r, avg_t)

        if done == reps and avg_p > best["precision@K"]:
            best = {
                "precision@K": avg_p,
                "recall@K": avg_r,
                "params": dict(zip(PARAM_GRID.keys(), combos[combo_idx - 1])),
                "time": avg_t,
            }
            save_best(best, base)

    # Wait threads finish
    for t in threads:
        t.join()

    print()  # newline after progress

    # Build summary
    summary = {"best": best, "combos": []}
    for idx, combo in enumerate(combos, start=1):
        lst = results[idx]
        avg_p = sum(x for x, _, _ in lst) / len(lst) if lst else 0.0
        avg_r = sum(y for _, y, _ in lst) / len(lst) if lst else 0.0
        avg_t = sum(z for *_, z in lst) / len(lst) if lst else 0.0
        summary["combos"].append(
            {
                "idx": idx,
                "params": dict(zip(PARAM_GRID.keys(), combo)),
                "avg_precision@K": avg_p,
                "avg_recall@K": avg_r,
                "avg_time": avg_t,
                "runs": len(lst),
            }
        )

    # --- Time metrics block START ---
    # total time per combo
    combo_times = {combo["idx"]: combo["avg_time"] * combo["runs"] for combo in summary["combos"]}
    # total grid time
    total_grid_time = sum(combo_times.values())
    # percent of grid per combo
    combo_percent = {idx: (t / total_grid_time) * 100 for idx, t in combo_times.items()}
    # locate best combo index from best["params"]
    params_tuple = tuple(best["params"][k] for k in PARAM_GRID.keys())
    combo_index_map = {
        tuple(c): i for i, c in enumerate(itertools.product(*PARAM_GRID.values()), start=1)
    }
    best_combo_idx = combo_index_map[params_tuple]
    # winner run time
    winner_run_time = best["time"]
    # total time of winner’s combo
    winner_combo_time = combo_times[best_combo_idx]
    # percent that combo took of the whole grid
    winner_combo_pct = combo_percent[best_combo_idx]

    time_metrics = {
        "winner_run_time": winner_run_time,
        "winner_combo_total_time": winner_combo_time,
        "winner_combo_pct_of_grid": winner_combo_pct,
        "combo_times": {
            idx: {"total_time": t, "pct_of_grid": combo_percent[idx]}
            for idx, t in combo_times.items()
        },
        "total_grid_time": total_grid_time,
    }
    summary["time_metrics"] = time_metrics
    # --- Time metrics block END ---

    # Save summary to disk
    metrics_path = os.path.join(base, "grid_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    logger.info("Grid search completo. Resumo em '%s'", metrics_path)

    # Print final best and time metrics
    print("\nMelhor configuração encontrada:")
    print(json.dumps(best, indent=2, ensure_ascii=False))
    print("\n=== Time Metrics ===")
    print(f"Run vencedor: {winner_run_time:.2f}s")
    print(
        f"Combo #{best_combo_idx:03d} total: {winner_combo_time:.2f}s "
        f"({winner_combo_pct:.2f}% do grid)"
    )
    print(f"Tempo total do grid: {total_grid_time:.2f}s\n")
    print("Detalhe por combo:")
    for idx, tm in time_metrics["combo_times"].items():
        print(f"  Combo {idx:03d}: {tm['total_time']:.2f}s ({tm['pct_of_grid']:.2f}% do grid)")


if __name__ == "__main__":
    main()
