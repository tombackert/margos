# SRQ4 KLM Analysis

## Operator Definitions

Source: Card, Moran, Newell (1983). *The Psychology of Human-Computer Interaction*.

| Operator | Symbol | Time (sec) | Description |
|----------|--------|------------|-------------|
| Keystroke | K | 0.20 | Single key press (average typist) |
| Point | P | 1.10 | Mouse movement to target |
| Button | B | 0.10 | Mouse button click |
| Homing | H | 0.40 | Hand movement keyboard ↔ mouse |
| Mental | M | 1.35 | Mental preparation / decision |
| System Response | R(t) | t | Wait for system (variable) |

**Convention:** K(n) = n × 0.20 s. M placed before each distinct decision/action. R(t) excluded from task totals (compute wait time, same in both conditions).

**Baseline:** SRQ2 Condition A — manual workflow using fragmented tools (training Python scripts, tensorboard CLI, zip, unzip). Assumes trained user who knows the tool structure.

**Platform:** Assumes trained user who knows `platform <cmd>` syntax and YAML schema.

---

## T1: Configure New Experiment

**Task:** Configure a new MARL experiment (create config/setup for a named experiment from scratch).

**Baseline (copy training script + edit constants):**

| Step | Action | Operators | Time (s) |
|------|--------|-----------|----------|
| 1 | Mental: plan configuration | M | 1.35 |
| 2 | List training templates: `ls training/` + Enter | K(12) | 2.40 |
| 3 | Copy script: `cp training/aggregation.py training/srq4_eval.py` + Enter | M + K(51) | 1.35 + 10.20 = 11.55 |
| 4 | Open copy: `nano training/srq4_eval.py` + Enter | M + K(27) + R(2) | 1.35 + 5.40 + 2.00 = 8.75 |
| 5 | Navigate to constants section: Ctrl+W + "SEED" + Enter | M + K(8) + R(1) | 1.35 + 1.60 + 1.00 = 3.95 |
| 6 | Edit 5 config constants (~50 chars total) | M + K(50) | 1.35 + 10.00 = 11.35 |
| 7 | Save and exit: Ctrl+X, Y, Enter | K(3) | 0.60 |
| **Total** | | | **40.95 s** |

*(R(2) for editor open, R(1) for search excluded from total as compute time)*

Recalculated without R: 1.35 + 2.40 + 11.55 + 8.75*(no R2)=6.75 + 3.95*(no R1)=2.95 + 11.35 + 0.60 = **37.35 s**

**Platform (copy existing config + edit name):**

| Step | Action | Operators | Time (s) |
|------|--------|-----------|----------|
| 1 | Mental: plan | M | 1.35 |
| 2 | List configs: `platform show configs` + Enter | K(20) | 4.00 |
| 3 | Copy config: `cp experiments/configs/aggregation_smoke.yaml experiments/configs/srq4_eval.yaml` + Enter | M + K(81) | 1.35 + 16.20 = 17.55 |
| 4 | Open copy: `nano experiments/configs/srq4_eval.yaml` + Enter | M + K(45) + R(2) | 1.35 + 9.00 + 2.00 = 12.35 |
| 5 | Search for name: Ctrl+W + "name" + Enter | M + K(7) + R(1) | 1.35 + 1.40 + 1.00 = 3.75 |
| 6 | Update name value (~12 chars) | M + K(12) | 1.35 + 2.40 = 3.75 |
| 7 | Save and exit: Ctrl+X, Y, Enter | K(3) | 0.60 |
| **Total** | | | **43.35 s** |

Without R: 1.35 + 4.00 + 17.55 + 12.35*(no R2)=10.35 + 3.75*(no R1)=2.75 + 3.75 + 0.60 = **40.35 s**

**KLM Totals (excluding R):**
- Baseline: **37.35 s**
- Platform: **40.35 s**
- **Reduction: −8%** (platform marginally slower — longer file path; equivalent editing effort)

---

