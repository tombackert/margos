# Backlog

# Open


# Done
- ~~Show real learning behavior over a long run -> convergence on reward curve into positiv.~~
- ~~Integrate the tensorboard logging into the cli~~
- ~~Remove the 4 or 2 iters overhead in every run~~
- ~~Remove/bundle the ray output, it is not pleasing~~
- ~~TB process was killed immediately after training ended, now killed after user enter~~

## Completed — SRQ2: Efficiency

- [x] SRQ2: Set up screen recording (QuickTime or equivalent)
- [x] SRQ2: Run 10 interleaved trials (Manual, Platform, Manual, Platform...) per protocol order
- [x] SRQ2: For each trial: record screen, time steps, fill `timing_data.csv` and `step_logs.csv`
- [x] SRQ2: Compute time/step reductions, fill `analysis_summary.md`

**Result:** H2 supported — 78.2% time reduction (87s → 19s), 75.0% step reduction (8 → 2), both ≥50%.

## Completed — SRQ3: Reproducibility

- [x] SRQ3: Run reference experiment: `platform run aggregation_srq3` (~6 min)
- [x] SRQ3: Record reference metrics in `docs/experiments/evidence/SRQ3/reference_run.md` (SRQ3 Batch section)
- [x] SRQ3: Run N=20 batch: `python experiments/run_srq3_batch.py --reference results/<ref_id>` (~2 hours)
- [x] SRQ3: Run unit tests, save output: `pytest tests/test_seeds.py -v > docs/experiments/evidence/SRQ3/unit_tests_output.txt`
- [x] SRQ3: Compute Reproduce-Success-Rate and variance, fill `analysis_summary.md`

**Platform Commit:** `06eb747` — all platform and experiment setup changes frozen at this state.
This is the exact platform version used for all SRQ data collection.

## Completed — Feasibility + Training Demo

- [x] Feasibility check: 300-iteration `aggregation_v1` run confirms ~85 min/run; created `aggregation_srq3.yaml` (10 iters, ~6 min/run) for batch
- [x] Real learning behavior demonstrated: -53.6 → -19.1 reward over 300 iterations (68.7% improvement), still converging
- [x] Reproducibility confirmed pre-batch: two seed=42 runs are bit-for-bit identical (max diff = 0.0 across 300 iterations)

## Completed — SRQ5: Collaboration

- [x] SRQ5: Prepare shareable experiment: `platform export <aggregation_v1_ref_id>`
- [x] SRQ5: Run 20 interleaved trials (10 manual + 10 platform)
- [x] SRQ5: For each platform trial: audit bundle completeness → fill `bundle_audits.csv`
- [x] SRQ5: For each trial: document environment comparison → fill `env_comparisons.csv`
- [x] SRQ5: Fill `trial_data.csv` (20 rows) with timing/steps/success
- [x] SRQ5: Compute Handoff-Success-Rate and time reductions, fill `analysis_summary.md`

**Result:** H5 partially supported. SRQ5 evaluation is complete: Steps-to-Share fell by 87.5%, Time-to-Share by 65.3%, and Time-to-Reproduce by 23.4%, while Handoff-Success-Rate remained 100% in both conditions. Time-to-First-Run increased by 59.7% in the platform condition because import overhead outweighed the direct file-copy path in the prepared-collaborator setup.

## Completed — SRQ4: Usability

- [x] SRQ4 (Part 1): Fill `heuristic_audit.md` 35-criteria checklist against live platform; compute Heuristic-Compliance-Rate
- [x] SRQ4 (Part 2): Fill `klm_analysis.md` for 7 tasks (baseline + platform); compute KLM-Reduction
- [x] SRQ4: Fill `analysis_summary.md` with M4.4–M4.6 results

**Result:** H4 supported — 85.7% heuristic compliance (30/35), 56.9% KLM reduction, both ≥ thresholds. Scope: analytical methods only (heuristic audit + KLM); empirical task trials excluded due to self-as-evaluator invalidity.

