# Protocol-SRQ5-Collaboration

## Header

| Field                | Value                                                                                                                                                                                                                                                           |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Protocol ID**      | P-SRQ5                                                                                                                                                                                                                                                          |
| **SRQ Reference**    | SRQ5: To what extent does Margos enable reliable reproduction of experiments across different research environments and by how much does it decrease time-to-reproduce?                                                                                   |
| **Hypothesis**       | H5: Margos' export/import mechanism significantly reduces sharing effort (Steps-to-Share, Time-to-Share) and receiving effort (Time-to-First-Run, Time-to-Reproduce) compared to manual experiment handoff, while maintaining high Handoff Success Rate. |
| **Success Criteria** | Significant reduction in sharing/receiving effort, Handoff-Success-Rate high                                                                                                                                                                                    |
| **Sample Size**      | N=20 total for Handoff-Success-Rate (10 manual + 10 Margos); N=10 per condition for timed trials (N raised to 20 in EvalPlanOverview for consistency with SRQ3; all 10 Margos trials include timing automatically)                                          |
| **Dependencies**     | Margos export/import implemented, isolated environment prepared                                                                                                                                                                                               |

---

## Prerequisites

### Required Artifacts
- [ ] Margos CLI operational (`export`, `import`, `run`)
- [ ] Completed experiment ready for export
- [ ] Isolated environment for "Researcher B" simulation
- [ ] Screen recording software
- [ ] Timer/stopwatch

### Environment Setup

**Machine A (Researcher A):**
- [ ] Margos installed
- [ ] Completed experiment in results directory

**Machine B (Simulated Researcher B):**
- [ ] Dedicated macOS user account (`researcherb`) prepared once before the study
- [ ] Fixed base environment available: ARGoS, Python, plugin build capability, `margos`, `ArgosToZoo`, shell config, shared SRQ5 `.venv`
- [ ] No pre-existing SRQ5 experiment artifacts available at trial start
- [ ] Transfer path restricted to `/Users/Shared/srq5-transfer`
- [ ] No direct use of Machine A working directories or results

### Pre-Execution Checklist
- [ ] Baseline workflow steps documented (8 steps)
- [ ] Margos workflow steps documented (5 steps)
- [ ] Transfer mechanism decided (e.g., file copy, simulated network transfer)
- [ ] Researcher B environment specification documented

---

## Definitions

### Key Terms

| Term                     | Definition                                                     |
| ------------------------ | -------------------------------------------------------------- |
| **Researcher A**         | Entity that creates and shares the experiment                  |
| **Researcher B**         | Entity that receives and reproduces the experiment (simulated) |
| **Handoff**              | Complete process from A sharing to B reproducing               |
| **Steps-to-Share**       | Manual actions required to prepare experiment for sharing      |
| **Time-to-Share**        | Time from "I want to share" to "bundle ready for transfer"     |
| **Time-to-First-Run**    | Time from "bundle received" to "first successful execution"    |
| **Time-to-Reproduce**    | Time from "bundle received" to "results verified as matching"  |
| **Handoff-Success-Rate** | % of handoffs where B successfully reproduces A's results      |
| **Bundle-Completeness**  | Checklist score of required components present in bundle       |
| **Setup-Divergence**     | Differences between A's and B's environment configurations     |

### Handoff Success Definition

A handoff is **successful** if Researcher B's experiment produces a final episode reward mean (averaged over the last 50 episodes of training) within **±1%** of Researcher A's reference value.

- Manual condition: Researcher B exports TensorBoard scalar data to CSV and computes the mean of the last 50 reward values. Compares against the reference value documented in A's README.
- Margos condition: `margos compare` applies the same ±1% threshold automatically for the reported **SRQ5 handoff** status. The command also reports a stricter SRQ3 reproducibility status, but that stricter judgment is not used for M5.5.

The initial SRQ5 draft specified a broader success tolerance. Before final analysis, this criterion was standardized to a stricter **±1%** threshold, computed on the mean of the final 50 reward values, and this finalized rule was used consistently in the reported evaluation. Because all successful Margos trials showed **0% deviation** under the finalized comparison, this amendment did not affect the study outcome.

### Measurement Triggers

| Metric            | Start Trigger                                   | Stop Trigger                                     |
| ----------------- | ----------------------------------------------- | ------------------------------------------------ |
| Time-to-Share     | Decision made to share ("I want to share this") | Shareable artifact ready (zip/bundle created)    |
| Time-to-First-Run | Bundle received on Machine B                    | First successful execution (any output produced) |
| Time-to-Reproduce | Bundle received on Machine B                    | Results verified as matching (SRQ5 handoff status passes) |
| Steps-to-Share    | First action toward sharing                     | Artifact ready for transfer                      |

### Controlled Variables

| Variable                          | How Controlled                                                                         |
| --------------------------------- | -------------------------------------------------------------------------------------- |
| Experiment being shared           | Same experiment for all trials                                                         |
| Transfer mechanism                | Consistent (e.g., file copy)                                                           |
| Machine B specification           | Same prepared `researcherb` account and fixed base environment                         |
| Pre-installed base infrastructure | Fixed and identical across trials; experiment-specific artifacts absent at trial start |

---

## Procedure

During timed trials, commands may be pasted verbatim into the terminal. Typing speed is not a measured SRQ5 metric; only the documented workflow steps and elapsed wall-clock time count. Use the same paste-as-written convention across all trials and both conditions.

### Condition A: Manual Workflow (Baseline)

#### Starting Machine State (identical for both conditions)

| Component                                 | Present? | Notes                                                                           |
| ----------------------------------------- | -------- | ------------------------------------------------------------------------------- |
| OS + Python                               | Yes      | Same version as Machine A                                                       |
| ARGoS binary + plugins                    | Yes      | Same version as Machine A                                                       |
| `ARGOS_PLUGIN_PATH` configured            | Yes      | Base infrastructure, identical on both machines                                 |
| ZMQ port 5555 available                   | Yes      | Base infrastructure, assumed free and working                                   |
| ArgosToZoo repo checked out               | Yes      | Provides `src/zoo/*` and `PYTHONPATH=src`                                       |
| Margos CLI                              | Yes      | Required for Condition B; present in both for symmetry                          |
| Common packages (numpy, torch, ray, etc.) | Yes      | Base ecosystem, not experiment-pinned                                           |
| Experiment files / bundle                 | **No**   | This is what the handoff provides                                               |
| Experiment-specific pinned deps           | **No**   | Manual: B installs from A's `requirements.txt`; Margos: handled automatically |

> **Rationale:** Margos installation is infrastructure cost amortized across all experiments. Both conditions start from the same state; measured friction is purely the experiment handoff itself.

Machine B is simulated by a dedicated prepared macOS account that remains constant across the study. The account's base software environment is installed once and treated as fixed infrastructure, not part of the measured handoff effort. Before each trial, all experiment-specific state from prior trials is removed so that only the prepared base environment persists.

#### Step 0 — Reference run on Machine A (per trial)

```bash
# From the ArgosToZoo repo root
PYTHONPATH=src python scripts/ray_footbot_aggregation_srq5.py
# Note the timestamped output dir, e.g.: results/aggregation_srq5_20260407-143000/
```

Produces the reference results (TensorBoard logs + final checkpoint) that Researcher B must reproduce.

All relative paths in the manual workflow below are executed from the `ArgosToZoo` repo root on the active machine. `/Users/Shared/srq5-transfer` is the only out-of-repo path used during timed trials.

#### Sharing Phase — 8 steps

