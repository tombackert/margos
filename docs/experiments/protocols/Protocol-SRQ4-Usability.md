# Protocol-SRQ4-Usability

## Header

| Field            | Value                                                                                                                                                                                                                                                                                                      |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Protocol ID      | P-SRQ4                                                                                                                                                                                                                                                                                                     |
| SRQ Reference    | SRQ4: To what extent does the platform's design comply with established usability heuristics and reduce predicted interaction complexity?                                                                                                                                                                  |
| Hypothesis       | H4: The platform demonstrates strong compliance with established usability heuristics (Heuristic-Compliance-Rate ≥80%), including learnability-related criteria (H6, H10) and error-tolerance criteria (H5, H9), and significant reduction in predicted interaction time (KLM-Reduction ≥50% vs baseline). |
| Success Criteria | ≥80% heuristic compliance (28/35 criteria), ≥50% KLM reduction                                                                                                                                                                                                                                             |
| Sample Size      | 35 heuristic criteria (1 audit session) + 7 KLM task analyses (analytical)                                                                                                                                                                                                                                 |
| Dependencies     | Platform implementation complete                                                                                                                                                                                                                                                                           |

---

## Prerequisites

### Required Artifacts
- [x] Platform CLI operational (all commands)
- [x] Platform documentation/help system
- [x] Test experiment configs prepared

### Environment Setup
- [x] Platform installed and accessible
- [x] Documentation accessible

### Pre-Execution Checklist
- [x] 35-criteria heuristic checklist prepared
- [x] KLM operator definitions reviewed
- [x] SRQ2 manual workflow steps documented (source for KLM baseline)

---

## Definitions

### Key Terms

| Term                          | Definition                                                            |
| ----------------------------- | --------------------------------------------------------------------- |
| Heuristic-Compliance-Rate     | Criteria met / 35 × 100%                                              |
| KLM-Predicted-Time            | Predicted task time using Keystroke-Level Model                       |
| KLM-Reduction                 | (Baseline_KLM - Platform_KLM) / Baseline_KLM × 100%                   |

### KLM Operator Definitions

Source: Card, Moran, Newell (1983). *The Psychology of Human-Computer Interaction*.

| Operator        | Symbol | Time (sec) | Description                        |
| --------------- | ------ | ---------- | ---------------------------------- |
| Keystroke       | K      | 0.20       | Single key press (average typist)  |
| Point           | P      | 1.10       | Mouse movement to target           |
| Button          | B      | 0.10       | Mouse button click                 |
| Homing          | H      | 0.40       | Hand movement (keyboard <-> mouse) |
| Mental          | M      | 1.35       | Mental preparation                 |
| System Response | R(t)   | t          | Wait for system (variable)         |

---

## Procedure

### Part 1: Heuristic Compliance Audit

Evaluate platform against Nielsen's 10 heuristics using the 35-criteria checklist below.

#### H1: Visibility of System Status

| #   | Criterion                                     | Present? | Evidence                                                                                                                                               |
| --- | --------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1.1 | Progress indicator for training runs          | Y        | RLlib prints iteration-by-iteration output during training; "Training Complete" Rich table printed on completion; TensorBoard link shown automatically |
| 1.2 | Feedback after command execution              | Y        | `run`: Rich summary table with reward/AUC/hash/output; `export`: "Bundle created: {path}"; `import`: "Imported to: {path}" + fingerprint table         |
| 1.3 | Current state visible (running/stopped/error) | Y        | Start: "Running experiment: {name}" echoed; end: "Training Complete" table; error: display_error() format with "Error: ..."                            |
| 1.4 | Resource usage visible (if applicable)        | N        | No CPU/GPU/memory metrics displayed in CLI output                                                                                                      |

#### H2: Match Between System and Real World

