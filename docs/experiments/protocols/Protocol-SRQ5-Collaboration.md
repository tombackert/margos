# Protocol-SRQ5-Collaboration

## Header

| Field | Value |
|-------|-------|
| **Protocol ID** | P-SRQ5 |
| **SRQ Reference** | SRQ5: To what extent does the platform enable reliable reproduction of experiments across different research environments and by how much does it decrease time-to-reproduce? |
| **Hypothesis** | H5: The platform's export/import mechanism significantly reduces sharing effort (Steps-to-Share, Time-to-Share) and receiving effort (Time-to-First-Run, Time-to-Reproduce) compared to manual experiment handoff, while maintaining high Handoff Success Rate. |
| **Success Criteria** | Significant reduction in sharing/receiving effort, Handoff-Success-Rate high |
| **Sample Size** | N=20 total for Handoff-Success-Rate (10 manual + 10 platform); N=10 per condition for timed trials (N raised to 20 in EvalPlanOverview for consistency with SRQ3; all 10 platform trials include timing automatically) |
| **Dependencies** | Platform export/import implemented, isolated environment prepared |

---

## Prerequisites

### Required Artifacts
- [ ] Platform CLI operational (`export`, `import`, `run`)
- [ ] Completed experiment ready for export
- [ ] Isolated environment for "Researcher B" simulation
- [ ] Screen recording software
- [ ] Timer/stopwatch

### Environment Setup

**Machine A (Researcher A):**
- [ ] Platform installed
- [ ] Completed experiment in results directory

**Machine B (Simulated Researcher B):**
- [ ] Fresh environment (one of the following):
  - [ ] Docker container with only base dependencies
  - [ ] Fresh VM
  - [ ] New user profile / fresh directory
- [ ] No pre-existing platform data
- [ ] Network isolation from Machine A's filesystem

### Pre-Execution Checklist
- [ ] Baseline workflow steps documented (8 steps)
- [ ] Platform workflow steps documented (4 steps)
- [ ] Transfer mechanism decided (e.g., file copy, simulated network transfer)
- [ ] Researcher B environment specification documented

---

## Definitions

### Key Terms

| Term | Definition |
|------|------------|
| **Researcher A** | Entity that creates and shares the experiment |
| **Researcher B** | Entity that receives and reproduces the experiment (simulated) |
| **Handoff** | Complete process from A sharing to B reproducing |
| **Steps-to-Share** | Manual actions required to prepare experiment for sharing |
| **Time-to-Share** | Time from "I want to share" to "bundle ready for transfer" |
| **Time-to-First-Run** | Time from "bundle received" to "first successful execution" |
| **Time-to-Reproduce** | Time from "bundle received" to "results verified as matching" |
| **Handoff-Success-Rate** | % of handoffs where B successfully reproduces A's results |
| **Bundle-Completeness** | Checklist score of required components present in bundle |
| **Setup-Divergence** | Differences between A's and B's environment configurations |

### Measurement Triggers

| Metric | Start Trigger | Stop Trigger |
|--------|---------------|--------------|
| Time-to-Share | Decision made to share ("I want to share this") | Shareable artifact ready (zip/bundle created) |
| Time-to-First-Run | Bundle received on Machine B | First successful execution (any output produced) |
| Time-to-Reproduce | Bundle received on Machine B | Results verified as matching (comparison passes) |
| Steps-to-Share | First action toward sharing | Artifact ready for transfer |

### Controlled Variables

| Variable | How Controlled |
|----------|----------------|
| Experiment being shared | Same experiment for all trials |
| Transfer mechanism | Consistent (e.g., file copy) |
| Machine B specification | Same container image / VM config |
| Pre-installed dependencies | None on Machine B (fresh environment) |

---

## Procedure

### Condition A: Manual Workflow (Baseline)

**Total steps: 8**