**Step 1 — Identify files**
```bash
ls scripts/ray_footbot_aggregation_srq5.py \
   experiments/footbot_aggregation_srq5.argos
# src/zoo/* are repo source files — present on both machines, not shared
```

**Step 2 — Copy files to staging**
```bash
mkdir -p srq5_share/scripts \
          srq5_share/experiments \
          srq5_share/results

cp scripts/ray_footbot_aggregation_srq5.py    srq5_share/scripts/
cp experiments/footbot_aggregation_srq5.argos srq5_share/experiments/
cp -r results/aggregation_srq5_<TIMESTAMP>/   srq5_share/results/reference/
```

**Step 3 — Write README** (use mandatory template below)
```bash
cat > srq5_share/README.md <<'EOF'
Experiment: footbot_aggregation_srq5
Run command: cp manual_received/srq5_received/scripts/ray_footbot_aggregation_srq5.py scripts/ray_footbot_aggregation_srq5.py && cp manual_received/srq5_received/experiments/footbot_aggregation_srq5.argos experiments/footbot_aggregation_srq5.argos && PYTHONPATH=src python scripts/ray_footbot_aggregation_srq5.py
Output dir: results/aggregation_srq5_<timestamp>/
Seeds: random_seed=<X> (argos), see experiments/footbot_aggregation_srq5.argos
Reference result: Final episode reward mean = <value> (mean of last 50 episodes)
Dependencies: pip install -r requirements.txt
Python: <version>  OS: macOS <version>
Compare: export TensorBoard scalar to CSV; compute mean of last 50 reward values; must be within ±1% of reference result above
EOF
# Replace placeholders after Steps 5 and 6 once the values have been collected.
```

README mandatory template (all fields required; do not deviate between trials):
```
Experiment: footbot_aggregation_srq5
Run command: cp manual_received/srq5_received/scripts/ray_footbot_aggregation_srq5.py scripts/ray_footbot_aggregation_srq5.py && cp manual_received/srq5_received/experiments/footbot_aggregation_srq5.argos experiments/footbot_aggregation_srq5.argos && PYTHONPATH=src python scripts/ray_footbot_aggregation_srq5.py
Output dir: results/aggregation_srq5_<timestamp>/
Seeds: random_seed=<X> (argos), see experiments/footbot_aggregation_srq5.argos
Reference result: Final episode reward mean = <value> (mean of last 50 episodes)
Dependencies: pip install -r requirements.txt
Python: <version>  OS: macOS <version>
Compare: export TensorBoard scalar to CSV; compute mean of last 50 reward values; must be within ±1% of reference result above
```

**Step 4 — List dependencies** (use pre-defined grep pattern; do not adjust per trial)
```bash
pip freeze | grep -E "^ray==|^pettingzoo==|^pyzmq==|^numpy==|^torch==|^tensorboard==|^gymnasium==" \
  > srq5_share/requirements.txt
```

**Step 5 — Document seeds**
```bash
grep "random_seed" experiments/footbot_aggregation_srq5.argos
grep -n "seed\|SEED" scripts/ray_footbot_aggregation_srq5.py
# Update the README seeds field with the discovered value(s).
```

**Step 6 — Document environment**
```bash
python --version
sw_vers -productVersion
pip show ray torch numpy pettingzoo pyzmq | grep -E "^Name|^Version"
# Update the README Python and OS fields with these values.
# (ARGOS_PLUGIN_PATH, ZMQ port — base infrastructure, assumed identical on both machines)
```

**Step 7 — Package**
```bash
mkdir -p bundles
(cd srq5_share && zip -r ../bundles/srq5_bundle.zip .)
```

**Step 8 — Transfer**
```bash
cp bundles/srq5_bundle.zip /Users/Shared/srq5-transfer/srq5_manual_.zip
```

#### Receiving Phase — 6 steps

**Step 1 — Unpack**
```bash
mkdir -p manual_received
unzip /Users/Shared/srq5-transfer/srq5_bundle.zip -d manual_received/srq5_received/
```

**Step 2 — Read README**
```bash
cat manual_received/srq5_received/README.md
```

**Step 3 — Verify/install experiment dependencies against the prepared shared venv**
```bash
pip install -r manual_received/srq5_received/requirements.txt
```

On the prepared Machine B account this command is expected to validate or reuse the fixed shared SRQ5 virtualenv, not provision a brand-new Python environment.

**Step 4 — Run experiment**
```bash
cp manual_received/srq5_received/scripts/ray_footbot_aggregation_srq5.py scripts/ray_footbot_aggregation_srq5.py
cp manual_received/srq5_received/experiments/footbot_aggregation_srq5.argos experiments/footbot_aggregation_srq5.argos
```

These copies install the handed-off files into the live `ArgosToZoo` checkout so Researcher B runs the shared script and scenario, not any stale local copy.

**Step 5 — Run experiment**
```bash
PYTHONPATH=src python scripts/ray_footbot_aggregation_srq5.py
# Note the new output dir, e.g. results/aggregation_srq5_<NEW_TIMESTAMP>/
```

**Step 6 — Compare results (manual)**
```bash
tensorboard --logdir manual_received/srq5_received/results/reference/tensorboard --port 6006 &
tensorboard --logdir results/aggregation_srq5_<NEW_TIMESTAMP>/tensorboard --port 6007 &
# Open http://localhost:6006 and http://localhost:6007, compare reward/mean curves
```

--- 


### Condition B: Margos Workflow

**Machine A — Researcher A:** Sharing Phase - 1 step
```bash
# Step 0 (pre-trial, NOT counted in Steps-to-Share): Run experiment (produces reference run)
margos run srq5_eval

# Step 1: Export reference run
margos export srq5_eval_<timestamp> --output /Users/Shared/srq5-transfer/srq5_eval_<timestamp>.zip
```

**Transfer:**
```bash
# Step 2: Bundle available to Machine B in the shared host transfer directory (no manual action)
# Machine A writes to /Users/Shared/srq5-transfer and Machine B reads only the received artifact from there
```

**Machine B — Researcher B:** Receiving Phase - 3 steps
```bash
# Step 3: Import bundle
margos import /Users/Shared/srq5-transfer/srq5_eval_<timestamp>.zip

# Step 4: Run experiment from imported config
margos run srq5_eval

# Step 5: Verify reproduction
margos compare <new_result_dir> srq5_eval_<timestamp>
```

**Total Margos steps: 5 active (+ 1 Step 0 pre-trial, not counted)**

**Steps-to-Share (M5.1): 1** (step 1 only, from "I want to share" to "bundle ready")

### Shared Transfer Setup

Machine A and Machine B are separate macOS user accounts on the same host. A shared host directory acts as the transfer point:

```bash
sudo mkdir -p /Users/Shared/srq5-transfer
sudo chmod 1777 /Users/Shared/srq5-transfer

# Machine A (Researcher A) writes transfer artifacts here
cp <artifact> /Users/Shared/srq5-transfer/

# Machine B (Researcher B) reads/imports artifacts from here
ls /Users/Shared/srq5-transfer/
```

Transfer time is not measured: Time-to-Share stops when the artifact is written to `/Users/Shared/srq5-transfer`, Time-to-First-Run starts when Researcher B begins unpack/import.

### Researcher B Simulation Setup

Prepare the dedicated Machine B account once before the study:

```bash
# One-time setup (already validated before timed trials)
cd ~/Repos/margos
./scripts/bootstrap_researcherb.sh

# One-time dry run validation
./scripts/srq5_dry_run_researcherb.sh
```

