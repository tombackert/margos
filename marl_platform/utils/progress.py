"""Progress indication utilities for long-running operations."""

import time
from contextlib import contextmanager
from typing import Iterator

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console(force_terminal=True)

# Minimum display time for progress indicators (seconds)
MIN_DISPLAY_TIME = 5.0


@contextmanager
def spinner(message: str, min_time: float = MIN_DISPLAY_TIME) -> Iterator[None]:
    """Display a spinner during an operation.

    Usage:
        with spinner("Loading config..."):
            load_config()
    """
    start = time.time()
    with console.status(message, spinner="dots"):
        yield
        elapsed = time.time() - start
        if elapsed < min_time:
            time.sleep(min_time - elapsed)


@contextmanager
def progress_bar(total: int, description: str = "Processing") -> Iterator[Progress]:
    """Display a progress bar for iterative operations.

    Usage:
        with progress_bar(100, "Training") as progress:
            task = progress.add_task("Training", total=100)
            for i in range(100):
                train_step()
                progress.update(task, advance=1)
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        yield progress


@contextmanager
def mock_progress(description: str, steps: int = 10, duration: float = MIN_DISPLAY_TIME) -> Iterator[None]:
    """Display a mock progress bar that fills over a duration.

    Useful for stub operations that complete instantly but should show progress.

    Usage:
        with mock_progress("Creating bundle..."):
            create_bundle()  # instant stub
    """
    step_time = duration / steps
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(description, total=steps)
        yield
        for _ in range(steps):
            time.sleep(step_time)
            progress.update(task, advance=1)
