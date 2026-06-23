# Sprint 1: CLI Component - GitHub Issues

## Design Clarification: Simplified CLI

**Problem identified:** The original CLI design required explicit paths:
```
margos run --config experiments/configs/exp_v1.yaml
```

**Issue:** This contradicts SRQ2 (efficiency). Every extra argument = more steps, more errors.

**Solution: Convention over configuration**

| Command | Old (Complex) | New (Simple) |
|---------|---------------|--------------|
| run | `margos run --config experiments/configs/exp.yaml` | `margos run exp` |
| report | `margos report --experiment results/exp_123/` | `margos report exp_123` |
| export | `margos export --experiment results/exp_123/` | `margos export exp_123` |
| import | `margos import bundles/bundle.zip` | `margos import bundle.zip` |

**Conventions:**
- Configs live in `experiments/configs/` → user only provides name
- Results live in `results/` → user only provides experiment ID
- Bundles live in `bundles/` → user provides filename
- Extensions auto-appended if missing (`.yaml`, `.zip`)

**Rationale:**
- Directly serves SRQ2 (reduce Steps-to-Complete)
- Serves SRQ4 (reduce cognitive load, fewer errors)
- KLM analysis: fewer keystrokes = lower predicted time

---

## Issue 1: Project scaffolding and CLI entry point

**Title:** `[CLI] Project scaffolding and Typer entry point`

**Labels:** `setup`, `cli`, `must`

**Requirements:** R4.3 (Help command)

### Description

Set up the Python project structure and create the CLI entry point using Typer. This establishes the foundation for all other CLI work.

### Context

From LowLevelArchitectureBrainstorm.md:
- Framework: Typer (Decision A2)
- Project structure defined in "Project Structure" section

### Tasks

- [ ] Create repository structure:
  ```
  margos/
  ├── margos/
  │   ├── __init__.py
  │   ├── cli.py
  │   ├── config/
  │   │   └── __init__.py
  │   ├── orchestrator/
  │   │   └── __init__.py
  │   ├── logging/
  │   │   └── __init__.py
  │   ├── analysis/
  │   │   └── __init__.py
  │   ├── export/
  │   │   └── __init__.py
  │   └── utils/
  │       └── __init__.py
  ├── experiments/
  │   ├── configs/
  │   ├── scenarios/
  │   └── training/
  ├── results/
  ├── bundles/
  ├── pyproject.toml
  ├── README.md
  └── docs/
      └── CLAUDE.md
  ```
- [ ] Create `pyproject.toml` with:
  - Name: `margos`
  - Dependencies: `typer`, `pyyaml`, `pydantic`
  - Entry point: `margos = "margos.cli:app"`
- [ ] Create `cli.py` with Typer app skeleton (4 commands as stubs)
- [ ] Verify installation: `pip install -e .`
- [ ] Verify help: `margos --help` shows all commands

### Acceptance Criteria

```bash
$ margos --help
Usage: margos [OPTIONS] COMMAND [ARGS]...

Commands:
  run      Run an experiment
  report   Generate experiment report
  export   Export experiment bundle
  import   Import experiment bundle

$ margos run --help
Usage: margos run [OPTIONS] EXPERIMENT
...
```

### Definition of Done

- [ ] Package installs without errors
- [ ] All 4 commands appear in `--help`
- [ ] Each command has `--help` with description
- [ ] Code passes basic linting

---

## Issue 2: Implement `run` command

**Title:** `[CLI] Implement run command with convention-based paths`

**Labels:** `cli`, `feature`, `must`

**Requirements:** R2.2 (`run` command)

**Depends on:** Issue 1

### Description

Implement the `run` command that accepts an experiment name (not full path) and routes to the Training Orchestrator.

### Context

The `run` command is the primary entry point for users. It should be as simple as possible.

**Convention:**
- User provides: experiment name (e.g., `exp_v1`)
- Margos resolves: `experiments/configs/exp_v1.yaml`

### Interface