## Completed — Experiment Setup (Phase 1)

- [x] Create `experiments/configs/aggregation_v1.yaml` (100 iterations, seed 42)
- [x] Update Protocol-SRQ2: `platform report` → `platform compare`
- [x] Update Protocol-SRQ3: `platform report exp_XXX --reference results/reference/` → `platform compare exp_XXX results/reference/`
- [x] Update Protocol-SRQ5: `platform run --verify-reference` → `platform run` + `platform compare` (two steps)
- [x] Create evidence directory scaffold (`docs/experiments/evidence/SRQ2-5/` with CSV/MD templates)
- [x] Create `docs/experiments/docker/Dockerfile.researcher_b`

## Completed

- [x] Use same layout/list-framing for experiment list everywhere (use platform show style as standard)
- [x] Report command does not serve any SRQ. What we want fto satisf the SRQs, is the compare experiments function. We should therefore get rid of the report command and the redundant option functions "reference" and "compare" and should instead have compare as native command. Should work the same as "platform report --compare" works right now
- [x] When listing available configurations for any command, e.g. configs, exp_to_export/import, etc, they should be always sorted by date (most recent last)

## Completed in feature/backlog-fixes (Round 4)

- [x] Removed non-functional autocomplete - Deleted autocomplete functions, relying on existing list selection
- [x] Added short options to all CLI commands: `-c` (config-dir), `-i` (imported-dir), `-r` (reference), `-d` (results-dir), `-o` (output), `-b` (bundles-dir)
- [x] TensorBoard enabled by default - Changed `tensorboard: bool = True` in schema, removed `--tensorboard` CLI flag
- [x] Cleaned up training script - Moved Ray logging utilities to `marl_platform/utils/ray_logging.py`, simplified `aggregation.py` to pure training logic

## Completed in feature/sprint3-analysis-export (Round 3)

- [x] Removed --install-completion flag (too slow) - set `add_completion=False` in Typer app
- [x] Fixed repro table alignment - Deviation column now uses `:9.2%` format for proper alignment
- [x] Fixed TensorBoard not working - training script now uses callbacks from orchestrator via `CombinedCallbacks` wrapper

## Completed in feature/backlog-fixes (Round 2)

- [x] Autocomplete on exp names - Added tab completion via Typer's autocompletion feature (use Tab to complete experiment names)
- [x] Reproducibility comparison has clear table format: "| Metric | Run | Reference | Deviation | Match |"
- [x] Exit option in choose-mode: Enter '0' or 'q' to cancel and exit selection
- [x] Reference experiment selection: Use `platform report --compare` for interactive reference selection
- [x] Imported vs user-created experiments clearly separated in selection with [yellow](imported)[/yellow] labels and grouped sections
- [x] TensorBoard shows clear link: Prints instructions with `tensorboard --logdir <path>` and `http://localhost:6006`

## Completed in feature/backlog-fixes (Round 1)

- [x] Show usage explainer as: "Usage: platform [run | report | export | import]"
- [x] We need autocomplete on experiment filenames or a faster way of choosing target file (currently typing date-strings in filenames) -> Added scrollable list selection when no argument provided
- [x] Need command platform show config/experiments/results -> Added `platform show [configs|results|imported|bundles|all]`
- [x] Report shows only derivation in percentage but user is not shown actual data comparison -> Now shows actual values alongside deviation
- [x] Currently it is not possible to run an imported experiment directly (you first have to copy it into config dir...) -> Added `--imported-dir` option and automatic detection
- [x] Report comparison with an imported experiment is not simple as of now (you first have to copy results and stuff) -> Report now automatically checks imported directory
- [x] Progress bar is still mock for report, import, export -> Replaced with real progress bars tracking actual operations
- [x] Tensorboard logging (already integrated through ray i think, but we currently suppress it) because on long runs you need to be able to track training progress on all parameters -> Added `--tensorboard` flag to run command and `tensorboard: true` config option
