"""Analysis and reporting."""

from marl_platform.analysis.compare import compare_runs
from marl_platform.analysis.report import (
    calculate_auc,
    format_comparison,
    generate_report,
    plot_learning_curve,
)

__all__ = [
    "generate_report",
    "plot_learning_curve",
    "calculate_auc",
    "compare_runs",
    "format_comparison",
]