```python
@app.command()
def run(
    experiment: str = typer.Argument(..., help="Experiment name (from experiments/configs/)"),
    config_dir: str = typer.Option("experiments/configs", help="Config directory (override default)")
):
    """Run an experiment from config file."""
```

### Tasks

- [ ] Implement path resolution:
  ```python
  def resolve_config_path(experiment: str, config_dir: str) -> Path:
      # Handle: "exp_v1" -> "experiments/configs/exp_v1.yaml"
      # Handle: "exp_v1.yaml" -> "experiments/configs/exp_v1.yaml"
      # Handle: absolute path -> use as-is (escape hatch)
  ```
- [ ] Validate config file exists before proceeding
- [ ] Create stub for orchestrator call:
  ```python
  # margos/orchestrator/__init__.py
  def run_experiment(config_path: str) -> str:
      """Stub: Returns output directory path."""
      raise NotImplementedError("Orchestrator not yet implemented")
  ```
- [ ] Display success message with result path
- [ ] Display clear error if config not found

### Acceptance Criteria

```bash
# Happy path (stub returns mock path)
$ margos run exp_v1
Running experiment: exp_v1
Config: experiments/configs/exp_v1.yaml
Output: results/exp_v1_20240115-143022/

# Config not found
$ margos run nonexistent
Error: Config file not found
  Path: experiments/configs/nonexistent.yaml
  Fix: Create the config file or check the experiment name

# With explicit path (escape hatch)
$ margos run /absolute/path/to/config.yaml
Running experiment from: /absolute/path/to/config.yaml
```

### Definition of Done

- [ ] `margos run <name>` resolves to correct config path
- [ ] Missing config shows clear error with path and fix suggestion
- [ ] Absolute paths work as escape hatch
- [ ] Orchestrator stub is called with resolved path

---

## Issue 3: Implement `report` command

**Title:** `[CLI] Implement report command with convention-based paths`

**Labels:** `cli`, `feature`, `must`

**Requirements:** R2.5 (`report` command)

**Depends on:** Issue 1

### Description

Implement the `report` command that generates analysis for an experiment.

### Context

**Convention:**
- User provides: experiment ID (e.g., `exp_v1_20240115-143022`)
- Margos resolves: `results/exp_v1_20240115-143022/`

### Interface

```python
@app.command()
def report(
    experiment: str = typer.Argument(..., help="Experiment ID (from results/)"),
    reference: str = typer.Option(None, help="Reference experiment for comparison"),
    results_dir: str = typer.Option("results", help="Results directory (override default)")
):
    """Generate report for an experiment."""
```

### Tasks

- [ ] Implement path resolution for experiment directory
- [ ] Implement path resolution for optional reference
- [ ] Validate directories exist
- [ ] Create stub for analysis call:
  ```python
  # margos/analysis/__init__.py
  def generate_report(experiment_dir: str, reference_dir: str = None) -> str:
      """Stub: Returns report directory path."""
      raise NotImplementedError("Analysis not yet implemented")
  ```
- [ ] Display success message with report path

### Acceptance Criteria

```bash
# Basic report
$ margos report exp_v1_20240115-143022
Generating report for: exp_v1_20240115-143022
Report saved to: results/exp_v1_20240115-143022/report/

# With reference comparison
$ margos report exp_v1_20240115-143022 --reference exp_v1_20240114-120000
Generating report with comparison...
Reference: results/exp_v1_20240114-120000/
Report saved to: results/exp_v1_20240115-143022/report/

# Experiment not found
$ margos report nonexistent
Error: Experiment not found
  Path: results/nonexistent/
  Fix: Check the experiment ID or run `ls results/` to see available experiments
```

### Definition of Done

- [ ] `margos report <id>` resolves to correct results path
- [ ] Optional `--reference` works for comparison
- [ ] Missing experiment shows clear error
- [ ] Analysis stub is called with resolved paths

---

## Issue 4: Implement `export` command

**Title:** `[CLI] Implement export command`

**Labels:** `cli`, `feature`, `must`

**Requirements:** R5.1 (`export` command)

**Depends on:** Issue 1

### Description

Implement the `export` command that bundles an experiment for sharing.

### Context

