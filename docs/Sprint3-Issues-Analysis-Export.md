# Sprint 3 Plan: Analysis & Export Systems

## Sprint Overview

| Attribute | Value |
|-----------|-------|
| Sprint | 3 |
| Focus | Analysis + Export Systems |
| Goal | `platform report` and `platform export/import` fully functional |
| Entry Criteria | Sprint 2 complete - `platform run` produces results with logs |
| Target | All 15 Must requirements satisfied |

---

## Exit Criteria

- [ ] `platform report <exp>` generates learning curve plot + summary
- [ ] `platform report <exp> --reference <ref>` compares runs (±1% tolerance)
- [ ] `platform export <exp>` creates shareable `bundle.zip`
- [ ] `platform import bundle.zip` unpacks and shows fingerprint comparison
- [ ] All 15 Must requirements satisfied

---

## Requirements Coverage (Sprint 3 Focus)

| Requirement | Description | Status | Sprint 3 Action |
|-------------|-------------|--------|-----------------|
| R2.5 | `report` command | Stub | **Implement** |
| R3.2 | Reproducibility comparison | Missing | **Implement** |
| R5.1 | `export` command | Stub | **Implement** |
| R5.2 | `import` command | Stub | **Implement** |
| R5.3 | Bundle format | Missing | **Implement** |
| R5.4 | Env-fingerprint comparison | Partial | **Complete** |

---

## Architecture Reference

### Analysis System (from LowLevelArchitectureBrainstorm.md)

**Files:** `analysis/report.py`, `analysis/compare.py`

**Interfaces:**
```python
# analysis/report.py
def generate_report(experiment_dir: str, reference_dir: str = None) -> str:
    """Generate analysis report for experiment."""
    pass

def plot_learning_curve(log_path: str, output_path: str):
    """Generate learning curve plot from metrics log."""
    pass
```

```python
# analysis/compare.py
def compare_runs(run_dir: str, reference_dir: str, tolerance: float = 0.01) -> dict:
    """
    Compare run against reference for reproducibility (M3.1).

    Returns:
        {
            "final_reward_match": bool,
            "final_reward_deviation": float,
            "auc_match": bool,
            "auc_deviation": float,
            "passed": bool  # both within tolerance
        }
    """
    pass

def calculate_auc(log_path: str) -> float:
    """Calculate area under learning curve."""
    pass
```

### Export System (from LowLevelArchitectureBrainstorm.md)

**Files:** `export/bundle.py`, `export/importer.py`

**Bundle Format:**
```
bundle.zip
├── manifest.yaml         # Bundle metadata
├── config.yaml           # Frozen experiment config
├── scenario.argos        # Copy of scenario file
├── train.py              # Copy of training script
├── env_fingerprint.yaml  # Environment metadata
├── logs/
│   └── metrics.jsonl
└── checkpoints/          # Optional (included by default - L5)
```

**Interfaces:**
```python
# export/bundle.py
def export_bundle(experiment_dir: str, output_path: str = None) -> str:
    """Create shareable bundle from experiment."""
    pass

def create_manifest(experiment_dir: str) -> dict:
    """Create bundle manifest with metadata."""
    pass
```

```python
# export/importer.py
def import_bundle(bundle_path: str, target_dir: str = None) -> str:
    """Import bundle and prepare for reproduction."""
    pass

def compare_fingerprints(bundle_fp: dict, current_fp: dict) -> dict:
    """
    Compare environment fingerprints.
    Returns: {field: (bundle_value, current_value, match)}
    """
    pass
```

---

## Issue Breakdown

### Issue 1: Learning Curve Plot Generation

**Requirement:** R2.5 (partial)
**Component:** Analysis System
**File:** `analysis/report.py`

**Acceptance Criteria:**
- [ ] Read `metrics.jsonl` from experiment directory
- [ ] Extract `iteration` and `episode_reward_mean` fields
- [ ] Generate matplotlib plot with:
  - X-axis: iteration
  - Y-axis: episode_reward_mean
  - Title: experiment name
  - Grid enabled
