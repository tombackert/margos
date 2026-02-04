# Backlog

## Open

## Completed

- [x] Use same layout/list-framing for experiment list everywhere (use platform show style as standard)
- [x] Report command does not serve any SRQ. What we want fto satisf the SRQs, is the compare experiments function. We should therefore get rid of the report command and the redundant option functions "reference" and "compare" and should instead have compare as native command. Should work the same as "platform report --compare" works right now
- [x] When listing available configurations for any command, e.g. configs, exp_to_export/import, etc, they should be always sorted by date (most recent last)

## Completed in feature/backlog-fixes (Round 4)

- [x] Removed non-functional autocomplete - Deleted autocomplete functions, relying on existing list selection
- [x] Added short options to all CLI commands: `-c` (config-dir), `-i` (imported-dir), `-r` (reference), `-d` (results-dir), `-o` (output), `-b` (bundles-dir)
- [x] TensorBoard enabled by default - Changed `tensorboard: bool = True` in schema, removed `--tensorboard` CLI flag
- [x] Cleaned up training script - Moved Ray logging utilities to `marl_platform/utils/ray_logging.py`, simplified `aggregation.py` to pure training logic

## Completed in feature/sprint3-analysis-export (Round 3)

- [x] Removed --install-completion flag (too slow) - set `add_completion=False` in Typer app
- [x] Fixed repro table alignment - Deviation column now uses `:9.2%` format for proper alignment
- [x] Fixed TensorBoard not working - training script now uses callbacks from orchestrator via `CombinedCallbacks` wrapper

## Completed in feature/backlog-fixes (Round 2)

- [x] Autocomplete on exp names - Added tab completion via Typer's autocompletion feature (use Tab to complete experiment names)
- [x] Reproducibility comparison has clear table format: "| Metric | Run | Reference | Deviation | Match |"
- [x] Exit option in choose-mode: Enter '0' or 'q' to cancel and exit selection
- [x] Reference experiment selection: Use `platform report --compare` for interactive reference selection
- [x] Imported vs user-created experiments clearly separated in selection with [yellow](imported)[/yellow] labels and grouped sections
- [x] TensorBoard shows clear link: Prints instructions with `tensorboard --logdir <path>` and `http://localhost:6006`

## Completed in feature/backlog-fixes (Round 1)

- [x] Show usage explainer as: "Usage: platform [run | report | export | import]"
- [x] We need autocomplete on experiment filenames or a faster way of choosing target file (currently typing date-strings in filenames) -> Added scrollable list selection when no argument provided
- [x] Need command platform show config/experiments/results -> Added `platform show [configs|results|imported|bundles|all]`
- [x] Report shows only derivation in percentage but user is not shown actual data comparison -> Now shows actual values alongside deviation
- [x] Currently it is not possible to run an imported experiment directly (you first have to copy it into config dir...) -> Added `--imported-dir` option and automatic detection
- [x] Report comparison with an imported experiment is not simple as of now (you first have to copy results and stuff) -> Report now automatically checks imported directory
- [x] Progress bar is still mock for report, import, export -> Replaced with real progress bars tracking actual operations
- [x] Tensorboard logging (already integrated through ray i think, but we currently suppress it) because on long runs you need to be able to track training progress on all parameters -> Added `--tensorboard` flag to run command and `tensorboard: true` config option