**Convention:**
- User provides: experiment ID
- Margos resolves: `results/<experiment_id>/`
- Output default: `bundles/<experiment_id>.zip`

### Interface

```python
@app.command()
def export(
    experiment: str = typer.Argument(..., help="Experiment ID to export"),
    output: str = typer.Option(None, help="Output bundle path (default: bundles/<experiment>.zip)")
):
    """Export experiment to shareable bundle."""
```

### Tasks

- [ ] Implement path resolution for experiment directory
- [ ] Generate default output path if not provided
- [ ] Validate experiment directory exists
- [ ] Create stub for export call:
  ```python
  # margos/export/__init__.py
  def export_bundle(experiment_dir: str, output_path: str) -> str:
      """Stub: Returns bundle path."""
      raise NotImplementedError("Export not yet implemented")
  ```
- [ ] Display success message with bundle path

### Acceptance Criteria

```bash
# Default output
$ margos export exp_v1_20240115-143022
Exporting experiment: exp_v1_20240115-143022
Bundle created: bundles/exp_v1_20240115-143022.zip

# Custom output
$ margos export exp_v1_20240115-143022 --output my_bundle.zip
Bundle created: bundles/my_bundle.zip

# Experiment not found
$ margos export nonexistent
Error: Experiment not found
  Path: results/nonexistent/
  Fix: Check the experiment ID or run `ls results/` to see available experiments
```

### Definition of Done

- [ ] `margos export <id>` creates bundle with default name
- [ ] `--output` allows custom bundle name
- [ ] Missing experiment shows clear error
- [ ] Export stub is called with resolved paths

---

## Issue 5: Implement `import` command

**Title:** `[CLI] Implement import command`

**Labels:** `cli`, `feature`, `must`

**Requirements:** R5.2 (`import` command)

**Depends on:** Issue 1

### Description

Implement the `import` command that unpacks an experiment bundle.

### Context

**Convention:**
- User provides: bundle filename (e.g., `exp_v1.zip`)
- Margos resolves: `bundles/exp_v1.zip`
- Output: `experiments/imported/<name>/`

Note: In code, use `import_` as function name (Typer maps to `import` in CLI).

### Interface

```python
@app.command("import")  # Explicit name mapping
def import_(
    bundle: str = typer.Argument(..., help="Bundle file to import"),
    bundles_dir: str = typer.Option("bundles", help="Bundles directory (override default)")
):
    """Import experiment bundle."""
```

### Tasks

- [ ] Implement path resolution for bundle file
- [ ] Validate bundle file exists
- [ ] Create stub for import call:
  ```python
  # margos/export/__init__.py
  def import_bundle(bundle_path: str) -> str:
      """Stub: Returns imported experiment path."""
      raise NotImplementedError("Import not yet implemented")
  ```
- [ ] Display success message with imported experiment path
- [ ] Show fingerprint comparison summary (from stub)

### Acceptance Criteria

```bash
# Import bundle
$ margos import exp_v1.zip
Importing bundle: bundles/exp_v1.zip
Imported to: experiments/imported/exp_v1/

Environment comparison:
  Python: 3.10.0 -> 3.10.0 ✓
  torch: 2.0.0 -> 2.0.0 ✓
  rllib: 2.5.0 -> 2.5.0 ✓

Ready to run: margos run imported/exp_v1

# Bundle not found
$ margos import nonexistent.zip
Error: Bundle not found
  Path: bundles/nonexistent.zip
  Fix: Check the filename or run `ls bundles/` to see available bundles
```

### Definition of Done

- [ ] `margos import <file>` resolves to correct bundle path
- [ ] Missing bundle shows clear error
- [ ] Import stub is called with resolved path
- [ ] Success message shows path to imported experiment

---

## Issue 6: CLI error handling framework

**Title:** `[CLI] Implement consistent error handling and display`

**Labels:** `cli`, `usability`, `must`

**Requirements:** R4.2 (Clear error messages)

**Depends on:** Issue 1

### Description

Implement consistent, user-friendly error handling across all CLI commands. This resolves Q9 from LowLevelArchitectureBrainstorm.