- [ ] Save as PNG to `results/<exp>/report/learning_curve.png`
- [ ] Handle missing data gracefully (error message if log empty)

**Technical Notes:**
- Plotting library: matplotlib (Decision L6)
- Output: thesis-ready PNG

---

### Issue 2: Report Summary Generation

**Requirement:** R2.5 (partial)
**Component:** Analysis System
**File:** `analysis/report.py`

**Acceptance Criteria:**
- [ ] Generate `summary.txt` containing:
  - Experiment name
  - Config hash
  - Total iterations
  - Final reward (last entry)
  - Best reward (max)
  - AUC (area under learning curve)
  - Training duration (first to last timestamp)
- [ ] Save to `results/<exp>/report/summary.txt`

**Technical Notes:**
- AUC: trapezoidal integration (np.trapz)
- Duration: parse ISO timestamps from log

---

### Issue 3: Reproducibility Comparison

**Requirement:** R3.2
**Component:** Analysis System
**File:** `analysis/compare.py`

**Acceptance Criteria:**
- [ ] `compare_runs(run_dir, reference_dir, tolerance=0.01)` returns comparison dict
- [ ] Compare final reward: `|run - ref| / ref <= tolerance`
- [ ] Compare AUC: `|run - ref| / ref <= tolerance`
- [ ] Return structured result:
  ```python
  {
      "final_reward_match": bool,
      "final_reward_deviation": float,  # as percentage
      "auc_match": bool,
      "auc_deviation": float,  # as percentage
      "passed": bool  # both within tolerance
  }
  ```
- [ ] Handle edge cases: missing reference, empty logs

**Technical Notes:**
- Tolerance: ±1% (Decision D1 from ReproBrainstorm)
- Both conditions must pass for `passed=True`

---

### Issue 4: Export Bundle Creation

**Requirement:** R5.1, R5.3
**Component:** Export System
**File:** `export/bundle.py`

**Acceptance Criteria:**
- [ ] `export_bundle(experiment_dir)` creates `bundles/<exp_name>.zip`
- [ ] Bundle contains:
  - [ ] `manifest.yaml` with metadata (export timestamp, platform version)
  - [ ] `config.yaml` (frozen copy from experiment)
  - [ ] `scenario.argos` (resolved from config, copied)
  - [ ] `train.py` (resolved from config, copied)
  - [ ] `env_fingerprint.yaml`
  - [ ] `logs/metrics.jsonl`
  - [ ] `checkpoints/` (if present, include by default - L5)
- [ ] Create `bundles/` directory if not exists
- [ ] Return path to created bundle

**Technical Notes:**
- Compression: standard ZIP deflate
- Resolve relative paths from config to copy source files

---

### Issue 5: Import Bundle Unpacking

**Requirement:** R5.2
**Component:** Export System
**File:** `export/importer.py`

**Acceptance Criteria:**
- [ ] `import_bundle(bundle_path)` extracts to `experiments/imported/<exp_name>/`
- [ ] Validate bundle structure (manifest, config, required files)
- [ ] Extract all contents preserving directory structure
- [ ] Return path to imported experiment directory
- [ ] Handle invalid bundles gracefully (clear error message)

**Technical Notes:**
- Target directory: `experiments/imported/` (separate from user experiments)

---

### Issue 6: Fingerprint Comparison on Import

**Requirement:** R5.4
**Component:** Export System
**File:** `export/importer.py`

**Acceptance Criteria:**
- [ ] `compare_fingerprints(bundle_fp, current_fp)` returns comparison dict
- [ ] Compare fields:
  - Python version
  - OS
  - Key packages (rllib, torch, numpy)
- [ ] Return structured result:
  ```python
  {
      "python": ("3.10.0", "3.10.1", False),  # (bundle, current, match)
      "os": ("Linux", "Linux", True),
      "packages": {
          "rllib": ("2.0.0", "2.0.0", True),
          ...
      }
  }
  ```