## T2: Modify Parameters

**Task:** Change one hyperparameter in an existing config and save.

**Baseline (edit constants in Python script):**

| Step | Action | Operators | Time (s) |
|------|--------|-----------|----------|
| 1 | Open script: `nano training/srq4_eval.py` + Enter | M + K(27) + R(2) | 1.35 + 5.40 + 2.00 = 8.75 |
| 2 | Search for parameter: Ctrl+W + param name + Enter | M + K(10) + R(1) | 1.35 + 2.00 + 1.00 = 4.35 |
| 3 | Edit value (~10 chars) | M + K(10) | 1.35 + 2.00 = 3.35 |
| 4 | Save: Ctrl+X, Y, Enter | K(3) | 0.60 |
| **Total** | | | **17.05 s** |

Without R: 8.75*(no R2)=6.75 + 4.35*(no R1)=3.35 + 3.35 + 0.60 = **14.05 s**

**Platform (edit YAML config):**

| Step | Action | Operators | Time (s) |
|------|--------|-----------|----------|
| 1 | Open config: `nano experiments/configs/srq4_eval.yaml` + Enter | M + K(45) + R(2) | 1.35 + 9.00 + 2.00 = 12.35 |
| 2 | Navigate to parameter (short file, visible immediately) | M | 1.35 |
| 3 | Edit value (~10 chars) | M + K(10) | 1.35 + 2.00 = 3.35 |
| 4 | Save: Ctrl+X, Y, Enter | K(3) | 0.60 |
| **Total** | | | **17.65 s** |

Without R: 12.35*(no R2)=10.35 + 1.35 + 3.35 + 0.60 = **15.65 s**

**KLM Totals (excluding R):**
- Baseline: **14.05 s**
- Platform: **15.65 s**
- **Reduction: −11%** (platform marginally slower — config path is longer to type than script name)

> Note: T1 and T2 show near-zero or slightly negative reduction. Both workflows involve equivalent file editing; the platform's YAML path is longer to type than the Python script name. This is expected for tasks where the platform's value is organizational/structural, not interaction-speed.

---

## T3: Start Training

**Task:** Initiate a training run with the configured experiment.

**Baseline (direct Python invocation):**

| Step | Action | Operators | Time (s) |
|------|--------|-----------|----------|
| 1 | Type run command: `PYTHONPATH=src python scripts/ray_footbot_aggregation_srq2.py` + Enter | M + K(59) | 1.35 + 11.80 = 13.15 |
| **Total** | | | **13.15 s** |

**Platform:**

| Step | Action | Operators | Time (s) |
|------|--------|-----------|----------|
| 1 | Type: `platform run srq4_eval` + Enter | M + K(21) | 1.35 + 4.20 = 5.55 |
| **Total** | | | **5.55 s** |

**KLM Totals:**
- Baseline: **13.15 s**
- Platform: **5.55 s**
- **Reduction: 57.8%**

---

## T4: Monitor Progress

**Task:** View training metrics and logs during an active run.

**Baseline (launch TensorBoard manually):**

| Step | Action | Operators | Time (s) |
|------|--------|-----------|----------|
| 1 | Find results dir: `ls results/` + Enter | M + K(9) + R(1) | 1.35 + 1.80 + 1.00 = 4.15 |
| 2 | Launch TensorBoard: `tensorboard --logdir results/srq4_eval_20240115-120000/tensorboard/` + Enter | M + K(68) | 1.35 + 13.60 = 14.95 |
| 3 | Open browser to TensorBoard URL | M + H + P + B | 1.35 + 0.40 + 1.10 + 0.10 = 2.95 |
| **Total** | | | **22.05 s** |

Without R: 4.15*(no R1)=3.15 + 14.95 + 2.95 = **21.05 s**

**Platform (follow auto-printed TensorBoard link):**

