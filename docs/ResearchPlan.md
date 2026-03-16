# Research Plan (Exposé)

## Thesis Title
- Development and Evaluation of an Integrated Platform for Multi-Agent Reinforcement Learning in Swarm Robotics.

## Thesis Topic
- Build an alternative to traditional, fragmented workflow in Swarm Robotic, by development and evaluation of an integrated and collaborative platform that improves the efficiency, reproducibility, and usability of Multi-Agent Reinforcement Learning (MARL) experiments in Swarm Robotics. 

## Background
- There are many simulators for robotics experiments (with strengths & weaknesses for their niche). For Swarm Robotics, ARGoS exists, which was specifically developed for highly-scalable swarm robotics simulations.
- For extremely realistic simulations of individual robots, the Nvidia IsaacSim is the de facto standard.
- IsaacLab is a platform built on IsaacSim that unifies the process of planning, implementation, and evaluation of robotics experiments. By integrating into a central platform, the goal is to increase the efficiency and reproducibility of robotics experiments.
- This concept is also needed for a simulator designed for Swarm Robotics like ARGoS.

## Motivation
- The current process of planning, implementation, and evaluation of Swarm Robotics experiments with MARL is fragmented (ARGoS + RLlib + scripts).
- This complicates reproducibility, is inefficient, and error-prone.
- A central platform could increase efficiency and reproducibility and thus advance research in Swarm Robotics.

## Definition of the Research Question (RQ)

### Methodological Strategy (Empiricism-First)

This thesis follows an empiricism-first principle: every claim must be supported by objective, measurable metrics rather than subjective assessments. User surveys and interviews are excluded by design.

Strategy:
- Each Sub-Research Question (SRQ) was decomposed until it yielded quantifiable metrics with clear thresholds
- Every empirical SRQ (2-5) has: defined metrics, start/stop triggers, minimum sample sizes, explicit baselines, and documented protocols
- SRQ1 (Architecture) is descriptive, validated by whether it enables execution of SRQ2-5 evaluation protocols

Rigor Standard (per SRQ):

| Component   | Requirement                    |
| ----------- | ------------------------------ |
| Metrics     | Objective, countable/timed     |
| Baseline    | Explicit comparison condition  |
| Protocol    | Step-by-step with triggers     |
| Sample size | Defined minimum N              |
| Evidence    | Screen recording, logs, hashes |

### Overarching RQ
- RQ: How does an integrated and collaborative platform improve the efficiency, reproducibility, and usability of Multi-Agent Reinforcement Learning experiments in Swarm Robotics compared to traditional, fragmented workflows?

### Sub-Research Questions (SRQs)
- The RQ is decomposed into five SRQs, each with testable hypotheses and objective evaluation protocols.

| No.                        | Sub-Research Question                                                                                                                                                   | Goal / Rationale                                                                                                                                                    |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[SRQ1 (Architecture)]]    | What architectural design enables execution of the evaluation protocols for SRQ2-5 and collection of their required metrics?                                            | - Descriptive (not empirical)<br>- Validated by enablement: can SRQ2-5 protocols run?<br>- Architecture is necessary prerequisite, not optimized solution           |
| [[SRQ2 (Efficiency)]]      | To what extent does the platform reduce time and effort across the full experiment lifecycle (setup, training management, and analysis) compared to manual workflows?   | - Time-to-Complete (≥50% reduction)<br>- Steps-to-Complete (≥50% reduction)<br>- Full pipeline scope (setup → training → analysis)                                  |
| [[SRQ3 (Reproducibility)]] | To what extent does the platform's centralized configuration and seed management improve self-reproducibility of MARL experiments compared to manual workflows?         | - Reproduce-Success-Rate (≥90% within ±1% tolerance)<br>- Result-Variance reduction<br>- Config-Integrity + Seed-Determinism (by design)                            |
| [[SRQ4 (Usability)]]       | How learnable is the platform, and to what extent does its design minimize user errors, support error recovery, and reduce interaction complexity?                      | - Learnability via task-based metrics<br>- Error-tolerance via error analysis<br>- Design quality via heuristic compliance<br>- Interaction complexity via GOMS/KLM |
| [[SRQ5 (Collaboration)]]   | To what extent does the platform enable reliable reproduction of experiments across different research environments and by how much does it decrease time-to-reproduce? | - Decrease time-to-reproduce between Researcher A and Researcher B<br>- Experiments transferrable and reproducible elsewhere                                        |