Stable base state that remains fixed across trials:
- macOS user account `researcherb`
- Host-native ARGoS, Python, and plugin build capability
- `~/Repos/margos` checkout
- `~/Repos/ArgosToZoo` checkout
- `~/.venvs/srq5` shared virtualenv
- Shell configuration and aliases

Per-trial reset requirement:
- Remove prior received bundles from `/Users/Shared/srq5-transfer`
- Remove prior manual handoff directories under `manual_received/`
- Remove prior manual staging artifacts `srq5_share/` and `bundles/srq5_bundle.zip`
- Remove prior manually copied SRQ5 handoff files from the `ArgosToZoo` checkout: `scripts/ray_footbot_aggregation_srq5.py` and `experiments/footbot_aggregation_srq5.argos`
- Remove prior imported experiments under `~/Repos/margos/experiments/imported/`
- Remove prior trial result directories relevant to the next run
- Verify no previous trial README, requirements, bundle, imported config, or result artifact remains available to the operator

Pasteable reset command for the `researcherb` account (run from any directory):

```bash
rm -rf \
  /Users/Shared/srq5-transfer/* \
  "$HOME/Repos/ArgosToZoo/manual_received" \
  "$HOME/Repos/ArgosToZoo/srq5_share" \
  "$HOME/Repos/ArgosToZoo/bundles/srq5_bundle.zip" \
  "$HOME/Repos/ArgosToZoo/scripts/ray_footbot_aggregation_srq5.py" \
  "$HOME/Repos/ArgosToZoo/experiments/footbot_aggregation_srq5.argos" \
  "$HOME/Repos/ArgosToZoo/results/aggregation_srq5_"* \
  "$HOME/Repos/margos/experiments/imported/"* \
  "$HOME/Repos/margos/results/srq5_eval_"*
```

This command removes only per-trial SRQ5 artifacts. It does not remove the fixed repo checkouts, the shared virtualenv, or any non-SRQ5 experiment assets.

If contamination is suspected, document the issue in the trial log. Re-clean the account state and rerun the trial; if cleanup is insufficient, re-run the one-time bootstrap as an exception path.

### Trial Protocol

For each trial:

1. **Reset Machine B trial state** (remove prior received bundles, imported configs, results, and transfer artifacts; verify no prior trial experiment data remains accessible)
2. **Start screen recording**
3. **Confirm cleanup complete before any timer starts**

**A's Sharing Phase:**
4. **State trial ID and condition**
5. **Start timer** (Time-to-Share)
6. **Perform sharing workflow** (Baseline or Margos)
7. **Count steps**
8. **Stop timer** when bundle ready

**Transfer:**
9. **Transfer bundle to Machine B**

**B's Receiving Phase:**
10. **Start timer** (Time-to-First-Run)
11. **Perform import/setup**
12. **Mark when first run succeeds**
13. **Continue to verification**
14. **Stop timer** when results verified (Time-to-Reproduce)
15. **Record success/failure**

16. **Stop screen recording**
17. **Record all data**

---

## Data Collection

### Per-Trial Data

| Trial | Condition | Steps-to-Share | Time-to-Share (sec) | Time-to-First-Run (sec) | Time-to-Reproduce (sec) | Handoff Success? |
| ----- | --------- | -------------- | ------------------- | ----------------------- | ----------------------- | ---------------- |
| 1     | Manual    | 8              | 115                 | 36                      | 167                     | Yes              |
| 2     | Manual    | 8              | 110                 | 62                      | 140                     | Yes              |
| 3     | Manual    | 8              | 132                 | 60                      | 121                     | Yes              |
| 4     | Manual    | 8              | 106                 | 52                      | 97                      | Yes              |
| 5     | Manual    | 8              | 69                  | 50                      | 86                      | Yes              |
| 6     | Manual    | 8              | 123                 | 33                      | 162                     | Yes              |
| 7     | Manual    | 8              | 112                 | 70                      | 145                     | Yes              |
| 8     | Manual    | 8              | 139                 | 59                      | 119                     | Yes              |
| 9     | Manual    | 8              | 106                 | 54                      | 102                     | Yes              |
| 10    | Manual    | 8              | 65                  | 50                      | 84                      | Yes              |
| 1     | Margos  | 1              | 57                  | 70                      | 80                      | Yes              |
| 2     | Margos  | 1              | 59                  | 39                      | 47                      | Yes              |
| 3     | Margos  | 1              | 29                  | 60                      | 77                      | Yes              |
| 4     | Margos  | 1              | 24                  | 55                      | 63                      | Yes              |
| 5     | Margos  | 1              | 15                  | 58                      | 65                      | Yes              |
| 6     | Margos  | 1              | 58                  | 73                      | 82                      | Yes              |
| 7     | Margos  | 1              | 57                  | 37                      | 46                      | Yes              |
| 8     | Margos  | 1              | 32                  | 63                      | 78                      | Yes              |
| 9     | Margos  | 1              | 25                  | 54                      | 59                      | Yes              |
| 10    | Margos  | 1              | 18                  | 56                      | 65                      | Yes              |

### Raw Timestamp Capture

Use the screen recording as the source of truth and fill these workflow tables during a single review pass per trial.

1. Record the visible video timestamp when the command starts executing.
2. Record the visible video timestamp when the expected command output or artifact-ready state appears.
3. Convert the difference to `Duration (sec)` once per row.
4. Sum the rows marked `Share` to fill `Time-to-Share (sec)`.
5. Sum the receiving rows up to the first successful run to fill `Time-to-First-Run (sec)`.
6. Sum all receiving rows through verification to fill `Time-to-Reproduce (sec)`.

Default timing boundary: command start = Enter key or execution trigger; command end = expected output, finished file write, or verified completion state visible in the recording.

#### Manual Workflow Raw Command Timestamps

Use one row per documented protocol step. For manual trials, `Time-to-First-Run` is the sum of Machine B receiving steps 1-5, and `Time-to-Reproduce` is the sum of Machine B receiving steps 1-6.