| #   | Criterion                                           | Present? | Evidence                                                                                                                |
| --- | --------------------------------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------- |
| 2.1 | Uses MARL/Swarm domain terminology                  | Y        | Config schema uses `experiment`, `scenario`, `training`, `output` — maps directly to MARL workflow concepts             |
| 2.2 | Follows conventions of similar tools (RLlib, ARGoS) | Y        | YAML config format (like RLlib); `platform run <name>` pattern mirrors `pytest <test>`, `docker run <image>`            |
| 2.3 | Logical ordering of operations                      | Y        | CLI commands follow natural research lifecycle: run → compare → export → import; `platform show` surfaces current state |

#### H3: User Control and Freedom

| #   | Criterion                             | Present? | Evidence                                                                                                     |
| --- | ------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------ |
| 3.1 | Cancel running operations             | Y        | Ctrl+C terminates any running command via standard Unix SIGINT; no data corruption (results dir timestamped) |
| 3.2 | Undo/revert config changes            | N        | No undo functionality in CLI; config files must be manually reverted                                         |
| 3.3 | Exit from any state without data loss | Y        | All interactive menus accept 'q'/'0'/'quit' to cancel (cli.py:113,155); exits cleanly without side effects   |

#### H4: Consistency and Standards

| #   | Criterion                     | Present? | Evidence                                                                                                                                  |
| --- | ----------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 4.1 | Consistent command syntax     | Y        | All commands follow `platform <verb> [name]` pattern; optional `--flag value` overrides consistent across commands                        |
| 4.2 | Consistent config file format | Y        | All experiments use same YAML schema: `experiment / scenario / training / output` keys                                                    |
| 4.3 | Consistent naming conventions | Y        | snake_case config keys; `exp_YYYYMMDD-HHMMss` output dir naming; short flags `-c/-d/-b/-i` consistent                                     |
| 4.4 | Consistent output formatting  | Y        | Rich tables throughout (Training Complete, Comparison, Fingerprint, List tables); error format always "Error: … Fix: …" (errors.py:76-83) |

#### H5: Error Prevention

| #   | Criterion                              | Present? | Evidence                                                                                                                                                       |
| --- | -------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 5.1 | Config validation before run           | Y        | `validate_config()` called in orchestrator before training; `ConfigNotFoundError` raised if file missing (errors.py:19-27)                                     |
| 5.2 | Confirmation for destructive actions   | Y        | No irreversible actions exposed; output dirs use timestamps (`exp_YYYYMMDD-HHMMss`) preventing overwrites; no delete commands in CLI                           |
| 5.3 | Default values for optional parameters | Y        | `--config-dir` → `experiments/configs`; `--results-dir` → `results`; `--output` → `bundles/<name>.zip`; `--bundles-dir` → `bundles` (cli.py:264-265, 435, 487) |
| 5.4 | Path/file existence checks             | Y        | `ConfigNotFoundError`, `ExperimentNotFoundError`, `BundleNotFoundError` each check path existence and report it (errors.py:19-49)                              |

#### H6: Recognition Rather Than Recall

| #   | Criterion                          | Present? | Evidence                                                                                                |
| --- | ---------------------------------- | -------- | ------------------------------------------------------------------------------------------------------- |
| 6.1 | Help/usage available for commands  | Y        | `platform --help` and `platform <cmd> --help` available via typer for all 5 commands                    |
| 6.2 | Available options visible          | Y        | `--help` shows all flags; interactive menus enumerate all available experiments/configs/bundles by name |
| 6.3 | Recent commands/configs accessible | N        | No command history or recent-files feature implemented                                                  |

#### H7: Flexibility and Efficiency of Use

| #   | Criterion                       | Present? | Evidence                                                                                                                                                |
| --- | ------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 7.1 | Shortcuts for common operations | Y        | `p` alias registered with 5 sub-aliases: `p r` → run, `p s` → show, `p c` → compare, `p e` → export, `p i` → import; `p --help` confirms all registered |
| 7.2 | Configurable defaults           | Y        | Directory defaults overridable via `--config-dir`, `--results-dir`, `--bundles-dir`, `--imported-dir` on all relevant commands                          |
| 7.3 | Batch operations supported      | N        | No batch run or multi-experiment execution command                                                                                                      |

