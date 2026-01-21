# Architecture Brainstorm (SRQ1)

## Core Insight: Data is the Product

- The MVP is NOT the research output. The DATA collected from executing the evaluation plan IS the research output.
- Implication for [[SRQ1 (Architecture)]]: The architecture question is not "What is the best architecture?" (subjective). It is: "What architecture enables us to collect meaningful evaluation data for SRQ2-5?"

---

## The Argumentation Chain

### Step 1: Thesis Goal
- Research question: Does an integrated platform improve efficiency, reproducibility, usability, collaboration compared to fragmented workflows?
- This is answered by collecting comparative data (Platform vs Baseline)

### Step 2: Data Requirements
To answer SRQ2-5, we need to collect:

| SRQ | Data Required | Platform Must Enable |
| --- | ------------- | -------------------- |
| SRQ2 | Time-to-Complete, Steps-to-Complete | Single command E2E, measurable workflow |
| SRQ3 | Reproduce-Success-Rate, Result-Variance | Deterministic execution, config hashing |
| SRQ4 | Error-Rate, Time-to-First-Success, KLM | Clear CLI, error messages, documented interface |
| SRQ5 | Steps-to-Share, Time-to-Reproduce | Export/import commands, bundling |

### Step 3: Architecture as Enabler
The architecture is instrumentalized: every design choice serves data collection.

| Architectural Choice | Enables Which Data Collection                 |
| -------------------- | --------------------------------------------- |
| Unified config       | Config hash for SRQ3, step reduction for SRQ2 |
| CLI interface        | Measurable commands for SRQ2, SRQ4            |
| Seed management      | Determinism metrics for SRQ3                  |
| Export/import        | Handoff metrics for SRQ5                      |

### Step 4: Validation Logic
SRQ1 is validated indirectly: If SRQ2-5 evaluations can be executed and produce meaningful data, then the architecture was sufficient.

This is NOT circular because:
- Architecture → enables → data collection → proves/disproves hypotheses
- Architecture success = data collection success (objective)
- Architecture failure = cannot execute evaluation protocols (observable)

---

## Reframed SRQ1

### Old Formulation (Problematic)
- "What architectural design principles are necessary...?"
- Problem: "Necessary" implies optimality, which is subjective

### New Formulation (Data-Oriented)
[[SRQ1 (Architecture)]]: "What architectural design enables execution of the evaluation protocols for SRQ2-5 and collection of their required metrics?"

### New H1
[[H1 (Architecture)]]: "A modular, config-driven CLI architecture enables measurement of efficiency metrics (SRQ2), reproducibility metrics (SRQ3), usability metrics (SRQ4), and collaboration metrics (SRQ5)."

### Validation
H1 is validated if: All SRQ2-5 evaluation protocols can be executed and produce the specified metrics.

---

## Architecture Requirements (Derived from Evaluation Plan)

### Minimum Viable Architecture for Data Collection

| Requirement | Why (Data Purpose) | From Which SRQ |
| ----------- | ------------------ | -------------- |
| Single CLI entry point | Measure Steps-to-Complete | SRQ2 |
| Unified config file | Measure step reduction, enable config hashing | SRQ2, SRQ3 |
| Deterministic seed control | Measure Reproduce-Success-Rate | SRQ3 |
| Config hash at runtime | Verify Config-Integrity | SRQ3 |
| Clear error messages | Measure Error-Rate, Recovery-Time | SRQ4 |
| Export command | Measure Steps-to-Share, Time-to-Share | SRQ5 |
| Import command | Measure Time-to-First-Run, Time-to-Reproduce | SRQ5 |

### NOT Required (Scope Exclusion)
Features that don't directly enable data collection are out of scope:

| Feature | Why Excluded |
| ------- | ------------ |
| Web UI | CLI sufficient for SRQ4 metrics |
| Multi-user auth | SRQ5 simulates Researcher B, no real collaboration |
| Advanced logging dashboard | Basic logs sufficient for evaluation |
| Plugin marketplace | Modularity demonstrated by structure, not features |

---


## Justification Strategy

### Primary Justification: Enablement
1. Define what data SRQ2-5 require
2. Derive minimum architecture to enable that data collection
3. Build exactly that
4. Validate by executing evaluation protocols