| Trial | Machine | Phase     | Step | Command / Action                                       | Start | End  | Duration (sec) | Included In           | Notes |
| ----- | ------- | --------- | ---- | ------------------------------------------------------ | ----- | ---- | -------------- | --------------------- | ----- |
| 1     | A       | Sharing   | 1    | Identify files (`ls ...`)                              | 0:46  | 0:48 | 2              | Share                 |       |
| 1     | A       | Sharing   | 2    | Stage share files (`mkdir -p`, `cp`, `cp -r`)          | 0:56  | 1:18 | 22             | Share                 |       |
| 1     | A       | Sharing   | 3    | Write `README.md`                                      | 1:28  | 1:46 | 18             | Share                 |       |
| 1     | A       | Sharing   | 4    | Capture `requirements.txt`                             | 2:01  | 2:04 | 3              | Share                 |       |
| 1     | A       | Sharing   | 5    | Document seeds                                         | 2:13  | 2:13 | 0              | Share                 |       |
| 1     | A       | Sharing   | 6    | Document environment                                   | 2:13  | 3:17 | 64             | Share                 |       |
| 1     | A       | Sharing   | 7    | Package bundle (`zip -r`)                              | 3:21  | 3:24 | 3              | Share                 |       |
| 1     | A       | Sharing   | 8    | Transfer bundle to `/Users/Shared/srq5-transfer`       | 3:29  | 3:32 | 3              | Share                 |       |
| 1     | B       | Receiving | 1    | Unpack bundle (`unzip`)                                | 0:06  | 0:08 | 2              | First-Run, Reproduce  |       |
| 1     | B       | Receiving | 2    | Read `README.md`                                       | 0:14  | 0:16 | 2              | First-Run, Reproduce  |       |
| 1     | B       | Receiving | 3    | Install/verify dependencies (`pip install -r ...`)     | 0:23  | 0:25 | 2              | First-Run, Reproduce  |       |
| 1     | B       | Receiving | 4    | Copy received files into checkout                      | 0:37  | 0:38 | 1              | First-Run, Reproduce  |       |
| 1     | B       | Receiving | 5    | Run experiment (`PYTHONPATH=src python ...`)           | 0:48  | 1:17 | 29             | First-Run, Reproduce  |       |
| 1     | B       | Receiving | 6    | Compare results (TensorBoard/manual check)             | 1:24  | 3:35 | 131            | Reproduce             |       |
| 2     | A       | Sharing   | 1    | Identify files (`ls ...`)                              | 0:32  | 0:35 | 3              | Share                 |       |
| 2     | A       | Sharing   | 2    | Stage share files (`mkdir -p`, `cp`, `cp -r`)          | 0:41  | 1:03 | 22             | Share                 |       |
| 2     | A       | Sharing   | 3    | Write `README.md`                                      | 1:19  | 1:22 | 3              | Share                 |       |
| 2     | A       | Sharing   | 4    | Capture `requirements.txt`                             | 1:41  | 1:42 | 1              | Share                 |       |
| 2     | A       | Sharing   | 5    | Document seeds                                         | 2:02  | 2:03 | 1              | Share                 |       |
| 2     | A       | Sharing   | 6    | Document environment                                   | 1:22  | 2:38 | 76             | Share                 |       |
| 2     | A       | Sharing   | 7    | Package bundle (`zip -r`)                              | 2:43  | 2:44 | 1              | Share                 |       |
| 2     | A       | Sharing   | 8    | Transfer bundle to `/Users/Shared/srq5-transfer`       | 2:48  | 2:51 | 3              | Share                 |       |
| 2     | B       | Receiving | 1    | Unpack bundle (`unzip`)                                | 0:00  | 0:30 | 30             | First-Run, Reproduce  |       |
| 2     | B       | Receiving | 2    | Read `README.md`                                       | 0:34  | 0:36 | 2              | First-Run, Reproduce  |       |
| 2     | B       | Receiving | 3    | Install/verify dependencies (`pip install -r ...`)     | 0:41  | 0:42 | 1              | First-Run, Reproduce  |       |
| 2     | B       | Receiving | 4    | Copy received files into checkout                      | 0:48  | 0:49 | 1              | First-Run, Reproduce  |       |
| 2     | B       | Receiving | 5    | Run experiment (`PYTHONPATH=src python ...`)           | 1:18  | 1:46 | 28             | First-Run, Reproduce  |       |
| 2     | B       | Receiving | 6    | Compare results (TensorBoard/manual check)             | 1:47  | 3:05 | 78             | Reproduce             |       |
| 3     | A       | Sharing   | 1    | Identify files (`ls ...`)                              | 0:47  | 0:48 | 1              | Share                 |       |
| 3     | A       | Sharing   | 2    | Stage share files (`mkdir -p`, `cp`, `cp -r`)          | 0:54  | 1:08 | 14             | Share                 |       |
| 3     | A       | Sharing   | 3    | Write `README.md`                                      | 1:13  | 1:17 | 4              | Share                 |       |
| 3     | A       | Sharing   | 4    | Capture `requirements.txt`                             | 1:28  | 1:29 | 1              | Share                 |       |
| 3     | A       | Sharing   | 5    | Document seeds                                         | 1:34  | 1:35 | 1              | Share                 |       |
| 3     | A       | Sharing   | 6    | Document environment                                   | 1:17  | 2:18 | 61             | Share                 |       |
| 3     | A       | Sharing   | 7    | Package bundle (`zip -r`)                              | 2:23  | 2:24 | 1              | Share                 |       |
| 3     | A       | Sharing   | 8    | Transfer bundle to `/Users/Shared/srq5-transfer`       | 2:28  | 3:17 | 49             | Share                 |       |
| 3     | B       | Receiving | 1    | Unpack bundle (`unzip`)                                | 0:16  | 0:41 | 25             | First-Run, Reproduce  |       |
| 3     | B       | Receiving | 2    | Read `README.md`                                       | 0:46  | 0:47 | 1              | First-Run, Reproduce  |       |
| 3     | B       | Receiving | 3    | Install/verify dependencies (`pip install -r ...`)     | 0:57  | 0:58 | 1              | First-Run, Reproduce  |       |
| 3     | B       | Receiving | 4    | Copy received files into checkout                      | 1:01  | 1:02 | 1              | First-Run, Reproduce  |       |
| 3     | B       | Receiving | 5    | Run experiment (`PYTHONPATH=src python ...`)           | 1:08  | 1:40 | 32             | First-Run, Reproduce  |       |
| 3     | B       | Receiving | 6    | Compare results (TensorBoard/manual check)             | 1:40  | 2:41 | 61             | Reproduce             |       |
| 4     | A       | Sharing   | 1    | Identify files (`ls ...`)                              | 0:32  | 0:32 | 0              | Share                 |       |
| 4     | A       | Sharing   | 2    | Stage share files (`mkdir -p`, `cp`, `cp -r`)          | 0:38  | 1:20 | 42             | Share                 |       |
| 4     | A       | Sharing   | 3    | Write `README.md`                                      | 1:31  | 1:32 | 1              | Share                 |       |
| 4     | A       | Sharing   | 4    | Capture `requirements.txt`                             | 1:37  | 1:38 | 1              | Share                 |       |
| 4     | A       | Sharing   | 5    | Document seeds                                         | 1:42  | 1:43 | 1              | Share                 |       |
| 4     | A       | Sharing   | 6    | Document environment                                   | 1:38  | 2:28 | 50             | Share                 |       |
| 4     | A       | Sharing   | 7    | Package bundle (`zip -r`)                              | 2:33  | 2:34 | 1              | Share                 |       |
| 4     | A       | Sharing   | 8    | Transfer bundle to `/Users/Shared/srq5-transfer`       | 2:41  | 2:51 | 10             | Share                 |       |
| 4     | B       | Receiving | 1    | Unpack bundle (`unzip`)                                | 0:03  | 0:25 | 22             | First-Run, Reproduce  |       |
| 4     | B       | Receiving | 2    | Read `README.md`                                       | 0:30  | 0:31 | 1              | First-Run, Reproduce  |       |
| 4     | B       | Receiving | 3    | Install/verify dependencies (`pip install -r ...`)     | 0:35  | 0:36 | 1              | First-Run, Reproduce  |       |
| 4     | B       | Receiving | 4    | Copy received files into checkout                      | 0:41  | 0:42 | 1              | First-Run, Reproduce  |       |
| 4     | B       | Receiving | 5    | Run experiment (`PYTHONPATH=src python ...`)           | 0:49  | 1:16 | 27             | First-Run, Reproduce  |       |
| 4     | B       | Receiving | 6    | Compare results (TensorBoard/manual check)             | 1:16  | 2:01 | 45             | Reproduce             |       |
| 5     | A       | Sharing   | 1    | Identify files (`ls ...`)                              | 0:34  | 0:35 | 1              | Share                 |       |
| 5     | A       | Sharing   | 2    | Stage share files (`mkdir -p`, `cp`, `cp -r`)          | 0:41  | 0:54 | 13             | Share                 |       |
| 5     | A       | Sharing   | 3    | Write `README.md`                                      | 1:03  | 1:03 | 0              | Share                 |       |
| 5     | A       | Sharing   | 4    | Capture `requirements.txt`                             | 1:09  | 1:11 | 2              | Share                 |       |
| 5     | A       | Sharing   | 5    | Document seeds                                         | 1:16  | 1:17 | 1              | Share                 |       |
| 5     | A       | Sharing   | 6    | Document environment                                   | 1:17  | 1:59 | 42             | Share                 |       |
| 5     | A       | Sharing   | 7    | Package bundle (`zip -r`)                              | 2:04  | 2:05 | 1              | Share                 |       |
| 5     | A       | Sharing   | 8    | Transfer bundle to `/Users/Shared/srq5-transfer`       | 2:09  | 2:18 | 9              | Share                 |       |
| 5     | B       | Receiving | 1    | Unpack bundle (`unzip`)                                | 0:00  | 0:17 | 17             | First-Run, Reproduce  |       |
| 5     | B       | Receiving | 2    | Read `README.md`                                       | 0:22  | 0:23 | 1              | First-Run, Reproduce  |       |
| 5     | B       | Receiving | 3    | Install/verify dependencies (`pip install -r ...`)     | 0:27  | 0:28 | 1              | First-Run, Reproduce  |       |
| 5     | B       | Receiving | 4    | Copy received files into checkout                      | 0:34  | 0:34 | 0              | First-Run, Reproduce  |       |
| 5     | B       | Receiving | 5    | Run experiment (`PYTHONPATH=src python ...`)           | 0:38  | 1:09 | 31             | First-Run, Reproduce  |       |
| 5     | B       | Receiving | 6    | Compare results (TensorBoard/manual check)             | 1:09  | 1:45 | 36             | Reproduce             |       |
| 6     | A       | Sharing   | 1    | Identify files (`ls ...`)                              | 0:47  | 0:48 | 1              | Share                 |       |
| 6     | A       | Sharing   | 2    | Stage share files (`mkdir -p`, `cp`, `cp -r`)          | 0:57  | 1:22 | 25             | Share                 |       |
| 6     | A       | Sharing   | 3    | Write `README.md`                                      | 1:29  | 1:49 | 20             | Share                 |       |
| 6     | A       | Sharing   | 4    | Capture `requirements.txt`                             | 2:03  | 2:04 | 1              | Share                 |       |
| 6     | A       | Sharing   | 5    | Document seeds                                         | 2:12  | 2:13 | 1              | Share                 |       |
| 6     | A       | Sharing   | 6    | Document environment                                   | 2:16  | 3:21 | 65             | Share                 |       |
| 6     | A       | Sharing   | 7    | Package bundle (`zip -r`)                              | 3:27  | 3:32 | 5              | Share                 |       |
| 6     | A       | Sharing   | 8    | Transfer bundle to `/Users/Shared/srq5-transfer`       | 3:40  | 3:45 | 5              | Share                 |       |
| 6     | B       | Receiving | 1    | Unpack bundle (`unzip`)                                | 0:07  | 0:08 | 1              | First-Run, Reproduce  |       |
| 6     | B       | Receiving | 2    | Read `README.md`                                       | 0:12  | 0:13 | 1              | First-Run, Reproduce  |       |
| 6     | B       | Receiving | 3    | Install/verify dependencies (`pip install -r ...`)     | 0:22  | 0:25 | 3              | First-Run, Reproduce  |       |
| 6     | B       | Receiving | 4    | Copy received files into checkout                      | 0:36  | 0:38 | 2              | First-Run, Reproduce  |       |
| 6     | B       | Receiving | 5    | Run experiment (`PYTHONPATH=src python ...`)           | 0:47  | 1:13 | 26             | First-Run, Reproduce  |       |
| 6     | B       | Receiving | 6    | Compare results (TensorBoard/manual check)             | 1:17  | 3:26 | 129            | Reproduce             |       |
| 7     | A       | Sharing   | 1    | Identify files (`ls ...`)                              | 0:35  | 0:40 | 5              | Share                 |       |
| 7     | A       | Sharing   | 2    | Stage share files (`mkdir -p`, `cp`, `cp -r`)          | 0:48  | 1:09 | 21             | Share                 |       |
| 7     | A       | Sharing   | 3    | Write `README.md`                                      | 1:27  | 1:28 | 1              | Share                 |       |
| 7     | A       | Sharing   | 4    | Capture `requirements.txt`                             | 1:44  | 1:48 | 4              | Share                 |       |
| 7     | A       | Sharing   | 5    | Document seeds                                         | 2:06  | 2:07 | 1              | Share                 |       |
| 7     | A       | Sharing   | 6    | Document environment                                   | 2:07  | 3:22 | 75             | Share                 |       |
| 7     | A       | Sharing   | 7    | Package bundle (`zip -r`)                              | 3:26  | 3:30 | 4              | Share                 |       |
| 7     | A       | Sharing   | 8    | Transfer bundle to `/Users/Shared/srq5-transfer`       | 3:31  | 3:32 | 1              | Share                 |       |
| 7     | B       | Receiving | 1    | Unpack bundle (`unzip`)                                | 0:00  | 0:32 | 32             | First-Run, Reproduce  |       |
| 7     | B       | Receiving | 2    | Read `README.md`                                       | 0:35  | 0:39 | 4              | First-Run, Reproduce  |       |
| 7     | B       | Receiving | 3    | Install/verify dependencies (`pip install -r ...`)     | 0:41  | 0:42 | 1              | First-Run, Reproduce  |       |
| 7     | B       | Receiving | 4    | Copy received files into checkout                      | 0:45  | 0:47 | 2              | First-Run, Reproduce  |       |
| 7     | B       | Receiving | 5    | Run experiment (`PYTHONPATH=src python ...`)           | 1:18  | 1:49 | 31             | First-Run, Reproduce  |       |
| 7     | B       | Receiving | 6    | Compare results (TensorBoard/manual check)             | 1:49  | 3:04 | 75             | Reproduce             |       |
| 8     | A       | Sharing   | 1    | Identify files (`ls ...`)                              | 0:50  | 0:51 | 1              | Share                 |       |
| 8     | A       | Sharing   | 2    | Stage share files (`mkdir -p`, `cp`, `cp -r`)          | 0:54  | 1:09 | 15             | Share                 |       |
| 8     | A       | Sharing   | 3    | Write `README.md`                                      | 1:13  | 1:16 | 3              | Share                 |       |
| 8     | A       | Sharing   | 4    | Capture `requirements.txt`                             | 1:28  | 1:31 | 3              | Share                 |       |
| 8     | A       | Sharing   | 5    | Document seeds                                         | 1:38  | 1:40 | 2              | Share                 |       |
| 8     | A       | Sharing   | 6    | Document environment                                   | 1:40  | 2:43 | 63             | Share                 |       |
| 8     | A       | Sharing   | 7    | Package bundle (`zip -r`)                              | 2:49  | 2:51 | 2              | Share                 |       |
| 8     | A       | Sharing   | 8    | Transfer bundle to `/Users/Shared/srq5-transfer`       | 2:57  | 3:47 | 50             | Share                 |       |
| 8     | B       | Receiving | 1    | Unpack bundle (`unzip`)                                | 0:15  | 0:39 | 24             | First-Run, Reproduce  |       |
| 8     | B       | Receiving | 2    | Read `README.md`                                       | 0:47  | 0:48 | 1              | First-Run, Reproduce  |       |
| 8     | B       | Receiving | 3    | Install/verify dependencies (`pip install -r ...`)     | 0:56  | 0:58 | 2              | First-Run, Reproduce  |       |
| 8     | B       | Receiving | 4    | Copy received files into checkout                      | 1:03  | 1:04 | 1              | First-Run, Reproduce  |       |
| 8     | B       | Receiving | 5    | Run experiment (`PYTHONPATH=src python ...`)           | 1:12  | 1:43 | 31             | First-Run, Reproduce  |       |
| 8     | B       | Receiving | 6    | Compare results (TensorBoard/manual check)             | 1:44  | 2:44 | 60             | Reproduce             |       |
| 9     | A       | Sharing   | 1    | Identify files (`ls ...`)                              | 0:33  | 0:34 | 1              | Share                 |       |
| 9     | A       | Sharing   | 2    | Stage share files (`mkdir -p`, `cp`, `cp -r`)          | 0:42  | 1:27 | 45             | Share                 |       |
| 9     | A       | Sharing   | 3    | Write `README.md`                                      | 1:36  | 1:37 | 1              | Share                 |       |
| 9     | A       | Sharing   | 4    | Capture `requirements.txt`                             | 1:44  | 1:47 | 3              | Share                 |       |
| 9     | A       | Sharing   | 5    | Document seeds                                         | 1:53  | 1:54 | 1              | Share                 |       |
| 9     | A       | Sharing   | 6    | Document environment                                   | 1:54  | 2:41 | 47             | Share                 |       |
| 9     | A       | Sharing   | 7    | Package bundle (`zip -r`)                              | 2:47  | 2:48 | 1              | Share                 |       |
| 9     | A       | Sharing   | 8    | Transfer bundle to `/Users/Shared/srq5-transfer`       | 2:56  | 3:03 | 7              | Share                 |       |
| 9     | B       | Receiving | 1    | Unpack bundle (`unzip`)                                | 0:02  | 0:21 | 19             | First-Run, Reproduce  |       |
| 9     | B       | Receiving | 2    | Read `README.md`                                       | 0:28  | 0:31 | 3              | First-Run, Reproduce  |       |
| 9     | B       | Receiving | 3    | Install/verify dependencies (`pip install -r ...`)     | 0:33  | 0:34 | 1              | First-Run, Reproduce  |       |
| 9     | B       | Receiving | 4    | Copy received files into checkout                      | 0:42  | 0:45 | 3              | First-Run, Reproduce  |       |
| 9     | B       | Receiving | 5    | Run experiment (`PYTHONPATH=src python ...`)           | 0:51  | 1:19 | 28             | First-Run, Reproduce  |       |
| 9     | B       | Receiving | 6    | Compare results (TensorBoard/manual check)             | 1:19  | 2:07 | 48             | Reproduce             |       |
| 10    | A       | Sharing   | 1    | Identify files (`ls ...`)                              | 0:36  | 0:37 | 1              | Share                 |       |
| 10    | A       | Sharing   | 2    | Stage share files (`mkdir -p`, `cp`, `cp -r`)          | 0:46  | 0:57 | 11             | Share                 |       |
| 10    | A       | Sharing   | 3    | Write `README.md`                                      | 1:05  | 1:06 | 1              | Share                 |       |
| 10    | A       | Sharing   | 4    | Capture `requirements.txt`                             | 1:13  | 1:14 | 1              | Share                 |       |
| 10    | A       | Sharing   | 5    | Document seeds                                         | 1:21  | 1:22 | 1              | Share                 |       |
| 10    | A       | Sharing   | 6    | Document environment                                   | 1:22  | 2:02 | 40             | Share                 |       |
| 10    | A       | Sharing   | 7    | Package bundle (`zip -r`)                              | 2:05  | 2:08 | 3              | Share                 |       |
| 10    | A       | Sharing   | 8    | Transfer bundle to `/Users/Shared/srq5-transfer`       | 2:10  | 2:17 | 7              | Share                 |       |
| 10    | B       | Receiving | 1    | Unpack bundle (`unzip`)                                | 0:00  | 0:15 | 15             | First-Run, Reproduce  |       |
| 10    | B       | Receiving | 2    | Read `README.md`                                       | 0:18  | 0:22 | 4              | First-Run, Reproduce  |       |
| 10    | B       | Receiving | 3    | Install/verify dependencies (`pip install -r ...`)     | 0:23  | 0:24 | 1              | First-Run, Reproduce  |       |
| 10    | B       | Receiving | 4    | Copy received files into checkout                      | 0:29  | 0:31 | 2              | First-Run, Reproduce  |       |
| 10    | B       | Receiving | 5    | Run experiment (`PYTHONPATH=src python ...`)           | 0:36  | 1:04 | 28             | First-Run, Reproduce  |       |
| 10    | B       | Receiving | 6    | Compare results (TensorBoard/manual check)             | 1:05  | 1:39 | 34             | Reproduce             |       |

