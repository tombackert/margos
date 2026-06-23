"""Ray logging utilities for suppressing verbose output."""

import logging
import os
import warnings


class _DeprecationFilter(logging.Filter):
    """Filter out deprecation warnings from Ray."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        skip_patterns = [
            "DeprecationWarning",
            "has been deprecated",
            "Install gputil",
            "will raise an error in the future",
        ]
        return not any(pattern in msg for pattern in skip_patterns)


def _install_logging_filter() -> None:
    """Install deprecation filter on all handlers."""
    filt = _DeprecationFilter()
    for name in [None, "ray", "ray.rllib", "ray.tune"]:
        logger = logging.getLogger(name)
        for handler in logger.handlers:
            handler.addFilter(filt)
        logger.addFilter(filt)


def setup_ray_environment() -> None:
    """Configure environment variables and warnings before Ray imports."""
    os.environ["PYTHONWARNINGS"] = "ignore"
    os.environ["RAY_DEDUP_LOGS"] = "0"
    os.environ["RAY_LOG_TO_STDERR"] = "0"

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", message=".*gputil.*")
    warnings.filterwarnings("ignore", message=".*deprecated.*")

    for logger_name in ["ray", "ray.rllib", "ray.tune", "ray.data", "ray.train"]:
        logging.getLogger(logger_name).setLevel(logging.ERROR)


def init_ray() -> None:
    """Initialize Ray with minimal logging.

    Should be called after setup_ray_environment().
    """
    import ray

    if not ray.is_initialized():
        ray.init(
            logging_level=logging.WARNING,
            log_to_driver=True,
            configure_logging=True,
        )

    _install_logging_filter()
