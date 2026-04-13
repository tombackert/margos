"""SRQ3 batch runner: runs N reproducibility experiments and populates evidence files.

Usage:
    python experiments/run_srq3_batch.py --reference results/<ref_dir>
    python experiments/run_srq3_batch.py --reference results/<ref_dir> --n 20

The script:
1. Runs `platform run aggregation_srq3` N times (default 20)
2. Compares each run against the reference using compare_runs()
3. Appends rows to docs/experiments/evidence/SRQ3/comparison_results.csv
4. Prints per-run summary and final statistics
"""

import argparse
import csv
import signal
import sys
from pathlib import Path

# Add project root to path so we can import marl_platform
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from marl_platform.analysis.compare import compare_runs
from marl_platform.analysis.report import calculate_auc, read_metrics
from marl_platform.orchestrator import run_experiment

CONFIG_PATH = str(ROOT / "experiments" / "configs" / "aggregation_srq3.yaml")
CSV_PATH = ROOT / "docs" / "experiments" / "evidence" / "SRQ3" / "comparison_results.csv"
CSV_FIELDS = [
    "Run#",
    "Reward",
    "AUC",
    "Reward Deviation (%)",
    "AUC Deviation (%)",
    "Pass/Fail",
    "Config Hash Match",
    "Config Integrity Match",
]


def get_run_stats(run_dir: str) -> tuple[float, float]:
    """Return (final_reward, auc) for a completed run."""
    log_path = Path(run_dir) / "logs" / "metrics.jsonl"
    metrics = read_metrics(log_path)
    rewards = [m["episode_reward_mean"] for m in metrics if m.get("episode_reward_mean") is not None]
    final_reward = rewards[-1] if rewards else float("nan")
    auc = calculate_auc(metrics) if len(metrics) >= 2 else 0.0
    return final_reward, auc


def get_config_hash(run_dir: str) -> str:
    hash_path = Path(run_dir) / "config_hash.txt"
    return hash_path.read_text().strip() if hash_path.exists() else "N/A"


def reset_csv() -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()


def append_csv_row(row: dict) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description="SRQ3 batch reproducibility runner")
    parser.add_argument("--reference", required=True, help="Path to reference experiment directory")
    parser.add_argument("--n", type=int, default=20, help="Number of reproduction attempts (default: 20)")
    args = parser.parse_args()

    reference_dir = str(Path(args.reference).resolve())
    if not Path(reference_dir).exists():
        print(f"Error: Reference directory not found: {reference_dir}")
        sys.exit(1)

    ref_reward, ref_auc = get_run_stats(reference_dir)
    ref_hash = get_config_hash(reference_dir)
    print(f"Reference: {Path(reference_dir).name}")
    print(f"  Final reward: {ref_reward:.4f}")
    print(f"  AUC:          {ref_auc:.4f}")
    print(f"  Config hash:  {ref_hash[:12]}...")
    print(f"\nRunning {args.n} reproduction attempts...\n")

    reset_csv()

    pass_count = 0
    rewards = []

    for i in range(1, args.n + 1):
        print(f"[{i:2d}/{args.n}] Running aggregation_srq3...", end=" ", flush=True)

        try:
            output_dir, tb_process = run_experiment(CONFIG_PATH)
            if tb_process is not None and tb_process.poll() is None:
                tb_process.send_signal(signal.SIGTERM)
            run_reward, run_auc = get_run_stats(output_dir)
            comparison = compare_runs(output_dir, reference_dir)

            reward_dev_pct = comparison["final_reward_deviation"] * 100
            auc_dev_pct = comparison["auc_deviation"] * 100
            passed = comparison["repro_pass"]
            hash_match = comparison["config_hash_match"]
            integrity_match = comparison["config_integrity_match"]

            status = "PASS" if passed else "FAIL"
            if passed:
                pass_count += 1
            rewards.append(run_reward)

            print(f"reward={run_reward:.2f}  AUC={run_auc:.1f}  dev={reward_dev_pct:.2f}%  [{status}]")

            append_csv_row({
                "Run#": i,
                "Reward": f"{run_reward:.4f}",
                "AUC": f"{run_auc:.4f}",
                "Reward Deviation (%)": f"{reward_dev_pct:.4f}",
                "AUC Deviation (%)": f"{auc_dev_pct:.4f}",
                "Pass/Fail": status,
                "Config Hash Match": "Yes" if hash_match else "No",
                "Config Integrity Match": "Yes" if integrity_match else "No",
            })

        except Exception as e:
            print(f"ERROR: {e}")
            append_csv_row({
                "Run#": i,
                "Reward": "ERROR",
                "AUC": "ERROR",
                "Reward Deviation (%)": "ERROR",
                "AUC Deviation (%)": "ERROR",
                "Pass/Fail": "FAIL",
                "Config Hash Match": "No",
                "Config Integrity Match": "No",
            })

    # Summary statistics
    import statistics
    success_rate = pass_count / args.n * 100
    reward_std = statistics.stdev(rewards) if len(rewards) >= 2 else 0.0

    print(f"\n{'='*50}")
    print(f"SRQ3 Results: {pass_count}/{args.n} passed ({success_rate:.1f}%)")
    print(f"Reward std dev: {reward_std:.4f}")
    print(f"Threshold: ≥90% required")
    print(f"Result: {'✓ H3 SUPPORTED' if success_rate >= 90 else '✗ H3 NOT SUPPORTED'}")
    print(f"CSV: {CSV_PATH}")


if __name__ == "__main__":
    main()