| Step | Action | Description |
|------|--------|-------------|
| 1 | Identify files | Determine which files are needed (configs, scripts, models) |
| 2 | Copy files to staging | Manually copy relevant files to a shareable location |
| 3 | Write README | Document setup instructions, dependencies, how to run |
| 4 | List dependencies | Create requirements.txt or equivalent manually |
| 5 | Document seeds | Write down seed values used in experiment |
| 6 | Document environment | Note Python version, OS, relevant env variables |
| 7 | Package files | Zip or tar the files for transfer |
| 8 | Transfer | Send via file copy (simulated) |

**Receiving (Baseline):**
| Step | Action |
|------|--------|
| 1 | Unpack files |
| 2 | Read README |
| 3 | Install dependencies |
| 4 | Configure environment |
| 5 | Run experiment |
| 6 | Compare results (manual) |

### Condition B: Platform Workflow

**Sharing (Platform):**
```bash
# Step 1: Export
platform export exp_123 --output bundle.zip
```

**Transfer:**
```bash
# Step 2: Copy bundle to Machine B
cp bundle.zip /path/to/machine_b/
```

**Receiving (Platform):**
```bash
# Step 3: Import
platform import bundle.zip

# Step 4: Reproduce
platform run exp_123

# Step 5: Verify
platform compare exp_123 results/reference/
```

**Total platform steps: 5**

### Researcher B Simulation Setup

Create isolated environment before each trial:

```bash
# Option 1: Docker
docker run -it --rm -v /path/to/bundles:/bundles base_image:latest

# Option 2: Fresh directory
mkdir -p ~/research_b_trial_N
cd ~/research_b_trial_N

# Option 3: VM snapshot
# Restore VM to clean snapshot before each trial
```

### Trial Protocol

For each trial:

1. **Prepare fresh Machine B environment**
2. **Start screen recording**

**A's Sharing Phase:**
3. **State trial ID and condition**
4. **Start timer** (Time-to-Share)
5. **Perform sharing workflow** (Baseline or Platform)
6. **Count steps**
7. **Stop timer** when bundle ready

**Transfer:**
8. **Transfer bundle to Machine B**

**B's Receiving Phase:**
9. **Start timer** (Time-to-First-Run)
10. **Perform import/setup**
11. **Mark when first run succeeds**
12. **Continue to verification**
13. **Stop timer** when results verified (Time-to-Reproduce)
14. **Record success/failure**

15. **Stop screen recording**
16. **Record all data**

---

## Data Collection

### Per-Trial Data Template

| Trial | Condition | Steps-to-Share | Time-to-Share (sec) | Time-to-First-Run (sec) | Time-to-Reproduce (sec) | Handoff Success? |
|-------|-----------|----------------|---------------------|-------------------------|-------------------------|------------------|
| 1 | Manual | | | | | Y/N |
| 2 | Platform | | | | | Y/N |
| 3 | Manual | | | | | Y/N |
| 4 | Platform | | | | | Y/N |
| 5 | Manual | | | | | Y/N |
| 6 | Platform | | | | | Y/N |
| 7 | Manual | | | | | Y/N |
| 8 | Platform | | | | | Y/N |
| 9 | Manual | | | | | Y/N |
| 10 | Platform | | | | | Y/N |

### Bundle Completeness Checklist

For each bundle (Platform condition), audit contents:

| Component | Required? | Present? |
|-----------|-----------|----------|
| Config file (frozen) | Yes | Y/N |
| Seeds documented | Yes | Y/N |
| Env fingerprint | Yes | Y/N |
| Training script | Yes | Y/N |
| ARGoS scenario file | Yes | Y/N |
| Logs (metrics.jsonl) | Yes | Y/N |
| Checkpoints | Optional | Y/N |
| Manifest | Yes | Y/N |

**Bundle-Completeness Score: ___/7 required, ___/8 total**

### Setup Divergence Analysis

Compare Machine A and Machine B environments:

| Field | Machine A | Machine B | Match? |
|-------|-----------|-----------|--------|
| Python version | | | Y/N |
| OS | | | Y/N |
| Platform version | | | Y/N |
| RLlib version | | | Y/N |
| PyTorch version | | | Y/N |
| NumPy version | | | Y/N |
| Config hash | | | Y/N |

### Error Log (for failed handoffs)

