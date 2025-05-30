#!/usr/bin/env python3
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
from concurrent.futures import ThreadPoolExecutor, as_completed


# ANSI colors for level tags
class Colors:
    RESET = "\033[0m"
    INFO = "\033[32m"
    WARNING = "\033[33m"
    ERROR = "\033[31m"


SCRIPTS = ["fake_customers_generation.py", "ai.py", "evaluate_v2.py"]
MAX_RETRIES = 3


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


class FlushHandler(logging.StreamHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()


logger = logging.getLogger("testbench")
logger.setLevel(logging.INFO)
h = FlushHandler(sys.stdout)
h.setFormatter(LevelColorFormatter())
logger.handlers = [h]


def parse_args():
    p = argparse.ArgumentParser(description="Testbench de recomendações")
    g = p.add_mutually_exclusive_group()
    g.add_argument("-n", "--n_runs", type=int, default=100, help="Número de iterações (finito)")
    g.add_argument("-i", "--indefinite", action="store_true", help="Modo indefinido até Ctrl+C")
    return p.parse_args()


def setup_workspace(base):
    if os.path.isdir(base):
        shutil.rmtree(base)
    os.makedirs(os.path.join(base, "logs"))
    logger.info(f"Workspace criado em '{base}/'")


def extract_metrics(logfile):
    try:
        with open(logfile, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.read().splitlines()
    except Exception:
        return None

    for text in reversed(lines):
        text = text.strip()
        if not (text.startswith("{") and text.endswith("}")):
            continue
        try:
            d = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            continue
        if isinstance(d, dict) and "precision@K" in d:
            return d
    return None


def run_single(idx, logs_dir):
    ws = os.path.join(logs_dir, f"Exec_{idx:02d}")
    os.makedirs(ws, exist_ok=True)
    data_dir = os.path.join(ws, "data")
    os.makedirs(data_dir, exist_ok=True)
    shutil.copy(os.path.abspath("data/source.py"), os.path.join(data_dir, "source.py"))
    logpath = os.path.join(ws, f"Exec_{idx:02d}.log")

    for attempt in range(1, MAX_RETRIES + 1):
        if os.path.exists(logpath):
            os.remove(logpath)
        with open(logpath, "w", encoding="utf-8") as log:
            for script in SCRIPTS:
                subprocess.run(
                    [sys.executable, os.path.abspath(script)], cwd=ws, stdout=log, stderr=log
                )
        mets = extract_metrics(logpath)
        if mets:
            return idx, mets, attempt
        time.sleep(1)
    return idx, {"precision@K": 0.0, "recall@K": 0.0}, MAX_RETRIES


def load_global_best():
    path = os.path.join("best", "metrics.json")
    if os.path.isfile(path):
        data = json.load(open(path, "r", encoding="utf-8"))
        return data.get("best", {}).get("precision@K", 0.0)
    return 0.0


def save_best(best):
    dst = "best"
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    with open(os.path.join(dst, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump({"best": best}, f, indent=2, ensure_ascii=False)
    logger.info("Melhor execução salva em 'best/metrics.json'")


def print_progress(idx, total, prec, rec, elapsed):
    prefix = f"[{idx}/{total}]" if total else f"[Run {idx}]"
    msg = f"{Colors.INFO}{prefix}{Colors.RESET} prec@K={prec:.4f} rec@K={rec:.4f} ({elapsed:.1f}s)"
    print(msg, end="\r", flush=True)


def main():
    args = parse_args()
    base = "testbench_indef" if args.indefinite else f"testbench_{args.n_runs}"
    total = None if args.indefinite else args.n_runs
    mode = "indefinido (Ctrl+C para parar)" if args.indefinite else f"finito ({total} execuções)"
    logger.info(f"Modo de execução: {mode}")

    setup_workspace(base)
    logs_dir = os.path.join(base, "logs")
    global_best = load_global_best()
    best = {"Exec": None, "precision@K": global_best, "recall@K": 0.0}
    results, stop = [], False

    def _sigint(sig, frame):
        nonlocal stop
        stop = True
        print()  # newline after progress
        logger.warning("Ctrl+C detectado – encerrando após run atual...")

    signal.signal(signal.SIGINT, _sigint)

    start = time.time()
    executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 1)

    try:
        if args.indefinite:
            # start one per worker
            pool = os.cpu_count() or 1
            futures = {executor.submit(run_single, i + 1, logs_dir): i + 1 for i in range(pool)}
            next_idx = pool + 1
            while futures and not stop:
                done = next(as_completed(futures), None)
                if not done:
                    break
                run_id = futures.pop(done)
                _, mets, tries = done.result()
                results.append({"Exec": run_id, **mets, "retries": tries})
                elapsed = time.time() - start
                print_progress(run_id, None, mets["precision@K"], mets["recall@K"], elapsed)
                if mets["precision@K"] > best["precision@K"]:
                    best = {"Exec": run_id, **mets}
                    save_best(best)
                if not stop:
                    fut = executor.submit(run_single, next_idx, logs_dir)
                    futures[fut] = next_idx
                    next_idx += 1

        else:
            futures = {executor.submit(run_single, i, logs_dir): i for i in range(1, total + 1)}
            for fut in as_completed(futures):
                if stop:
                    break
                run_id = futures[fut]
                _, mets, tries = fut.result()
                results.append({"Exec": run_id, **mets, "retries": tries})
                elapsed = time.time() - start
                print_progress(run_id, total, mets["precision@K"], mets["recall@K"], elapsed)
                if mets["precision@K"] > best["precision@K"]:
                    best = {"Exec": run_id, **mets}

    finally:
        executor.shutdown(wait=False, cancel_futures=True)
        print()

    # compute stability
    retries = [r["retries"] for r in results]
    stability = {
        "avg_retries": sum(retries) / len(retries) if retries else 0.0,
        "max_retries": max(retries) if retries else 0,
        "with_retry": sum(1 for t in retries if t > 1),
        "failed": sum(1 for t in retries if t == MAX_RETRIES),
    }

    final = {
        "best": best,
        "elapsed_time": time.time() - start,
        "results_count": len(results),
        "stability": stability,
        "results": results,
    }
    metrics_path = os.path.join(base, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    logger.info(f"Métricas salvas em '{metrics_path}'")

    if not args.indefinite and best["Exec"] and best["precision@K"] > global_best:
        save_best(best)

    logger.info(f"Testbench concluído em {time.time() - start:.1f}s")


if __name__ == "__main__":
    main()