#### Margos Workflow Raw Command Timestamps

Use one row per documented protocol step. For Margos trials, exclude Step 0 from all measured totals, sum Step 1 for `Time-to-Share`, sum Steps 3-4 for `Time-to-First-Run`, and sum Steps 3-5 for `Time-to-Reproduce`.

| Trial | Machine | Phase     | Step | Command / Action                                   | Start | End  | Duration (sec) | Included In           | Notes                                              |
| ----- | ------- | --------- | ---- | -------------------------------------------------- | ----- | ---- | -------------- | --------------------- | -------------------------------------------------- |
| 1     | A       | Pre-trial | 0    | Reference run (`margos run srq5_eval`)           | 0:11  | 0:45 | 34             | No                    |                                                    |
| 1     | A       | Sharing   | 1    | Export bundle (`margos export ...`)              | 0:46  | 1:43 | 57             | Share                 |                                                    |
| 1     | B       | Receiving | 3    | Import bundle (`margos import ...`)              | 0:11  | 0:47 | 36             | First-Run, Reproduce  |                                                    |
| 1     | B       | Receiving | 4    | Run imported experiment (`margos run srq5_eval`) | 0:48  | 1:22 | 34             | First-Run, Reproduce  |                                                    |
| 1     | B       | Receiving | 5    | Verify reproduction (`margos compare ...`)       | 1:23  | 1:33 | 10             | Reproduce             |                                                    |
| 2     | A       | Pre-trial | 0    | Reference run (`margos run srq5_eval`)           | 0:11  | 0:45 | 34             | No                    |                                                    |
| 2     | A       | Sharing   | 1    | Export bundle (`margos export ...`)              | 0:46  | 1:45 | 59             | Share                 |                                                    |
| 2     | B       | Receiving | 3    | Import bundle (`margos import ...`)              | 0:04  | 0:09 | 5              | First-Run, Reproduce  |                                                    |
| 2     | B       | Receiving | 4    | Run imported experiment (`margos run srq5_eval`) | 0:10  | 0:44 | 34             | First-Run, Reproduce  |                                                    |
| 2     | B       | Receiving | 5    | Verify reproduction (`margos compare ...`)       | 0:45  | 0:53 | 8              | Reproduce             |                                                    |
| 3     | A       | Pre-trial | 0    | Reference run (`margos run srq5_eval`)           | 0:18  | 0:52 | 34             | No                    |                                                    |
| 3     | A       | Sharing   | 1    | Export bundle (`margos export ...`)              | 0:53  | 1:22 | 29             | Share                 |                                                    |
| 3     | B       | Receiving | 3    | Import bundle (`margos import ...`)              | 0:03  | 0:29 | 26             | First-Run, Reproduce  |                                                    |
| 3     | B       | Receiving | 4    | Run imported experiment (`margos run srq5_eval`) | 0:30  | 1:04 | 34             | First-Run, Reproduce  |                                                    |
| 3     | B       | Receiving | 5    | Verify reproduction (`margos compare ...`)       | 1:05  | 1:22 | 17             | Reproduce             |                                                    |
| 4     | A       | Pre-trial | 0    | Reference run (`margos run srq5_eval`)           | 0:14  | 0:48 | 34             | No                    |                                                    |
| 4     | A       | Sharing   | 1    | Export bundle (`margos export ...`)              | 0:49  | 1:13 | 24             | Share                 |                                                    |
| 4     | B       | Receiving | 3    | Import bundle (`margos import ...`)              | 0:00  | 0:21 | 21             | First-Run, Reproduce  |                                                    |
| 4     | B       | Receiving | 4    | Run imported experiment (`margos run srq5_eval`) | 0:22  | 0:56 | 34             | First-Run, Reproduce  |                                                    |
| 4     | B       | Receiving | 5    | Verify reproduction (`margos compare ...`)       | 0:57  | 1:05 | 8              | Reproduce             |                                                    |
| 5     | A       | Pre-trial | 0    | Reference run (`margos run srq5_eval`)           | 0:00  | 0:34 | 34             | No                    |                                                    |
| 5     | A       | Sharing   | 1    | Export bundle (`margos export ...`)              | 0:35  | 0:50 | 15             | Share                 |                                                    |
| 5     | B       | Receiving | 3    | Import bundle (`margos import ...`)              | 0:00  | 0:24 | 24             | First-Run, Reproduce  |                                                    |
| 5     | B       | Receiving | 4    | Run imported experiment (`margos run srq5_eval`) | 0:25  | 0:59 | 34             | First-Run, Reproduce  |                                                    |
| 5     | B       | Receiving | 5    | Verify reproduction (`margos compare ...`)       | 1:00  | 1:07 | 7              | Reproduce             |                                                    |
| 6     | A       | Pre-trial | 0    | Reference run (`margos run srq5_eval`)           | 0:14  | 0:48 | 34             | No                    |                                                    |
| 6     | A       | Sharing   | 1    | Export bundle (`margos export ...`)              | 0:49  | 1:47 | 58             | Share                 |                                                    |
| 6     | B       | Receiving | 3    | Import bundle (`margos import ...`)              | 0:08  | 0:47 | 39             | First-Run, Reproduce  |                                                    |
| 6     | B       | Receiving | 4    | Run imported experiment (`margos run srq5_eval`) | 0:48  | 1:22 | 34             | First-Run, Reproduce  |                                                    |
| 6     | B       | Receiving | 5    | Verify reproduction (`margos compare ...`)       | 1:23  | 1:32 | 9              | Reproduce             |                                                    |
| 7     | A       | Pre-trial | 0    | Reference run (`margos run srq5_eval`)           | 0:08  | 0:42 | 34             | No                    |                                                    |
| 7     | A       | Sharing   | 1    | Export bundle (`margos export ...`)              | 0:43  | 1:40 | 57             | Share                 |                                                    |
| 7     | B       | Receiving | 3    | Import bundle (`margos import ...`)              | 0:05  | 0:08 | 3              | First-Run, Reproduce  |                                                    |
| 7     | B       | Receiving | 4    | Run imported experiment (`margos run srq5_eval`) | 0:09  | 0:43 | 34             | First-Run, Reproduce  |                                                    |
| 7     | B       | Receiving | 5    | Verify reproduction (`margos compare ...`)       | 0:44  | 0:53 | 9              | Reproduce             |                                                    |
| 8     | A       | Pre-trial | 0    | Reference run (`margos run srq5_eval`)           | 0:15  | 0:49 | 34             | No                    |                                                    |
| 8     | A       | Sharing   | 1    | Export bundle (`margos export ...`)              | 0:50  | 1:22 | 32             | Share                 |                                                    |
| 8     | B       | Receiving | 3    | Import bundle (`margos import ...`)              | 0:01  | 0:30 | 29             | First-Run, Reproduce  |                                                    |
| 8     | B       | Receiving | 4    | Run imported experiment (`margos run srq5_eval`) | 0:31  | 1:05 | 34             | First-Run, Reproduce  |                                                    |
| 8     | B       | Receiving | 5    | Verify reproduction (`margos compare ...`)       | 1:06  | 1:21 | 15             | Reproduce             |                                                    |
| 9     | A       | Pre-trial | 0    | Reference run (`margos run srq5_eval`)           | 0:17  | 0:51 | 34             | No                    |                                                    |
| 9     | A       | Sharing   | 1    | Export bundle (`margos export ...`)              | 0:52  | 1:17 | 25             | Share                 |                                                    |
| 9     | B       | Receiving | 3    | Import bundle (`margos import ...`)              | 0:03  | 0:23 | 20             | First-Run, Reproduce  |                                                    |
| 9     | B       | Receiving | 4    | Run imported experiment (`margos run srq5_eval`) | 0:24  | 0:58 | 34             | First-Run, Reproduce  |                                                    |
| 9     | B       | Receiving | 5    | Verify reproduction (`margos compare ...`)       | 0:59  | 1:04 | 5              | Reproduce             |                                                    |
| 10    | A       | Pre-trial | 0    | Reference run (`margos run srq5_eval`)           | 0:02  | 0:36 | 34             | No                    |                                                    |
| 10    | A       | Sharing   | 1    | Export bundle (`margos export ...`)              | 0:37  | 0:55 | 18             | Share                 |                                                    |
| 10    | B       | Receiving | 3    | Import bundle (`margos import ...`)              | 0:00  | 0:22 | 22             | First-Run, Reproduce  |                                                    |
| 10    | B       | Receiving | 4    | Run imported experiment (`margos run srq5_eval`) | 0:23  | 0:57 | 34             | First-Run, Reproduce  |                                                    |
| 10    | B       | Receiving | 5    | Verify reproduction (`margos compare ...`)       | 0:58  | 1:07 | 9              | Reproduce             |                                                    |
| 0     | A       | Pre-trial | 0    | Reference run (`margos run srq5_eval`)           | 0:07  | 0:41 | 34             | No                    | reference 34s deterministic training run           |
| 0     | A       | Sharing   | 1    | Export bundle (`margos export ...`)              | 0:42  | 0:59 | 17             | Share                 |                                                    |
| 0     | B       | Receiving | 3    | Import bundle (`margos import ...`)              | 0:05  | 0:27 | 22             | First-Run, Reproduce  |                                                    |
| 0     | B       | Receiving | 4    | Run imported experiment (`margos run srq5_eval`) | 0:28  | 1:02 | 34             | First-Run, Reproduce  | reference 34s deterministic training run           |
| 0     | B       | Receiving | 5    | Verify reproduction (`margos compare ...`)       | 1:03  | 1:17 | 14             | Reproduce             |                                                    |

