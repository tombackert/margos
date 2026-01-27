"""Pydantic schema for experiment configuration."""

from pydantic import BaseModel, Field, field_validator


class ExperimentConfig(BaseModel):
    """Experiment metadata."""

    name: str = Field(..., min_length=1, description="Experiment name")
    seed: int = Field(..., ge=0, description="Random seed for reproducibility")

    @field_validator("seed")
    @classmethod
    def seed_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("seed must be a non-negative integer")
        return v


class ScenarioConfig(BaseModel):
    """ARGoS scenario configuration."""

    file: str = Field(..., min_length=1, description="Path to .argos scenario file")


class TrainingConfig(BaseModel):
    """Training script configuration."""

    script: str = Field(..., min_length=1, description="Path to training script")
    iterations: int = Field(default=100, ge=1, description="Number of training iterations")


class OutputConfig(BaseModel):
    """Output directory configuration."""

    dir: str = Field(default="results/", description="Output directory for results")


class PlatformConfig(BaseModel):
    """Root configuration schema for experiments."""

    experiment: ExperimentConfig
    scenario: ScenarioConfig
    training: TrainingConfig
    output: OutputConfig = Field(default_factory=OutputConfig)
