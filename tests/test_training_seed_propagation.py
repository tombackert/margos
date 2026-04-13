"""Tests for seed propagation in training entrypoints."""

import sys
import types
from pathlib import Path


class _Callback:
    def on_train_result(self, algorithm, result) -> None:
        pass


class _FakeAlgo:
    def __init__(self, result: dict) -> None:
        self._result = result

    def train(self) -> dict:
        return self._result

    def save(self, path: str) -> None:
        Path(path).mkdir(parents=True, exist_ok=True)

    def stop(self) -> None:
        pass


class _FakePPOConfig:
    last_instance = None
    env_creators: dict[str, object] = {}
    env_instances: list[dict] = []

    def __init__(self) -> None:
        self.environment_name = None
        self.environment_config = {}
        self.seed_value = None
        _FakePPOConfig.last_instance = self

    def environment(self, env, env_config=None):
        self.environment_name = env
        self.environment_config = env_config or {}
        return self

    def api_stack(self, **kwargs):
        return self

    def framework(self, framework_name):
        return self

    def debugging(self, **kwargs):
        if "seed" in kwargs:
            self.seed_value = kwargs["seed"]
        return self

    def env_runners(self, **kwargs):
        return self

    def training(self, **kwargs):
        return self

    def build(self):
        creator = _FakePPOConfig.env_creators[self.environment_name]
        env = creator(dict(self.environment_config))
        _FakePPOConfig.env_instances.append(env)
        return _FakeAlgo({"episode_reward_mean": -1.0})


def _install_fake_training_stack(monkeypatch, env_ctor_calls: list[dict]) -> None:
    """Install fake Ray and Argos modules for training-script tests."""
    ppo_module = types.ModuleType("ray.rllib.algorithms.ppo")
    ppo_module.PPOConfig = _FakePPOConfig

    wrapper_module = types.ModuleType("ray.rllib.env.wrappers.pettingzoo_env")
    wrapper_module.ParallelPettingZooEnv = lambda env: env

    registry_module = types.ModuleType("ray.tune.registry")

    def register_env(name, creator):
        _FakePPOConfig.env_creators[name] = creator

    registry_module.register_env = register_env

    monkeypatch.setitem(sys.modules, "ray", types.ModuleType("ray"))
    monkeypatch.setitem(sys.modules, "ray.rllib", types.ModuleType("ray.rllib"))
    monkeypatch.setitem(sys.modules, "ray.rllib.algorithms", types.ModuleType("ray.rllib.algorithms"))
    monkeypatch.setitem(sys.modules, "ray.rllib.algorithms.ppo", ppo_module)
    monkeypatch.setitem(sys.modules, "ray.rllib.env", types.ModuleType("ray.rllib.env"))
    monkeypatch.setitem(sys.modules, "ray.rllib.env.wrappers", types.ModuleType("ray.rllib.env.wrappers"))
    monkeypatch.setitem(sys.modules, "ray.rllib.env.wrappers.pettingzoo_env", wrapper_module)
    monkeypatch.setitem(sys.modules, "ray.tune", types.ModuleType("ray.tune"))
    monkeypatch.setitem(sys.modules, "ray.tune.registry", registry_module)

    import marl_platform.argos_zoo as argos_zoo

    def fake_prepare_scenario(path: str) -> str:
        return f"{path}.prepared"

    def fake_argos_env(**kwargs):
        env_ctor_calls.append(kwargs)
        return kwargs

    monkeypatch.setattr(argos_zoo, "prepare_scenario", fake_prepare_scenario)
    monkeypatch.setattr(argos_zoo, "ArgosEnv", fake_argos_env)
    monkeypatch.setattr(argos_zoo, "aggregation_reward", object())


def test_aggregation_main_propagates_seed_to_rllib_and_argos(tmp_path: Path, monkeypatch) -> None:
    """Aggregation training uses the configured seed for RLlib and ARGoS."""
    from experiments.training import aggregation

    env_ctor_calls: list[dict] = []
    _FakePPOConfig.env_creators = {}
    _FakePPOConfig.env_instances = []
    _install_fake_training_stack(monkeypatch, env_ctor_calls)
    monkeypatch.setattr(aggregation, "init_ray", lambda: None)

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    config = {
        "experiment": {"name": "agg", "seed": 123},
        "scenario": {"file": "scenario.argos"},
        "training": {"iterations": 1},
    }

    aggregation.main(config, [_Callback()], str(output_dir))

    assert _FakePPOConfig.last_instance.seed_value == 123
    assert _FakePPOConfig.last_instance.environment_config == {"seed": 123}
    assert env_ctor_calls[0]["seed"] == 123
    assert env_ctor_calls[0]["argos_file"] == "scenario.argos.prepared"


def test_srq5_main_propagates_seed_to_rllib_and_argos(tmp_path: Path, monkeypatch) -> None:
    """SRQ5 training uses the configured seed for RLlib and ARGoS."""
    from experiments.training import srq5

    env_ctor_calls: list[dict] = []
    _FakePPOConfig.env_creators = {}
    _FakePPOConfig.env_instances = []
    _install_fake_training_stack(monkeypatch, env_ctor_calls)
    monkeypatch.setattr(srq5, "init_ray", lambda: None)

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    config = {
        "experiment": {"name": "srq5", "seed": 321},
        "scenario": {"file": "scenario.argos"},
        "training": {"iterations": 1},
    }

    srq5.main(config, [_Callback()], str(output_dir))

    assert _FakePPOConfig.last_instance.seed_value == 321
    assert _FakePPOConfig.last_instance.environment_config["seed"] == 321
    assert env_ctor_calls[0]["seed"] == 321
    assert env_ctor_calls[0]["argos_file"] == "scenario.argos.prepared"
