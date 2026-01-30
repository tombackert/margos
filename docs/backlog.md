# Backlog

- Autocomplete on exp names is not working. I want an autocomplete by hitting tab or something. I want autocomplete active from the start. No manual install from user required. Also no need for customization. 
- Reproducibility comparison has not clear format: should be a table with following format: "| Metric | Run | Reference | Derivation | Match |"
- No exit option in choose-mode: Currently you cant exit the "choose-mode" --> Once you hit "platform run" your are givin the available configs and you have to run before exiting. We need esc/q function 
- You still have to copy paste the name of the reference experiment when you want to run a reproducibility comparison
- Imported and user-created experiments should be in seperate dirs. Currently its confusing where they separate. Need to think together about a way that feels natural. Imported exp should also be marked as such when in exp choose mode 
- Tensorboard only logs, I need a link appearing to the tensorboard client which shows all the live logging. Ray provides this automatically, so no need for implementing ourselfs. We just need to harness the ray functionality. Check/run the ray trainingsscript in ATZ legacy for reference.

## Completed in feature/backlog-fixes

- [x] Show usage explainer as: "Usage: platform [run | report | export | import]"
- [x] We need autocomplete on experiment filenames or a faster way of choosing target file (currently typing date-strings in filenames) -> Added scrollable list selection when no argument provided
- [x] Need command platform show config/experiments/results -> Added `platform show [configs|results|imported|bundles|all]`
- [x] Report shows only derivation in percentage but user is not shown actual data comparison -> Now shows actual values alongside deviation
- [x] Currently it is not possible to run an imported experiment directly (you first have to copy it into config dir...) -> Added `--imported-dir` option and automatic detection
- [x] Report comparison with an imported experiment is not simple as of now (you first have to copy results and stuff) -> Report now automatically checks imported directory
- [x] Progress bar is still mock for report, import, export -> Replaced with real progress bars tracking actual operations
- [x] Tensorboard logging (already integrated through ray i think, but we currently suppress it) because on long runs you need to be able to track training progress on all parameters -> Added `--tensorboard` flag to run command and `tensorboard: true` config option