#### H8: Aesthetic and Minimalist Design

| #   | Criterion                                 | Present? | Evidence                                                                                                                        |
| --- | ----------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------- |
| 8.1 | Output contains only relevant information | Y        | Training summary shows 6 key metrics only (reward, AUC, duration, iterations, hash, output); no debug output unless `--verbose` |
| 8.2 | No redundant prompts/confirmations        | Y        | Commands execute directly; interactive selection only appears when required argument is missing; no extra confirmations         |
| 8.3 | Clear visual hierarchy in output          | Y        | Rich tables use `bold` headers, `dim` metric labels, right-justified values; consistent column structure (cli.py:192-205)       |

#### H9: Help Users Recognize, Diagnose, and Recover from Errors

| #   | Criterion                           | Present? | Evidence                                                                                                                              |
| --- | ----------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| 9.1 | Error messages in plain language    | Y        | "Config file not found", "Experiment not found", "Bundle not found" — plain English, no technical jargon (errors.py:22,32,42)         |
| 9.2 | Error messages indicate the problem | Y        | Context dict shows `Path:` with exact problematic path in every error type (errors.py:24,33,44)                                       |
| 9.3 | Error messages suggest solution     | Y        | All errors include `fix=` with actionable suggestion, e.g. "Create the config file or check the experiment name" (errors.py:26,35,46) |
| 9.4 | Error codes for reference           | N        | Errors have no numeric/symbolic codes — only message + context + fix                                                                  |

#### H10: Help and Documentation

| #    | Criterion                   | Present? | Evidence                                                                                             |
| ---- | --------------------------- | -------- | ---------------------------------------------------------------------------------------------------- |
| 10.1 | Built-in help command       | Y        | `platform --help` and `platform <cmd> --help` via typer; lists all commands and flags                |
| 10.2 | Examples provided           | Y        | `compare`, `export`, `import`, `show` all have Examples sections in docstrings displayed by `--help` |
| 10.3 | Documentation accessible    | Y        | `docs/` folder contains ResearchPlan.md, DesignBrainstorm.md, experiment protocols                   |
| 10.4 | Quick-start guide available | Y        | README.md at repo root; covers install, all 5 commands with short/long aliases and examples          |

### Part 2: GOMS/KLM Analysis

For each task, document operator sequence for both baseline and platform. Baseline operator sequences must be derived from the pre-documented SRQ2 manual workflow steps - do not redefine them independently.

#### Task List

| ID  | Task                     | Description                                            | Complexity |
| --- | ------------------------ | ------------------------------------------------------ | ---------- |
| T1  | Configure new experiment | Create config for a basic MARL experiment from scratch | Medium     |
| T2  | Modify parameters        | Change hyperparameters in existing config and re-run   | Low        |
| T3  | Start training           | Initiate training run with configured experiment       | Low        |
| T4  | Monitor progress         | View training metrics and logs during run              | Low        |
| T5  | View results             | Access and interpret final training results            | Medium     |
| T6  | Export experiment        | Create shareable bundle of completed experiment        | Low        |
| T7  | Import and reproduce     | Import bundle on fresh environment and verify          | Medium     |

#### Task Breakdown Template

**Task: T1 - Configure new experiment**

**Task:** Configure a new MARL experiment by copying a template and setting 3 parameters: experiment name, seed, iterations. Both conditions configure the same parameters using VS Code (IDE + mouse).

**"Find+Edit" macro (VS Code Ctrl+F):** M + K(2) + K(n_search) + K(1) + K(1) + H + P + B + B + M + K(n_value) = 5.30 + 0.20×n_search + 0.20×n_value

**Baseline (VS Code, Python training script):**

