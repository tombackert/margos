"""Analysis and reporting."""

from margos.analysis.compare import compare_runs
from margos.analysis.report import (
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
