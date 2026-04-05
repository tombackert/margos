# SRQ4 KLM Analysis

## Operator Definitions

Source: Card, Moran, Newell (1983). *The Psychology of Human-Computer Interaction*.

| Operator        | Symbol   | Time (sec)   | Description                       |
| --------------- | -------- | ------------ | --------------------------------- |
| Keystroke       | K        | 0.20         | Single key press (average typist) |
| Point           | P        | 1.10         | Mouse movement to target          |
| Button          | B        | 0.10         | Mouse button click                |
| Homing          | H        | 0.40         | Hand movement keyboard ↔ mouse    |
| Mental          | M        | 1.35         | Mental preparation / decision     |
| System Response | R(t)     | t            | Wait for system (variable)        |

**Convention:** K(n) = n × 0.20 s. M placed before each distinct decision/action. R(t) excluded from task totals (compute wait time, same in both conditions). H/P/B used for IDE mouse interactions (T1, T2): H = hand to mouse, P = point to target, B = button click.

**Baseline:** SRQ2 Condition A — manual workflow using fragmented tools (training Python scripts, tensorboard CLI, zip, unzip). Assumes trained user who knows the tool structure.

**Platform:** Assumes trained user who knows `platform <cmd>` syntax and YAML schema.

---

## T1: Configure New Experiment

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

**KLM Totals:**
- Baseline: **33.70 s**
- Platform: **33.70 s**
- **Reduction: 0%** (workflows structurally equivalent — Explorer file ops and Ctrl+F search are identical; YAML fields and Python constants use same-length 4-char search terms)

> Note: T1 shows 0% reduction by design. Both conditions configure the same 3 parameters in the same IDE. The platform's value for configuration tasks is structural (validation, reproducibility), not interaction speed.

---

## T2: Modify Parameters

**Task:** Change one hyperparameter (iterations) in an existing config and save. Both conditions use VS Code (IDE + mouse).

**Baseline (VS Code, Python training script):**

| Step      | Action                                                          | Operators         | Time (s)   |
| --------- | --------------------------------------------------------------- | ----------------- | ---------- |
| 1         | Mental: plan                                                    | M                 | 1.35       |
| 2         | Double-click script in Explorer to open                         | H + P + B + B     | 1.70       |
| 3         | Find+Edit NUM_ITERATIONS (search "ITER"=4, value "10"=2)        | Find+Edit macro   | 6.50       |
| 4         | Ctrl+S to save                                                  | K(2)              | 0.40       |
| **Total** |                                                                 |                   | **9.95 s** |

**Platform (VS Code, YAML config):**

| Step      | Action                                                          | Operators         | Time (s)   |
| --------- | --------------------------------------------------------------- | ----------------- | ---------- |
| 1         | Mental: plan                                                    | M                 | 1.35       |
| 2         | Double-click config YAML in Explorer to open                    | H + P + B + B     | 1.70       |
| 3         | Find+Edit iterations (search "iter"=4, value "10"=2)            | Find+Edit macro   | 6.50       |
| 4         | Ctrl+S to save                                                  | K(2)              | 0.40       |
| **Total** |                                                                 |                   | **9.95 s** |

**KLM Totals:**
- Baseline: **9.95 s**
- Platform: **9.95 s**
- **Reduction: 0%** (identical tool, identical parameter, same search term length)

---

## T3: Start Training

**Task:** Initiate a training run with the configured experiment.

**Baseline (direct Python invocation):**

| Step      | Action                                                                                    | Operators   | Time (s)             |
| --------- | ----------------------------------------------------------------------------------------- | ----------- | -------------------- |
| 1         | Type run command: `PYTHONPATH=src python scripts/ray_footbot_aggregation_srq2.py` + Enter | M + K(59)   | 1.35 + 11.80 = 13.15 |
| **Total** |                                                                                           |             | **13.15 s**          |

**Platform (interactive selection):**

| Step      | Action                                              | Operators        | Time (s)            |
| --------- | --------------------------------------------------- | ---------------- | ------------------- |
| 1         | Type: `platform run` + Enter                        | M + K(13)        | 1.35 + 2.60 = 3.95  |
| 2         | Select experiment from list: type "1" + Enter       | M + K(1)         | 1.35 + 0.20 = 1.55  |
| **Total** |                                                     |                  | **5.50 s**          |

*(R(~0.5) for list display excluded as system response)*

**KLM Totals:**
- Baseline: **13.15 s**
- Platform: **5.50 s**
- **Reduction: 58.1%**

---

## T4: Monitor Progress

**Task:** View training metrics and logs during an active run.

**Baseline (launch TensorBoard manually):**