### Context

From R4.2 requirements:
- Plain language (not stack traces)
- Identify what went wrong
- Suggest how to fix
- Include relevant context (file, line, value)

### Error Display Format

```
Error: <What went wrong>
  <Context key>: <value>
  <Context key>: <value>
  Fix: <How to resolve>
```

### Tasks

- [ ] Create error display utility:
  ```python
  # margos/utils/errors.py
  class MargosError(Exception):
      def __init__(self, message: str, context: dict = None, fix: str = None):
          self.message = message
          self.context = context or {}
          self.fix = fix

  def display_error(error: MargosError):
      """Format and display error to user."""
  ```
- [ ] Create common error types:
  ```python
  class ConfigNotFoundError(MargosError): ...
  class ExperimentNotFoundError(MargosError): ...
  class BundleNotFoundError(MargosError): ...
  class ValidationError(MargosError): ...
  ```
- [ ] Add global exception handler to CLI app
- [ ] Add `--verbose` flag for full traceback (debugging)
- [ ] Update all commands to use error framework

### Acceptance Criteria

```bash
# Normal error (clean)
$ margos run nonexistent
Error: Config file not found
  Path: experiments/configs/nonexistent.yaml
  Fix: Create the config file or check the experiment name

# Verbose error (debugging)
$ margos run nonexistent --verbose
Error: Config file not found
  Path: experiments/configs/nonexistent.yaml
  Fix: Create the config file or check the experiment name

Traceback (most recent call last):
  File "margos/cli.py", line 42, in run
    config_path = resolve_config_path(experiment)
  ...
ConfigNotFoundError: Config file not found
```

### Definition of Done

- [ ] All errors display in consistent format
- [ ] No raw stack traces in normal mode
- [ ] `--verbose` shows full traceback
- [ ] Error types cover common failure modes
- [ ] Each error includes actionable fix suggestion

---

## Issue 7: Progress indication (Should)

**Title:** `[CLI] Add progress indication for long operations`

**Labels:** `cli`, `enhancement`, `should`

**Requirements:** R2.6 (Progress indication)

**Depends on:** Issues 1-6

**Priority:** Should (implement after Must issues)

### Description

Add visual feedback during long-running operations like training.

### Tasks

- [ ] Add spinner for operations in progress
- [ ] Add progress bar where iteration count is known
- [ ] Use `rich` library (Typer-compatible) for display

### Acceptance Criteria

```bash
$ margos run exp_v1
Running experiment: exp_v1
⠋ Starting training...
Training: [████████░░░░░░░░░░░░] 40/100 iterations
```

### Definition of Done

- [ ] Spinner shows during initialization
- [ ] Progress updates during training (when orchestrator supports it)
- [ ] Clean display without cluttering output

---

## Sprint Summary

| # | Issue | Requirements | Priority | Depends On |
|---|-------|--------------|----------|------------|
| 1 | Project scaffolding | R4.3 | Must | - |
| 2 | `run` command | R2.2 | Must | 1 |
| 3 | `report` command | R2.5 | Must | 1 |
| 4 | `export` command | R5.1 | Must | 1 |
| 5 | `import` command | R5.2 | Must | 1 |
| 6 | Error handling | R4.2 | Must | 1 |
| 7 | Progress indication | R2.6 | Should | 1-6 |

**Sprint Goal:** Complete CLI interface with stubs for all backend components. User can run all commands (they fail gracefully until backends implemented).

---

## Context for MVP Repo

The MVP repo needs these docs for Claude context:

1. **CLAUDE.md** - Distilled version with:
   - Project purpose (thesis MVP, not production)
   - Architecture overview (from DesignBrainstorm)
   - Component interfaces (from LowLevelArchitectureBrainstorm)
   - Conventions (paths, naming)

2. **docs/architecture.md** - Key sections from:
   - DesignBrainstorm (requirements, decisions)
   - LowLevelArchitectureBrainstorm (interfaces)

3. **docs/requirements-traceability.md** - The requirements table from DesignBrainstorm

This ensures Claude has full context when working on implementation.