| Step      | Action                                                                           | Operators               | Time (s)                          |
| --------- | -------------------------------------------------------------------------------- | ----------------------- | --------------------------------- |
| 1         | Mental: plan configuration                                                       | M                       | 1.35                              |
| 2         | Explorer: right-click template script → Copy                                     | H + P + B + P + B       | 0.40+1.10+0.10+1.10+0.10 = 2.80   |
| 3         | Right-click scripts/ folder → Paste                                              | P + B + P + B           | 1.10+0.10+1.10+0.10 = 2.40        |
| 4         | Press F2 to rename + type new name ("srq4_eval.py" + Enter)                      | K(2) + M + K(14)        | 0.40 + 1.35 + 2.80 = 4.55         |
| 5         | Double-click new file to open                                                    | P + B + B               | 1.10+0.10+0.10 = 1.30             |
| 6         | Find+Edit EXPERIMENT_NAME (search "EXPE"=4, value "srq4_eval"=9)                 | Find+Edit macro         | 5.30 + 0.80 + 1.80 = 7.90         |
| 7         | Find+Edit SEED (search "SEED"=4, value "42"=2)                                   | Find+Edit macro         | 5.30 + 0.80 + 0.40 = 6.50         |
| 8         | Find+Edit NUM_ITERATIONS (search "ITER"=4, value "10"=2)                         | Find+Edit macro         | 5.30 + 0.80 + 0.40 = 6.50         |
| 9         | Ctrl+S to save                                                                   | K(2)                    | 0.40                              |
| **Total** |                                                                                  |                         | **33.70 s**                       |

**Platform (VS Code, YAML config):**

| Step      | Action                                                                           | Operators               | Time (s)                          |
| --------- | -------------------------------------------------------------------------------- | ----------------------- | --------------------------------- |
| 1         | Mental: plan                                                                     | M                       | 1.35                              |
| 2         | Explorer: right-click template YAML → Copy                                       | H + P + B + P + B       | 2.80                              |
| 3         | Right-click configs/ folder → Paste                                              | P + B + P + B           | 2.40                              |
| 4         | Press F2 to rename + type new name ("srq4_eval.yaml" + Enter)                    | K(2) + M + K(14)        | 4.55                              |
| 5         | Double-click new file to open                                                    | P + B + B               | 1.30                              |
| 6         | Find+Edit name (search "name"=4, value "srq4_eval"=9)                            | Find+Edit macro         | 5.30 + 0.80 + 1.80 = 7.90         |
| 7         | Find+Edit seed (search "seed"=4, value "42"=2)                                   | Find+Edit macro         | 5.30 + 0.80 + 0.40 = 6.50         |
| 8         | Find+Edit iterations (search "iter"=4, value "10"=2)                             | Find+Edit macro         | 5.30 + 0.80 + 0.40 = 6.50         |
| 9         | Ctrl+S to save                                                                   | K(2)                    | 0.40                              |
| **Total** |                                                                                  |                         | **33.70 s**                       |

**KLM Calculation:**
- Baseline: 33.70 seconds
- Platform: 33.70 seconds
- Reduction: 0% (workflows structurally equivalent — Explorer file ops and Ctrl+F search are identical; YAML fields and Python constants use same-length 4-char search terms)%

---

## Data Collection

### Heuristic Compliance Summary

| Heuristic            | Criteria Count | Met    | Score     |
| -------------------- | -------------- | ------ | --------- |
| H1: Visibility       | 4              | 3      | 3/4       |
| H2: Real World Match | 3              | 3      | 3/3       |
| H3: User Control     | 3              | 2      | 2/3       |
| H4: Consistency      | 4              | 4      | 4/4       |
| H5: Error Prevention | 4              | 4      | 4/4       |
| H6: Recognition      | 3              | 2      | 2/3       |
| H7: Flexibility      | 3              | 2      | 2/3       |
| H8: Minimalist       | 3              | 3      | 3/3       |
| H9: Error Recovery   | 4              | 3      | 3/4       |
| H10: Help/Docs       | 4              | 4      | 4/4       |
| **Total**            | **35**         | **30** | **30/35** |

