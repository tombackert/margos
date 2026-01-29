# ARGoS Plugin Setup Guide

This guide explains how to build the ARGoS plugins and run your first simulation.

## Prerequisites

1. **ARGoS3** installed and accessible via `argos3` command
2. **CMake** (>= 3.8)
3. **cppzmq** library installed
4. **Python environment** with platform dependencies

Verify ARGoS installation:
```bash
argos3 --version
```

## Step 1: Build the Plugins

```bash
# Navigate to plugins directory
cd argos_plugins

# Create build directory
mkdir -p build && cd build

# Configure with CMake
cmake ..

# Build
make -j4
```

This produces:
- `argos_plugins/build/controllers/libmy_ipc_controller.dylib`
- `argos_plugins/build/loop_functions/libzoo_loop_functions.dylib`

## Step 2: Prepare a Scenario File

Scenario templates are in `experiments/scenarios/`. They contain placeholders for library paths.

Create a runnable scenario by substituting the library paths:

```bash
# From repo root
CONTROLLER_LIB=$(pwd)/argos_plugins/build/controllers/libmy_ipc_controller.dylib
LOOP_LIB=$(pwd)/argos_plugins/build/loop_functions/libzoo_loop_functions.dylib

sed -e "s|MARL_PLATFORM_CONTROLLER_LIB|$CONTROLLER_LIB|g" \
    -e "s|MARL_PLATFORM_LOOP_LIB|$LOOP_LIB|g" \
    experiments/scenarios/footbot_aggregation.argos > /tmp/test_scenario.argos
```

## Step 3: Run with Python

```python
from marl_platform.argos_zoo import ArgosEnv
from marl_platform.argos_zoo.scenarios.aggregation import aggregation_reward

# Create environment
env = ArgosEnv(
    argos_file="/tmp/test_scenario.argos",
    max_steps=100,
    startup_delay=3.0,
    reward_fn=aggregation_reward,
)

# Reset with seed for reproducibility
obs, infos = env.reset(seed=42)
print(f"Agents: {env.agents}")

# Run simulation loop
for step in range(10):
    actions = {agent: env.action_space(agent).sample() for agent in env.agents}
    obs, rewards, terms, truncs, infos = env.step(actions)
    print(f"Step {step}: reward={sum(rewards.values())/len(rewards):.4f}")

env.close()
```

## Step 4: Run Tests

```bash
# Unit tests (fast, no ARGoS needed)
pytest tests/test_argos_zoo.py -v

# Integration tests (requires ARGoS + built plugins)
pytest tests/test_argos_integration.py -v
```

## Troubleshooting

### CMake can't find ARGoS
Ensure ARGoS is installed in `/usr/local/lib/argos3/`. If installed elsewhere, set:
```bash
cmake .. -DARGOS_INCLUDE_DIRS=/path/to/argos/include
```

### Library not found at runtime
ARGoS needs to find the plugin libraries. The scenario file must contain absolute paths to the `.dylib` files.

### ZMQ connection timeout
- Increase `startup_delay` (default 3.0 seconds)
- Check that no other ARGoS instance is running on the same port

### Agents not discovered
Ensure the scenario file has `<distribute>` with `<foot-bot>` entities configured with `controller config="ipc_ctrl"`.

## Project Structure

```
argos_plugins/
├── CMakeLists.txt              # Main build config
├── common/
│   └── json.hpp                # JSON library
├── controllers/
│   ├── CMakeLists.txt
│   ├── my_ipc_controller.cpp   # Robot controller
│   └── my_ipc_controller.h
└── loop_functions/
    ├── CMakeLists.txt
    ├── zoo_loop_functions.cpp  # Simulation orchestration
    └── zoo_loop_functions.h

experiments/scenarios/
└── footbot_aggregation.argos   # Scenario template
```