| Step | Action | Operators | Time (s) |
|------|--------|-----------|----------|
| 1 | Click TensorBoard link printed by `platform run` in terminal | M + P + B | 1.35 + 1.10 + 0.10 = 2.55 |
| **Total** | | | **2.55 s** |

**KLM Totals:**
- Baseline: **21.05 s**
- Platform: **2.55 s**
- **Reduction: 87.9%**

---

## T5: View Results

**Task:** Access and interpret the final training results after a completed run.

**Baseline (navigate TensorBoard + manual inspection):**

| Step | Action | Operators | Time (s) |
|------|--------|-----------|----------|
| 1 | Find results dir: `ls results/` + Enter | M + K(9) + R(1) | 1.35 + 1.80 + 1.00 = 4.15 |
| 2 | Open TensorBoard (if not running): `tensorboard --logdir results/...` | M + K(65) + R(5) | 1.35 + 13.00 + 5.00 = 19.35 |
| 3 | Navigate to episode_reward_mean in UI | M + H + P + B × 3 | 1.35 + 0.40 + 1.10 + 0.30 = 3.15 |
| 4 | Read and note key values | M | 1.35 |
| **Total** | | | **28.00 s** |

Without R: 4.15*(no R1)=3.15 + 19.35*(no R5)=14.35 + 3.15 + 1.35 = **22.00 s**

**Platform:**

| Step | Action | Operators | Time (s) |
|------|--------|-----------|----------|
| 1 | Type: `platform show results` + Enter | M + K(20) + R(1) | 1.35 + 4.00 + 1.00 = 6.35 |
| **Total** | | | **6.35 s** |

Without R: 1.35 + 4.00 = **5.35 s**

**KLM Totals:**
- Baseline: **22.00 s**
- Platform: **5.35 s**
- **Reduction: 75.7%**

---

## T6: Export Experiment

**Task:** Create a shareable bundle of a completed experiment.

**Baseline (manual zip):**

| Step | Action | Operators | Time (s) |
|------|--------|-----------|----------|
| 1 | Find experiment dir: `ls results/` + Enter | M + K(9) + R(1) | 1.35 + 1.80 + 1.00 = 4.15 |
| 2 | Zip experiment: `zip -r srq4_eval.zip results/srq4_eval_20240115-120000/` + Enter | M + K(52) + R(3) | 1.35 + 10.40 + 3.00 = 14.75 |
| **Total** | | | **18.90 s** |

Without R: 4.15*(no R1)=3.15 + 14.75*(no R3)=11.75 = **14.90 s**

**Platform (interactive selection):**

| Step | Action | Operators | Time (s) |
|------|--------|-----------|----------|
| 1 | Type: `platform export` + Enter | M + K(15) + R(1) | 1.35 + 3.00 + 1.00 = 5.35 |
| 2 | Select experiment from list: type "1" + Enter | M + K(1) + R(3) | 1.35 + 0.20 + 3.00 = 4.55 |
| **Total** | | | **9.90 s** |

Without R: 5.35*(no R1)=4.35 + 4.55*(no R3)=1.55 = **5.90 s**

**KLM Totals:**
- Baseline: **14.90 s**
- Platform: **5.90 s**
- **Reduction: 60.4%**

---

## T7: Import and Reproduce

**Task:** Import an experiment bundle on a fresh environment and verify it reproduces.

**Baseline (manual unzip + reconfigure + re-run):**

| Step | Action | Operators | Time (s) |
|------|--------|-----------|----------|
| 1 | Find bundle: `ls bundles/` + Enter | M + K(9) + R(1) | 1.35 + 1.80 + 1.00 = 4.15 |
| 2 | Unzip: `unzip bundles/srq4_eval.zip -d experiments/reproduced/` + Enter | M + K(50) + R(5) | 1.35 + 10.00 + 5.00 = 16.35 |
| 3 | Open training script to update paths | M + K(45) + R(2) | 1.35 + 9.00 + 2.00 = 12.35 |
| 4 | Navigate to path constants: Ctrl+W + "PATH" | M + K(8) + R(1) | 1.35 + 1.60 + 1.00 = 3.95 |
| 5 | Edit paths to match new location (~40 chars) | M + K(40) | 1.35 + 8.00 = 9.35 |
| 6 | Save: Ctrl+X, Y, Enter | K(3) | 0.60 |
| 7 | Re-run: `PYTHONPATH=src python experiments/reproduced/srq4_eval/training/srq4_eval.py` | M + K(77) | 1.35 + 15.40 = 16.75 |
| **Total** | | | **63.50 s** |

