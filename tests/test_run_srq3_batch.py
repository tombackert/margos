from pathlib import Path

from experiments import run_srq3_batch


def test_main_requires_auc_match_for_pass(monkeypatch, tmp_path, capsys) -> None:
    """SRQ3 batch pass/fail requires both the comparator pass and AUC tolerance."""
    reference_dir = tmp_path / "reference"
    reference_dir.mkdir()
    csv_path = tmp_path / "comparison_results.csv"

    monkeypatch.setattr(
        run_srq3_batch,
        "CSV_PATH",
        csv_path,
    )
    monkeypatch.setattr(
        run_srq3_batch,
        "get_run_stats",
        lambda run_dir: (-80.0, -445.0) if Path(run_dir) == reference_dir else (-80.0, -460.0),
    )
    monkeypatch.setattr(run_srq3_batch, "get_config_hash", lambda run_dir: "abc123")
    monkeypatch.setattr(
        run_srq3_batch,
        "run_experiment",
        lambda config_path: (str(tmp_path / "run-1"), None),
    )
    monkeypatch.setattr(
        run_srq3_batch,
        "compare_runs",
        lambda output_dir, ref_dir: {
            "final_reward_deviation": 0.0,
            "auc_deviation": 0.02,
            "passed": True,
            "auc_match": False,
            "config_hash_match": True,
            "config_integrity_match": True,
        },
    )
    monkeypatch.setattr(
        "sys.argv",
        ["run_srq3_batch.py", "--reference", str(reference_dir), "--n", "1"],
    )

    run_srq3_batch.main()

    output = capsys.readouterr().out
    assert "[FAIL]" in output
    assert "SRQ3 Results: 0/1 passed (0.0%)" in output
    csv_rows = csv_path.read_text()
    assert "FAIL" in csv_rows