## Answering the RQs
- The RQs will be answered with the help of hypotheses (testable assumptions). For this, hypotheses are first formulated, which are then answered with the help of empirical measurable experiments. By answering the SRQs, the overarching RQ is answered, and thus the research goal is achieved.



### Hypotheses
| No.                      | Hypothesis                                                                                                                                                                                                                                                                                                                           | Rationale                                                                                                                                                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[H1 (Architecture)]]    | A modular, config-driven CLI architecture enables measurement of efficiency metrics (SRQ2), reproducibility metrics (SRQ3), usability metrics (SRQ4), and collaboration metrics (SRQ5).                                                                                                                                              | - Validated if: all SRQ2-5 evaluation protocols execute successfully<br>- Architecture is necessary (not optimized): without it, metrics unmeasurable<br>- See ArchitectureBrainstorm.md |
| [[H2 (Efficiency)]]      | The platform reduces Time-to-Complete by ≥50% and Steps-to-Complete by ≥50% compared to manual experiment workflows, measuring human effort across the full pipeline (excluding compute wait time).                                                                                                                                  | - Objective metrics: time + steps<br>- Full pipeline: setup → training → analysis<br>- Training time excluded (workflow efficiency, not compute optimization)                            |
| [[H3 (Reproducibility)]] | The platform achieves higher Reproduce-Success-Rate (≥90% within ±1% tolerance on final reward and AUC) and lower Result-Variance compared to manual reproducibility workflows, through centralized config management and deterministic seed control.                                                                                | - Objective measurement via repetition tests (N=20, automated)<br>- Platform vs Manual baseline (5-step)<br>- Config-Integrity + Seed-Determinism verified via unit tests                           |
| [[H4 (Usability)]]       | The platform demonstrates high learnability (Time-to-First-Success), low error-proneness (Error-Rate), effective error recovery (Recovery-Time), strong compliance with established usability heuristics (Heuristic-Compliance-Rate ≥80%), and significant reduction in predicted interaction time (KLM-Reduction ≥50% vs baseline). | - Objective measurement via task-based trials<br>- Nielsen's heuristic audit<br>- GOMS/KLM analysis <br>- No user surveys required                                                       |
| [[H5 (Collaboration)]]   | The platform's export/import mechanism reduces Steps-to-Share by ≥50%, Time-to-Share by ≥50%, Time-to-First-Run by ≥50%, and Time-to-Reproduce by ≥50% compared to manual experiment handoff, while achieving a Handoff-Success-Rate of ≥90%.                                                                                      | - Steps-to-Share: ≥50% reduction (8 manual → ~2 platform steps)<br>- Time-to-Share / Time-to-First-Run / Time-to-Reproduce: ≥50% reduction (mirrors H2 pattern)<br>- Handoff-Success-Rate: ≥90% (10% resolution at N=20 makes threshold cleanly testable)<br>- Teams avoid setup divergences and version conflicts |

### Evaluation Plan