| Step      | Action                                                                                            | Operators       | Time (s)                         |
| --------- | ------------------------------------------------------------------------------------------------- | --------------- | -------------------------------- |
| 1         | Find results dir: `ls results/` + Enter                                                           | M + K(9) + R(1) | 1.35 + 1.80 + 1.00 = 4.15        |
| 2         | Launch TensorBoard: `tensorboard --logdir results/srq4_eval_20240115-120000/tensorboard/` + Enter | M + K(68)       | 1.35 + 13.60 = 14.95             |
| 3         | Open browser to TensorBoard URL                                                                   | M + H + P + B   | 1.35 + 0.40 + 1.10 + 0.10 = 2.95 |
| **Total** |                                                                                                   |                 | **22.05 s**                      |

Without R: 4.15*(no R1)=3.15 + 14.95 + 2.95 = **21.05 s**

**Platform (follow auto-printed TensorBoard link):**

| Step      | Action                                                       | Operators   | Time (s)                  |
| --------- | ------------------------------------------------------------ | ----------- | ------------------------- |
| 1         | Click TensorBoard link printed by `platform run` in terminal | M + P + B   | 1.35 + 1.10 + 0.10 = 2.55 |
| **Total** |                                                              |             | **2.55 s**                |

**KLM Totals:**
- Baseline: **21.05 s**
- Platform: **2.55 s**
- **Reduction: 87.9%**

---

## T5: View Results

**Task:** Access and interpret the final training results after a completed run.

**Baseline (navigate TensorBoard + manual inspection):**

| Step      | Action                                                                | Operators         | Time (s)                         |
| --------- | --------------------------------------------------------------------- | ----------------- | -------------------------------- |
| 1         | Find results dir: `ls results/` + Enter                               | M + K(9) + R(1)   | 1.35 + 1.80 + 1.00 = 4.15        |
| 2         | Open TensorBoard (if not running): `tensorboard --logdir results/...` | M + K(65) + R(5)  | 1.35 + 13.00 + 5.00 = 19.35      |
| 3         | Navigate to episode_reward_mean in UI                                 | M + H + P + B × 3 | 1.35 + 0.40 + 1.10 + 0.30 = 3.15 |
| 4         | Read and note key values                                              | M                 | 1.35                             |
| **Total** |                                                                       |                   | **28.00 s**                      |

Without R: 4.15*(no R1)=3.15 + 19.35*(no R5)=14.35 + 3.15 + 1.35 = **22.00 s**

**Platform:**

| Step      | Action                        | Operators        | Time (s)                  |
| --------- | ----------------------------- | ---------------- | ------------------------- |
| 1         | Type: `platform show` + Enter | M + K(13) + R(1) | 1.35 + 2.60 + 1.00 = 4.95 |
| **Total** |                               |                  | **4.95 s**                |

Without R: 1.35 + 2.60 = **3.95 s**

**KLM Totals:**
- Baseline: **22.00 s**
- Platform: **3.95 s**
- **Reduction: 82.0%**

---

## T6: Export Experiment

**Task:** Create a shareable bundle of a completed experiment.

**Baseline (manual zip):**

| Step      | Action                                                                            | Operators        | Time (s)                    |
| --------- | --------------------------------------------------------------------------------- | ---------------- | --------------------------- |
| 1         | Find experiment dir: `ls results/` + Enter                                        | M + K(9) + R(1)  | 1.35 + 1.80 + 1.00 = 4.15   |
| 2         | Zip experiment: `zip -r srq4_eval.zip results/srq4_eval_20240115-120000/` + Enter | M + K(52) + R(3) | 1.35 + 10.40 + 3.00 = 14.75 |
| **Total** |                                                                                   |                  | **18.90 s**                 |

Without R: 4.15*(no R1)=3.15 + 14.75*(no R3)=11.75 = **14.90 s**

**Platform (interactive selection):**

| Step      | Action                                        | Operators        | Time (s)                  |
| --------- | --------------------------------------------- | ---------------- | ------------------------- |
| 1         | Type: `platform export` + Enter               | M + K(15) + R(1) | 1.35 + 3.00 + 1.00 = 5.35 |
| 2         | Select experiment from list: type "1" + Enter | M + K(1) + R(3)  | 1.35 + 0.20 + 3.00 = 4.55 |
| **Total** |                                               |                  | **9.90 s**                |

Without R: 5.35*(no R1)=4.35 + 4.55*(no R3)=1.55 = **5.90 s**

**KLM Totals:**
- Baseline: **14.90 s**
- Platform: **5.90 s**
- **Reduction: 60.4%**

---

## T7: Import and Reproduce

**Task:** Import an experiment bundle on a fresh environment and verify it reproduces.

**Baseline (manual unzip + reconfigure + re-run):**