Trial `0` is the reference baseline showing the deterministic 34s training run reflected in the recorded handoff trials.

### Bundle Completeness Checklist

For each bundle (Margos condition), audit contents:

| Component            | Required?   | Present?   |
| -------------------- | ----------- | ---------- |
| Config file (frozen) | Yes         | Y/N        |
| Seeds documented     | Yes         | Y/N        |
| Env fingerprint      | Yes         | Y/N        |
| Training script      | Yes         | Y/N        |
| ARGoS scenario file  | Yes         | Y/N        |
| Logs (metrics.jsonl) | Yes         | Y/N        |
| Checkpoints          | Optional    | Y/N        |
| Manifest             | Yes         | Y/N        |

**Bundle-Completeness Score: ___/7 required, ___/8 total**

### Setup Divergence Analysis

Compare Machine A and Machine B environments:

| Field            | Machine A   | Machine B   | Match?   |
| ---------------- | ----------- | ----------- | -------- |
| Python version   |             |             | Y/N      |
| OS               |             |             | Y/N      |
| Margos version |             |             | Y/N      |
| RLlib version    |             |             | Y/N      |
| PyTorch version  |             |             | Y/N      |
| NumPy version    |             |             | Y/N      |
| Config hash      |             |             | Y/N      |

### Error Log (for failed handoffs)