| Trial | Condition | Error Type | Error Description | Resolution |
|-------|-----------|------------|-------------------|------------|
| | | | | |

---

## Analysis

### Primary Metrics (M5.1-M5.7)

| Metric | Manual (Mean ± SD) | Platform (Mean ± SD) | Reduction (%) | Target |
|--------|-------------------|---------------------|---------------|--------|
| M5.1: Steps-to-Share | 8 (fixed) | ~2 | | Significant |
| M5.2: Time-to-Share | | | | Significant |
| M5.3: Time-to-First-Run | | | | Significant |
| M5.4: Time-to-Reproduce | | | | Significant |
| M5.5: Handoff-Success-Rate | | | | High |

### Secondary Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| M5.6: Bundle-Completeness | /8 | |
| M5.7: Setup-Divergence | # mismatches | |

### Success Rate Calculation

```
Handoff-Success-Rate = (# successful handoffs) / (total handoffs) × 100%
```

A handoff is **successful** if Researcher B can reproduce results that match Researcher A's reference within defined tolerance.

### Time Reduction Calculation

```
Time-to-Share Reduction = (Manual_mean - Platform_mean) / Manual_mean × 100%
Time-to-Reproduce Reduction = (Manual_mean - Platform_mean) / Manual_mean × 100%
```

### Interpretation Guidelines

| Outcome | Interpretation |
|---------|----------------|
| High success rate (≥90%) + significant time reduction | H5 strongly supported |
| High success rate + moderate time reduction | H5 supported |
| Low success rate regardless of time | H5 not supported - investigate failures |
| Ceiling effect (100% both conditions) | Focus on time metrics for differentiation |

### Failure Mode Analysis

If Handoff-Success-Rate < 100%, categorize failures:

| Failure Mode | Count | Cause |
|--------------|-------|-------|
| Missing dependency | | |
| Config incompatibility | | |
| Environment mismatch | | |
| Data corruption | | |
| Other | | |

---

## Evidence Checklist

- [ ] Screen recordings of all trials
- [ ] Per-trial data complete
- [ ] Bundle completeness audit for platform trials
- [ ] Setup divergence analysis for each trial
- [ ] Error logs for any failed handoffs
- [ ] Environment specifications documented

### Required Evidence Files

| File | Description |
|------|-------------|
| `trial_01_manual.mp4` ... | Screen recordings |
| `trial_data.csv` | All timing and step data |
| `bundle_audits.csv` | Bundle completeness for each platform trial |
| `env_comparisons.csv` | Machine A vs B environment data |
| `error_log.csv` | Any errors encountered |
| `analysis_summary.md` | Computed statistics |

### Simulation Environment Documentation

| Field | Value |
|-------|-------|
| Simulation method | Docker / VM / Fresh directory |
| Base image/config | |
| Resource limits | |
| Network isolation | Yes/No |

---

## Limitations

| Limitation | Mitigation |
|------------|------------|
| Researcher B is simulated | Explicitly acknowledge - measures technical enablement, not social/communication aspects |
| Same hardware for A and B (if using containers) | Document hardware specification |
| Transfer time not included | Focus on preparation and reproduction time |
| Limited trial count | Report confidence intervals |

### Note on Simulation

Researcher B is simulated using isolated environments (containers/VMs/fresh directories) rather than actual external researchers. This measures **technical collaboration enablement** but not social/communication aspects of collaboration.

---

## Distinction from SRQ3

| Aspect | SRQ3: Reproducibility | SRQ5: Collaboration |
|--------|----------------------|---------------------|
| Perspective | Self-reproducibility | Cross-environment handoff |
| Who | Same researcher | Simulated "other researcher" |
| Where | Same environment | Different environment |
| Question | "Do I get same results when I run again?" | "Can someone else pick up where I left off?" |
| Focus | Determinism, variance, correctness | Portability, bundling, friction reduction |
| Failure Mode | Non-deterministic results, config drift | Missing dependencies, incomplete bundles |

---

## References

- `docs/CollabBrainstorm.md` - Full rationale and decisions
- `docs/ResearchPlan.md` - SRQ5, H5, E5 definitions