| Step      | Action                                                                                 | Operators        | Time (s)                    |
| --------- | -------------------------------------------------------------------------------------- | ---------------- | --------------------------- |
| 1         | Find bundle: `ls bundles/` + Enter                                                     | M + K(9) + R(1)  | 1.35 + 1.80 + 1.00 = 4.15   |
| 2         | Unzip: `unzip bundles/srq4_eval.zip -d experiments/reproduced/` + Enter                | M + K(50) + R(5) | 1.35 + 10.00 + 5.00 = 16.35 |
| 3         | Open training script to update paths                                                   | M + K(45) + R(2) | 1.35 + 9.00 + 2.00 = 12.35  |
| 4         | Navigate to path constants: Ctrl+W + "PATH"                                            | M + K(8) + R(1)  | 1.35 + 1.60 + 1.00 = 3.95   |
| 5         | Edit paths to match new location (~40 chars)                                           | M + K(40)        | 1.35 + 8.00 = 9.35          |
| 6         | Save: Ctrl+X, Y, Enter                                                                 | K(3)             | 0.60                        |
| 7         | Re-run: `PYTHONPATH=src python experiments/reproduced/srq4_eval/training/srq4_eval.py` | M + K(77)        | 1.35 + 15.40 = 16.75        |
| **Total** |                                                                                        |                  | **63.50 s**                 |

Without R: 4.15*(no R1)=3.15 + 16.35*(no R5)=11.35 + 12.35*(no R2)=10.35 + 3.95*(no R1)=2.95 + 9.35 + 0.60 + 16.75 = **54.50 s**

**Platform (interactive selection):**

| Step      | Action                                               | Operators        | Time (s)                   |
| --------- | ---------------------------------------------------- | ---------------- | -------------------------- |
| 1         | Type: `platform import` + Enter                      | M + K(15) + R(1) | 1.35 + 3.00 + 1.00 = 5.35  |
| 2         | Select bundle from list: type "1" + Enter            | M + K(1) + R(5)  | 1.35 + 0.20 + 5.00 = 6.55  |
| 3         | Run imported: `platform run` + Enter                 | M + K(13) + R(1) | 1.35 + 2.60 + 1.00 = 4.95  |
| 4         | Select imported experiment: type "1" + Enter         | M + K(1)         | 1.35 + 0.20 = 1.55         |
| **Total** |                                                      |                  | **18.40 s**                |

Without R: 5.35*(no R1)=4.35 + 6.55*(no R5)=1.55 + 4.95*(no R1)=3.95 + 1.55 = **11.40 s**

**KLM Totals:**
- Baseline: **54.50 s**
- Platform: **11.40 s**
- **Reduction: 79.1%**

---

## KLM Summary (M4.5, M4.6)

*Times below exclude system response R(t) as per KLM convention (compute wait time is equal in both conditions).*

| Task                 | Baseline (s) | Platform (s) | Reduction (%) | Speedup (x) |
| -------------------- | ------------ | ------------ | ------------- | ----------- |
| T1: Configure        | 33.70        | 33.70        | 0%            | 1.00x       |
| T2: Modify           | 9.95         | 9.95         | 0%            | 1.00x       |
| T3: Train            | 13.15        | 5.50         | 58%           | 2.39x       |
| T4: Monitor          | 21.05        | 2.55         | 88%           | 8.25x       |
| T5: Results          | 22.00        | 3.95         | 82%           | 5.57x       |
| T6: Export           | 14.90        | 5.90         | 60%           | 2.53x       |
| T7: Import/Reproduce | 54.50        | 11.40        | 79%           | 4.78x       |
| **Average**          | **24.18**    | **10.42**    | **52%**       | **2.32x**   |

**Weighted KLM-Reduction (M4.6):** (169.25 − 72.95) / 169.25 = **56.9%**

**Simple average of per-task reduction:** (0 + 0 + 58 + 88 + 82 + 60 + 79) / 7 = 367 / 7 = **52.4%**

**KLM-Predicted-Time (platform, M4.5):** mean 10.42 s per task

**Target:** ≥50% reduction

**Met?** YES — weighted reduction 56.9%; simple average 52.4%

---

## Interpretation

**Tasks T1 and T2 (Configure/Modify)** show 0% reduction. Both conditions use VS Code (IDE + mouse) and configure the same parameters (name, seed, iterations for T1; one parameter for T2). Explorer file operations and Ctrl+F search are identical regardless of file format (Python vs YAML). The platform's value for configuration tasks is structural — config validation, schema enforcement, reproducibility guarantees — not interaction speed.

**Tasks T3–T7** show large reductions (58–88%) because the platform replaces complex multi-step workflows with single short commands:
- T3: `platform run` replaces 59-char `PYTHONPATH=...` invocation
- T4: TensorBoard link printed automatically vs manual path discovery + launch
- T5: `platform show` replaces TensorBoard navigation + manual data extraction
- T6: Interactive selection replaces manual `ls` + `zip` with correct path
- T7: `platform import` + `platform run` replaces unzip + path editing + re-invocation

**Conclusion:** H4's KLM-Reduction criterion is met at 56.9% (weighted). T1/T2 near-zero reduction is expected and honest — the platform does not improve file-editing tasks. The 56.9% weighted reduction is driven entirely by T3–T7, where platform automation replaces fragmented multi-step manual workflows.