| Trial   | Condition   | Error Type   | Error Description   | Resolution   |
| ------- | ----------- | ------------ | ------------------- | ------------ |

---

## Analysis

Derived cross-trial statistics and interpretation are maintained in [analysis_summary.md](../evidence/SRQ5/analysis_summary.md). Keep the per-trial data above as the evidence source for those calculations.

The timing metrics below are computed from the recorded handoff trials documented in the timestamp table above.

### Primary Metrics (M5.1-M5.7)

| Metric                     | Manual (Mean ± SD)  | Margos (Mean ± SD)  | Reduction (%)   | Target         |
| -------------------------- | ------------------- | --------------------- | --------------- | -------------- |
| M5.1: Steps-to-Share       | 8 (fixed)           | 1 (fixed)             | 87.5%           | ≥50% reduction |
| M5.2: Time-to-Share        | 107.7 ± 24.1 sec    | 37.4 ± 18.2 sec       | 65.3%           | ≥50% reduction |
| M5.3: Time-to-First-Run    | 52.6 ± 11.4 sec     | 56.5 ± 11.6 sec       | -7.4%           | ≥50% reduction |
| M5.4: Time-to-Reproduce    | 122.3 ± 30.3 sec    | 66.2 ± 13.1 sec       | 45.9%           | ≥50% reduction |
| M5.5: Handoff-Success-Rate | 100% (10/10)        | 100% (10/10)          | —               | ≥90%           |