- [ ] Display comparison table in CLI after import
- [ ] Warn on mismatches but do not block import

**Technical Notes:**
- User decides action based on comparison (no automated handling)
- Display format: table with match/mismatch indicators

---

### Issue 7: CLI Integration (Remove Stubs)

**Requirement:** R2.5, R5.1, R5.2
**Component:** CLI
**File:** `cli.py`

**Acceptance Criteria:**
- [ ] `platform report <exp>` calls `generate_report()`
  - [ ] `--reference <ref>` option for comparison
  - [ ] Display summary in terminal
  - [ ] Show comparison result if reference provided
- [ ] `platform export <exp>` calls `export_bundle()`
  - [ ] `--output <path>` option for custom output path
  - [ ] Display success message with bundle path
- [ ] `platform import <bundle>` calls `import_bundle()`
  - [ ] Display fingerprint comparison table
  - [ ] Show path to imported experiment
- [ ] All commands have `--help` with usage examples (R4.3)
- [ ] Clear error messages on failure (R4.2, L8)

**Technical Notes:**
- Error format: message + context + fix suggestion (Decision L8)
- Convention over configuration: user provides names, platform resolves paths (L7)

---

## Implementation Order

```
1. Issue 1: Learning curve plot
   └── Enables basic `platform report`

2. Issue 2: Report summary
   └── Completes `platform report` without comparison

3. Issue 3: Reproducibility comparison
   └── Enables `platform report --reference`

4. Issue 4: Export bundle creation
   └── Enables `platform export`

5. Issue 5: Import bundle unpacking
   └── Enables `platform import`

6. Issue 6: Fingerprint comparison
   └── Completes import with env comparison

7. Issue 7: CLI integration
   └── Wire everything together, remove stubs
```

---

## SRQ Coverage After Sprint 3

### SRQ2 (Efficiency)
- R2.5 `report` command: **Complete** (Issues 1, 2, 7)

### SRQ3 (Reproducibility)
- R3.2 Reproducibility comparison: **Complete** (Issue 3)

### SRQ5 (Collaboration)
- R5.1 `export` command: **Complete** (Issue 4, 7)
- R5.2 `import` command: **Complete** (Issue 5, 7)
- R5.3 Bundle format: **Complete** (Issue 4)
- R5.4 Env-fingerprint comparison: **Complete** (Issue 6)

---

## Risks

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| R1 | Large checkpoints slow export/import | Medium | Optional flag to exclude checkpoints |
| R2 | Path resolution complexity | Medium | Test with various directory structures |
| R3 | Cross-platform fingerprint differences | Low | Document expected differences (OS, paths) |

---

## Definition of Done

Sprint 3 is complete when:

1. **All 7 issues** have passing acceptance criteria
2. **Exit criteria** met:
   - `platform report exp_001` generates `learning_curve.png` + `summary.txt`
   - `platform report exp_001 --reference exp_000` shows ±1% comparison
   - `platform export exp_001` creates `bundles/exp_001.zip`
   - `platform import bundles/exp_001.zip` unpacks and shows fingerprint comparison
3. **All 15 Must requirements** satisfied
4. **Integration test**: Full workflow runs without manual intervention
   - `platform run` → `platform report` → `platform export` → `platform import`

---

## Files to Create/Modify

| File | Action | Issue |
|------|--------|-------|
| `analysis/__init__.py` | Create | - |
| `analysis/report.py` | Create | 1, 2 |
| `analysis/compare.py` | Create | 3 |
| `export/__init__.py` | Create | - |
| `export/bundle.py` | Create | 4 |
| `export/importer.py` | Create | 5, 6 |
| `cli.py` | Modify | 7 |

---

## Decisions Made (This Document)

| # | Decision | Details |
|---|----------|---------|
| S3.1 | Implementation order | Analysis → Export → CLI (dependencies) |
| S3.2 | Bundle includes checkpoints | By default (per L5) |
| S3.3 | Import target | `experiments/imported/` directory |