| Target Area              | Measurable Metrics                                                                                                                                                                                                                                  | Methodology                                                                                                           | Experiments                                                                                                                                                                                                                         | Analysis                                                                            | Controlled Variables                                                 |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| [[E1 (Architecture)]]    | Enablement validation: Can SRQ2-5 protocols execute?                                                                                                                                                                                                | - Descriptive documentation (ADRs, diagrams)<br>- Enablement test: run all evaluation protocols                       | - Implement minimum architecture<br>- Attempt to execute each SRQ2-5 protocol<br>- Document which features enabled which metrics                                                                                                    | H1 validated if all protocols run                                                   | -                                                                    |
| [[E2 (Efficiency)]]      | - Time-to-Complete (human effort time) ([[M2.1]])<br>- Steps-to-Complete (manual actions) ([[M2.2]])                                                                                                                                                | - Platform vs Manual (8-step measured scope) baseline<br>- Screen recording + step logging<br>- N=5 per condition (10 runs total, alternating)<br>- Scope: .argos + training script pre-exist in both conditions; glue script + debug counted as 2 fixed steps (not timed) | - Pre-eval: document actual manual workflow<br>- Condition A (Manual): perform workflow, count steps (8 total: 6 timed + 2 counted), record time<br>- Condition B (Platform): perform workflow, count steps (3), record time<br>- Post-hoc: verify from video | - ≥50% Time reduction<br>- ≥50% Step reduction<br>- Note: time metric is conservative lower bound (glue + debug excluded from timing) | Expert user, same hardware, training time excluded, .argos + training script pre-exist in both conditions |
| [[E3 (Reproducibility)]] | - Reproduce-Success-Rate (±1% tolerance) ([[M3.1]])<br>- Result-Variance ([[M3.2]])<br>- Config-Integrity (by design) ([[M3.3]])<br>- Seed-Determinism (by design) ([[M3.4]])                                                                       | - Repetition tests (N=20, automated)<br>- Platform vs Manual (5-step) baseline<br>- Unit tests for M3.3/M3.4             | - Reference run → N=20 automated reproduction attempts → compare within ±1% on final reward + AUC<br>- Calculate success rate + variance<br>- Verify Config-Integrity + Seed-Determinism via unit tests                                          | - ≥90% Reproduce-Success-Rate<br>- Lower variance than baseline                     | Same hardware, GPU non-determinism documented                        |
| [[E4 (Usability)]]       | - Time-to-First-Success ([[M4.1]])<br>- Error-Rate ([[M4.2]])<br>- Recovery-Time ([[M4.3]])<br>- Documentation-Lookups ([[M4.7]])<br>- Heuristic-Compliance-Rate ([[M4.4]])<br>- KLM-Predicted-Time ([[M4.5]])<br>- KLM-Reduction ([[M4.6]])        | - Task-based trials (7 tasks × 3 trials = 21 data points)<br>- Nielsen's heuristic audit (35 criteria, 1 session)<br>- GOMS/KLM operator analysis (analytical) | - Perform standard tasks as simulated novice → measure time, errors, recovery<br>- Evaluate platform against Nielsen's 10 heuristics<br>- Document operator sequences → calculate predicted times<br>- Compare baseline vs platform | - Learning curve improvement<br>- ≥80% heuristic compliance<br>- ≥50% KLM reduction | Self-as-evaluator (acknowledged limitation)                          |
| [[E5 (Collaboration)]]   | - Steps-to-Share ([[M5.1]])<br>- Time-to-Share ([[M5.2]])<br>- Time-to-First-Run ([[M5.3]])<br>- Time-to-Reproduce (cross-env) ([[M5.4]])<br>- Handoff-Success-Rate ([[M5.5]])<br>- Bundle-Completeness ([[M5.6]])<br>- Setup-Divergence ([[M5.7]]) | - Baseline (manual) vs Platform comparison<br>- Simulated Researcher B via containers/VMs                             | - Export bundle → transfer → import on fresh env → measure effort + success<br>- N=20 handoff cycles (10 per condition) for success rate<br>- N=10 timed trials (platform condition) for M5.2–M5.4<br>- M5.1 steps logged per trial (N=20) | - ≥50% reduction in Steps-to-Share (M5.1)<br>- ≥50% reduction in Time-to-Share (M5.2)<br>- ≥50% reduction in Time-to-First-Run (M5.3)<br>- ≥50% reduction in Time-to-Reproduce (M5.4)<br>- ≥90% Handoff-Success-Rate (M5.5) | Simulated Researcher B (containers/VMs), fresh environment per trial |