### Secondary Metrics

| Metric                                   | Value          | Notes                                                                                                                                 |
| ---------------------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| M5.6: Bundle-Completeness                | 8/8            | All required and optional components are present in the retained SRQ5 export bundle; recordings show the same structure across trials |
| M5.7: Setup-Divergence (mean mismatches) | 3.0 mismatches | Recording comparison output shows mismatches on NumPy, PettingZoo, and PyTorch, while Python, OS, Gymnasium, Pydantic, and Ray match  |

### Success Rate Calculation

```
Handoff-Success-Rate = (# successful handoffs) / (total handoffs) × 100%
```

A handoff is **successful** if Researcher B's final episode reward mean (last 50 episodes) is within ±1% of Researcher A's reference value (see Handoff Success Definition above).

### Time Reduction Calculation

```
Time-to-Share Reduction = (Manual_mean - Margos_mean) / Manual_mean × 100%
Time-to-First-Run Reduction = (Manual_mean - Margos_mean) / Manual_mean × 100%
Time-to-Reproduce Reduction = (Manual_mean - Margos_mean) / Manual_mean × 100%
```

### Interpretation Guidelines

| Outcome                                               | Interpretation                            |
| ----------------------------------------------------- | ----------------------------------------- |
| High success rate (≥90%) + significant time reduction | H5 strongly supported                     |
| High success rate + moderate time reduction           | H5 supported                              |
| High success rate + mixed timing results              | H5 partially supported                    |
| Low success rate regardless of time                   | H5 not supported                          |
| Ceiling effect (100% both conditions)                 | Focus on time metrics for differentiation |

### Failure Mode Analysis

If Handoff-Success-Rate < 100%, categorize failures:

| Failure Mode           | Count   | Cause   |
| ---------------------- | ------- | ------- |
| Missing dependency     |         |         |
| Config incompatibility |         |         |
| Environment mismatch   |         |         |
| Data corruption        |         |         |
| Other                  |         |         |

---

## Evidence Checklist

- [x] Screen recordings of all trials
- [x] Per-trial data complete
- [x] Bundle completeness audit for Margos trials
- [x] Setup divergence analysis for each trial
- [x] Error log documented: no failed handoffs or recorded trial errors occurred, so `error_log.csv` is intentionally header-only
- [x] Environment specifications documented

All 20 trials completed successfully; no failed handoffs or recorded trial errors occurred.

### Required Evidence Files

| File                      | Description                                                              |
| ------------------------- | ------------------------------------------------------------------------ |
| `trial_01_manual.mp4` ... | Screen recordings                                                        |
| `trial_data.csv`          | All timing and step data                                                 |
| `bundle_audits.csv`       | Bundle completeness for each Margos trial                              |
| `env_comparisons.csv`     | Machine A vs B environment data                                          |
| `error_log.csv`           | Error log artifact; intentionally empty because no trial errors occurred |
| `analysis_summary.md`     | Computed statistics                                                      |

### Simulation Environment Documentation

| Field             | Value                                                                            |
| ----------------- | -------------------------------------------------------------------------------- |
| Simulation method | Dedicated macOS account                                                          |
| Base environment  | `researcherb` account with fixed repos and `~/.venvs/srq5`                       |
| Transfer path     | `/Users/Shared/srq5-transfer`                                                    |
| Network isolation | No direct access to Machine A working directories; transfer-only artifact access |

---

## Limitations

| Limitation                                              | Mitigation                                                                                                                                                                                                           |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Researcher B is simulated                               | Explicitly acknowledge - measures technical enablement, not social/communication aspects                                                                                                                             |
| Same hardware for A and B                               | Document hardware specification                                                                                                                                                                                      |
| Prepared collaborator environment, not cold-start setup | State explicitly that base infrastructure is amortized and outside SRQ5 timing scope                                                                                                                                 |
| Transfer time not included                              | Focus on preparation and reproduction time                                                                                                                                                                           |
| Limited trial count                                     | Report confidence intervals                                                                                                                                                                                          |
| Time metrics measured by Margos developer             | Times represent a lower bound - a naive researcher would take longer on Margos condition. Direction of comparison is preserved (same evaluator for both conditions); absolute times should not be generalized. |

### Note on Simulation

Researcher B is simulated using a dedicated local macOS account with an isolated home directory, fixed repo copies, a shared SRQ5 virtualenv, and transfer-only artifact access via `/Users/Shared/srq5-transfer`. This measures **technical collaboration enablement** on a prepared collaborator workstation, but not social/communication aspects of collaboration or first-time machine provisioning effort.

---

## Distinction from SRQ3

| Aspect       | SRQ3: Reproducibility                     | SRQ5: Collaboration                          |
| ------------ | ----------------------------------------- | -------------------------------------------- |
| Perspective  | Self-reproducibility                      | Cross-environment handoff                    |
| Who          | Same researcher                           | Simulated "other researcher"                 |
| Where        | Same environment                          | Different environment                        |
| Question     | "Do I get same results when I run again?" | "Can someone else pick up where I left off?" |
| Focus        | Determinism, variance, correctness        | Portability, bundling, friction reduction    |
| Failure Mode | Non-deterministic results, config drift   | Missing dependencies, incomplete bundles     |

---

## References

- `docs/CollabBrainstorm.md` - Full rationale and decisions
- `docs/ResearchPlan.md` - SRQ5, H5, E5 definitions