### Secondary Justification: Literature Reference
Architectural patterns used can be traced to established SE literature, but this is **explanatory** (why this pattern), not **validating** (proof it's correct).

| Pattern | Literature Source | Role |
| ------- | ----------------- | ---- |
| Config-driven | 12-Factor App | Explains choice, enables SRQ3 |
| CLI-first | Unix philosophy | Explains choice, enables SRQ2/4 |
| Modular layers | Bass et al. | Explains structure, enables maintenance |

---

## What SRQ1 Section in Thesis Contains

1. Evaluation-Driven Requirements: Table mapping SRQ metrics → architectural features
2. Architecture Description: Layers, modules, data flow (descriptive)
3. Design Rationale: ADRs explaining choices, referencing literature
4. Validation Statement: "The architecture was validated by successful execution of SRQ2-5 evaluations"

---

## Comparison: Old vs New Approach

| Aspect | Old Approach | New Approach |
| ------ | ------------ | ------------ |
| Question | "What is the best architecture?" | "What enables data collection?" |
| Validation | Conform to best practices | Execute evaluation protocols |
| Success criterion | Subjective (expert judgment) | Objective (protocols run, data collected) |
| Risk | Circular reasoning | Clear causal chain |

---

## Methodological Validity: Risk Analysis

### The Concern
"If we build architecture specifically to collect certain data, are we biasing the research? Are we steering results in our favor?"

### Defense: Necessity, Not Optimization

The architecture is necessary to enable measurement. Without it, the experiment cannot run.

| Without this feature... | ...we cannot measure...      | ...therefore SRQ fails  |
| ----------------------- | ---------------------------- | ----------------------- |
| No unified config       | Config hash, step count      | SRQ2, SRQ3 unmeasurable |
| No CLI interface        | Command count, KLM operators | SRQ2, SRQ4 unmeasurable |
| No seed management      | Reproduce-Success-Rate       | SRQ3 unmeasurable       |
| No export/import        | Handoff metrics              | SRQ5 unmeasurable       |

This is prerequisite logic, not result optimization. The architecture enables the experiment to run—it does not determine whether the results are favorable.

### The Actual Research Claim

| What we are NOT claiming                        | What we ARE claiming                                                  |
| ----------------------------------------------- | --------------------------------------------------------------------- |
| "Our platform achieves exactly 50% improvement" | "Integration achieves X% improvement over fragmentation" (X measured) |
| "We designed the best possible architecture"    | "We designed architecture sufficient to run the evaluation"           |
| "Thresholds were chosen correctly upfront"      | "We measure actual improvement and report it"                         |

**The novelty is the empirical comparison itself**, not hitting specific thresholds.

### On Threshold Adjustment

Thresholds (≥50%, ≥90%) are initial estimates. Adjusting them is normal in exploratory research:

| Scenario                                      | Scientific Validity                       |
| --------------------------------------------- | ----------------------------------------- |
| Measure 60%, threshold was 50%                | Valid - hypothesis confirmed              |
| Measure 35%, threshold was 50%                | Valid - report 35%, discuss significance  |
| Measure 35%, adjust threshold to 30% post-hoc | Valid if transparent - 35% is the finding |
| Hide that we measured 35%                     | Invalid - data suppression                |

**Key**: The data is objective. Thresholds are interpretation. We report all data.

### What Would Invalidate the Research

| Invalid Practice                                    | Why                  |
| --------------------------------------------------- | -------------------- |
| Cherry-picking which runs to report                 | Selection bias       |
| Hiding failed reproduction attempts                 | Data suppression     |
| Adjusting measurement protocol after seeing results | P-hacking equivalent |
| Claiming architecture is "optimal"                  | Unfounded claim      |

### What Keeps the Research Valid

| Valid Practice          | Implementation                                   |
| ----------------------- | ------------------------------------------------ |
| Report all data         | Document all trials, positive and negative       |
| Transparent methodology | Protocols defined before implementation          |
| Honest interpretation   | Report actual percentages, not rounded-up claims |
| Acknowledge limitations | Self-as-evaluator, threshold estimates, scope    |

### The Objective Test

The research is valid if:
1. Did we measure what we said we would measure?
2. Did we report all results?
3. Is the comparison fair? (same task, same conditions)
4. Are conclusions grounded in data?

---

![[HighLevelArchitecture.png]]

## Status

- [x] Core insight articulated (data is product)
- [x] Argumentation chain complete
- [x] SRQ1/H1 reframed
- [x] Requirements derived from evaluation plan
- [x] Justification strategy defined
- [x] Methodological validity analysis
- [ ] Update ResearchPlan.md
- [ ] Update SRQMeasurabilityAnalysis.md