### KLM Comparison Summary

*Times exclude system response R(t) as per KLM convention (compute wait time is equal in both conditions).*

| Task                 | Baseline (sec) | Platform (sec) | Reduction (%) |
| -------------------- | -------------- | -------------- | ------------- |
| T1: Configure        | 33.70          | 33.70          | 0%            |
| T2: Modify           | 9.95           | 9.95           | 0%            |
| T3: Train            | 13.15          | 5.50           | 58%           |
| T4: Monitor          | 21.05          | 2.55           | 88%           |
| T5: Results          | 22.00          | 3.95           | 82%           |
| T6: Export           | 14.90          | 5.90           | 60%           |
| T7: Import/Reproduce | 54.50          | 11.40          | 79%           |
| **Weighted Total**   | **169.25**     | **72.95**      | **56.9%**     |

---

## Analysis

### Metrics Summary (M4.4-M4.6)

| Metric                              | Value          | Target       | Met? |
| ----------------------------------- | -------------- | ------------ | ---- |
| M4.4: Heuristic-Compliance-Rate     | 30/35 (85.7%)  | ≥80% (28/35) | Yes  |
| M4.5: KLM-Predicted-Time (platform) | 10.42 s/task   | —            | —    |
| M4.6: KLM-Reduction                 | 56.9%          | ≥50%         | Yes  |

### Interpretation Guidelines

| Outcome                                          | Interpretation         |
| ------------------------------------------------ | ---------------------- |
| ≥80% heuristic compliance AND ≥50% KLM reduction | H4 supported           |
| ≥80% heuristic OR ≥50% KLM (not both)            | H4 partially supported |
| <80% heuristic AND <50% KLM                      | H4 not supported       |

---

## Evidence Checklist

- [x] Heuristic audit complete with evidence per criterion
- [x] KLM operator analysis complete for all 7 tasks

### Required Evidence Files

| File                  | Description                         |
| --------------------- | ----------------------------------- |
| `heuristic_audit.md`  | Complete checklist with evidence    |
| `klm_analysis.md`     | Operator breakdown and calculations |
| `analysis_summary.md` | Computed statistics                 |

---

## Limitations

| Limitation                                                                                                            | Mitigation                                                                                    |
| --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Single evaluator for heuristic audit (developer evaluating own design; Nielsen recommends 3-5 independent evaluators) | Use structured checklist; require evidence citation per criterion; state explicitly in thesis |
| KLM assumes error-free execution                                                                                      | Conservative operator estimates; noted as model limitation                                    |
| H6/H10 measure design properties indicative of learnability, not behavioral learnability directly                     | Scoped as design-property proxies; bridged to behavioral interpretation in Discussion chapter |
| Both methods (KLM + heuristics) are analytical; zero behavioral data in SRQ4                                          | Consistent with empiricism-first principle; stated as limitation in thesis                    |

---

## Comparison: SRQ4 vs SRQ2

| Aspect      | SRQ2: Efficiency                               | SRQ4: Usability                                                                                |
| ----------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Question    | How much does the platform reduce time/effort? | Does the platform's design comply with usability heuristics and reduce interaction complexity? |
| Perspective | Experienced user (knows system)                | Design-property analysis (analytical + structured audit)                                       |
| Focus       | Throughput, step reduction                     | Heuristic compliance, interaction complexity (KLM)                                             |
| Metrics     | Time-to-Complete, Steps-to-Complete            | Heuristic-Compliance-Rate, KLM-Predicted-Time, KLM-Reduction                                   |

---

## References

- `docs/SRQ4UsabilityBrainstorm.md` - Full rationale and decisions
- `docs/ResearchPlan.md` - SRQ4, H4, E4 definitions
- Card, Moran, Newell (1983). *The Psychology of Human-Computer Interaction*. Lawrence Erlbaum Associates.
- Nielsen, J. (1994). *10 Usability Heuristics for User Interface Design*.