Without R: 4.15*(no R1)=3.15 + 16.35*(no R5)=11.35 + 12.35*(no R2)=10.35 + 3.95*(no R1)=2.95 + 9.35 + 0.60 + 16.75 = **54.50 s**

**Platform:**

| Step | Action | Operators | Time (s) |
|------|--------|-----------|----------|
| 1 | Import bundle: `platform import srq4_eval.zip` + Enter | M + K(28) + R(5) | 1.35 + 5.60 + 5.00 = 11.95 |
| 2 | Run imported: `platform run` + Enter (select imported from list) | M + K(12) + R(1) | 1.35 + 2.40 + 1.00 = 4.75 |
| 3 | Select imported experiment: "1" + Enter | M + K(1) | 1.35 + 0.20 = 1.55 |
| **Total** | | | **18.25 s** |

Without R: 11.95*(no R5)=6.95 + 4.75*(no R1)=3.75 + 1.55 = **12.25 s**

**KLM Totals:**
- Baseline: **54.50 s**
- Platform: **12.25 s**
- **Reduction: 77.5%**

---

## KLM Summary (M4.5, M4.6)

*Times below exclude system response R(t) as per KLM convention (compute wait time is equal in both conditions).*

| Task | Baseline (s) | Platform (s) | Reduction (%) |
|------|--------------|--------------|---------------|
| T1: Configure | 37.35 | 40.35 | −8% |
| T2: Modify | 14.05 | 15.65 | −11% |
| T3: Train | 13.15 | 5.55 | 58% |
| T4: Monitor | 21.05 | 2.55 | 88% |
| T5: Results | 22.00 | 5.35 | 76% |
| T6: Export | 14.90 | 5.90 | 60% |
| T7: Import/Reproduce | 54.50 | 12.25 | 78% |
| **Average** | **25.29** | **12.51** | **49%** |

**Weighted KLM-Reduction (M4.6):** (177.00 − 87.60) / 177.00 = **50.5%**

**Simple average of per-task reduction:** (−8 − 11 + 58 + 88 + 76 + 60 + 78) / 7 = 341 / 7 = **48.7%**

**KLM-Predicted-Time (platform, M4.5):** mean 12.51 s per task

**Target:** ≥50% reduction

**Met?** BORDERLINE — weighted reduction 50.5% (meets); simple average 48.7% (misses by 1.3 pp)

---

## Interpretation

**Tasks T1 and T2 (Configure/Modify)** show negative reduction because both workflows involve editing text files. The platform's YAML config path is longer to type than the Python training script name. The platform's value here is structural/organizational (reproducibility, validation), not interaction speed.

**Tasks T3–T7** show large reductions (58–88%) because the platform replaces complex multi-step workflows with single short commands:
- T3: `platform run` replaces 59-char `PYTHONPATH=...` invocation
- T4: TensorBoard link printed automatically vs manual path discovery + launch
- T5: `platform show` replaces TensorBoard navigation + manual data extraction
- T6: Interactive selection replaces manual `ls` + `zip` with correct path
- T7: `platform import` + `platform run` replaces unzip + path editing + re-invocation

**Conclusion:** H4's KLM-Reduction criterion is borderline met (50.5% weighted). Whether H4 is supported or partially supported depends on method choice. Recommended: report weighted reduction (50.5%) as primary metric with per-task breakdown, and note T1/T2 as expected zero-benefit cases.
