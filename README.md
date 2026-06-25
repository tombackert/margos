<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/margos-logo-dark.svg">
  <img src="docs/assets/margos-logo.svg" alt="MARGoS" width="440">
</picture>

<p><strong>Research infrastructure for reproducible Multi-Agent Reinforcement Learning experiments.</strong></p>

<p>
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="RL" src="https://img.shields.io/badge/RL-Ray%20RLlib%20%C2%B7%20PyTorch-EE4C2C">
  <img alt="Simulator" src="https://img.shields.io/badge/simulator-ARGoS%203-4f46e5">
  <img alt="Status" src="https://img.shields.io/badge/status-research%20MVP-7c3aed">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-22c55e">
</p>

<p>
  <a href="https://htmlpreview.github.io/?https://github.com/tombackert/margos/blob/main/docs/index.html"><b>📖 Read the Documentation</b></a>
  &nbsp;·&nbsp;
  <a href="#quickstart">Quickstart</a>
  &nbsp;·&nbsp;
  <a href="#architecture">Architecture</a>
</p>

</div>

---

## Overview

A typical MARL workflow is fragmented across a simulator, an RL framework, ad-hoc training scripts,
manual seeding, scattered logs, and hand-built archives for sharing results. **MARGoS** unifies that
workflow behind five commands: you provide *names*, and MARGoS resolves paths, freezes configuration,
captures the environment, propagates seeds, logs metrics, and packages everything needed to reproduce
a run on another machine.

It is built on **ARGoS 3** (swarm-robotics simulation) and **Ray RLlib** (PPO on PyTorch), connected
by **ArgosToZoo**, a PettingZoo environment that bridges the two over ZeroMQ.

| Capability | What it gives you |
|---|---|
| **Run** | One command loads a config, seeds every RNG, launches the simulator, and trains with live metrics |
| **Reproduce** | Centralized seeding, config hashing, integrity checks, and an environment fingerprint |
| **Compare** | Validate a run against a reference for handoff success and strict reproducibility |
| **Share** | Export a run to a single portable ZIP and import it elsewhere with an environment diff |

## Documentation

📖 **The complete software documentation lives in [`docs/index.html`](docs/index.html)**: a single-page
site with a sidebar table of contents covering every component: architecture, the CLI, configuration,
reproducibility, the ArgosToZoo bridge, training scripts, logging, analysis, and export/import.

> Open it locally in a browser, or view it online via
> **[htmlpreview](https://htmlpreview.github.io/?https://github.com/tombackert/margos/blob/main/docs/index.html)**.

## Installation

```bash
# core CLI
pip install -e .

# full ML / simulation stack (RLlib, PyTorch, PettingZoo, ZeroMQ, …)
pip install -e ".[ml]"
```

Running training also requires **ARGoS 3** and two compiled C++ plugins:

```bash
cd argos_plugins && mkdir -p build && cd build
cmake .. && make -j4
```

See the [Installation & Setup](https://htmlpreview.github.io/?https://github.com/tombackert/margos/blob/main/docs/index.html#install) docs for prerequisites and platform notes.

## Quickstart

```bash
# Run an experiment (resolves experiments/configs/<name>.yaml)
margos run aggregation_v1
p r aggregation_v1          # short alias

# Show configs, results, imported runs, and bundles
margos show
p s results

# Compare two runs for reproducibility
margos compare run_a run_b
p c                         # pick both runs interactively

# Export a run as a portable bundle, then import it elsewhere
margos export run_a         # -> bundles/run_a.zip
margos import bundles/run_a.zip
```

Every command accepts `--help`; a global `--verbose / -v` prints full tracebacks.

| Command | Alias | Purpose |
|---|---|---|
| `margos run` | `p r` | Run an experiment from a config file |
| `margos show` | `p s` | List configs, results, imported runs, and bundles |
| `margos compare` | `p c` | Compare two runs for reproducibility / handoff |
| `margos export` | `p e` | Package a run into a shareable bundle |
| `margos import` | `p i` | Unpack a bundle and check the environment |

## Architecture

```
Command-Line Interface · Typer (margos / p)
        │
        ├─ Config System ─┐
        ├─ Orchestrator ──┤   shared store:  results/
        ├─ Analysis ──────┤   (frozen config · hashes · fingerprint ·
        └─ Export/Import ─┘    metrics.jsonl · checkpoints)
        │
        └─ run ▶ Training Script ▶ Ray RLlib (PPO) ▶ ArgosToZoo ──ZeroMQ── ARGoS 3 (C++ plugins)
```

A thin CLI drives four core subsystems over a single artifact store; the orchestrator invokes the
simulation stack. Full diagrams and rationale are in the
[Architecture](https://htmlpreview.github.io/?https://github.com/tombackert/margos/blob/main/docs/index.html#architecture) docs.

## Repository layout

```
margos/         Python package (cli, config, orchestrator, logging,
                analysis, export, argos_zoo, utils)
argos_plugins/  ARGoS C++ controller + loop-functions plugins
experiments/    configs/ · scenarios/ · training/ · imported/
results/        timestamped run outputs
bundles/        exported .zip bundles
tests/          pytest suite (slow e2e tests opt-in)
docs/           documentation (open docs/index.html)
```

## Development

```bash
pip install -e ".[dev]"
pytest            # fast unit tests (slow e2e excluded by default)
pytest -m slow    # end-to-end tests (require ARGoS + RLlib)
ruff check .
```

## License

MIT

---

<div align="center">
<sub>MARGoS is research infrastructure built for a small-scale research project. The research questions,
hypotheses, and evaluation protocol are described in the accompanying paper; this repository documents the software.</sub>
</div>
