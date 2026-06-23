# Margos

Margos runs, compares, and shares Multi-Agent Reinforcement Learning experiments with ARGoS and RLlib.

## Install

```bash
pip install -e .
```

## Quickstart

```bash
# Run an experiment (resolves experiments/configs/<name>.yaml)
margos run exp_v1
p r exp_v1          # short alias

# Show results for an experiment (or list all)
margos show exp_v1
p s

# Compare two runs for reproducibility
margos compare exp_v1 --reference exp_v2
p c exp_v1 --reference exp_v2

# Export a run as a portable bundle
margos export exp_v1
p e exp_v1

# Import a bundle on another machine
margos import bundles/exp_v1.zip
p i bundles/exp_v1.zip
```

Each command accepts `--help` for full flag details.

## Docs

See `docs/` for the research plan, design rationale, and experiment protocols.
