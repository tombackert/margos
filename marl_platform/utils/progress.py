"""Progress indication utilities for long-running operations."""

import time
from contextlib import contextmanager
from typing import Iterator, Optional

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    MofNCompleteColumn,
)

console = Console(force_terminal=True)

# Minimum display time for progress indicators (seconds)
MIN_DISPLAY_TIME = 5.0


class TrainingProgress:
    """Progress reporter for training scripts.

    Provides a clean interface for training scripts to report progress
    to the platform's progress bar.

    Usage in training script:
        def main(config, callbacks, output_dir, progress=None):
            iterations = config.get("training", {}).get("iterations", 10)

            for i in range(iterations):
                result = algo.train()
                reward = result.get("episode_reward_mean", 0.0)

                if progress:
                    progress.update(i + 1, iterations, reward=reward)
    """

    def __init__(self) -> None:
        self._progress: Optional[Progress] = None
        self._task_id: Optional[int] = None
        self._started = False

    def start(self, total: int, description: str = "Training") -> None:
        """Start the progress bar.

        Args:
            total: Total number of iterations
            description: Description to show
        """
        if self._started:
            return

        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=30),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("• reward: {task.fields[reward]:.2f}"),
            console=console,
            refresh_per_second=4,
        )
        self._progress.start()
        self._task_id = self._progress.add_task(
            description, total=total, reward=0.0
        )
        self._started = True

    def update(
        self,
        current: int,
        total: Optional[int] = None,
        reward: float = 0.0,
        description: Optional[str] = None,
    ) -> None:
        """Update progress.

        Args:
            current: Current iteration (1-indexed)
            total: Total iterations (optional, uses initial total if not provided)
            reward: Current reward to display
            description: Optional new description
        """
        if not self._started:
            # Auto-start if not started
            self.start(total or 100)

        if self._progress and self._task_id is not None:
            update_kwargs = {"completed": current, "reward": reward}
            if total is not None:
                update_kwargs["total"] = total
            if description is not None:
                update_kwargs["description"] = description
            self._progress.update(self._task_id, **update_kwargs)

    def finish(self, message: Optional[str] = None) -> None:
        """Finish and close the progress bar.

        Args:
            message: Optional completion message to print
        """
        if self._progress:
            self._progress.stop()
            self._progress = None
        self._started = False

        if message:
            console.print(f"[green]✓[/green] {message}")

    def __enter__(self) -> "TrainingProgress":
        return self

    def __exit__(self, *args) -> None:
        self.finish()


@contextmanager
def training_progress(total: int, description: str = "Training") -> Iterator[TrainingProgress]:
    """Context manager for training progress.

    Usage:
        with training_progress(100, "Training") as progress:
            for i in range(100):
                result = train_step()
                progress.update(i + 1, reward=result.reward)
    """
    progress = TrainingProgress()
    progress.start(total, description)
    try:
        yield progress
    finally:
        progress.finish()


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


class OperationProgress:
    """Progress reporter for operations with steps.

    Usage:
        with OperationProgress("Exporting") as progress:
            export_bundle(path, progress_callback=progress.callback)
    """

    def __init__(self, description: str) -> None:
        self._description = description
        self._progress: Optional[Progress] = None
        self._task_id: Optional[int] = None

    def __enter__(self) -> "OperationProgress":
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=30),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            console=console,
            refresh_per_second=4,
        )
        self._progress.start()
        self._task_id = self._progress.add_task(self._description, total=1)
        return self

    def __exit__(self, *args) -> None:
        if self._progress:
            self._progress.stop()

    def callback(self, current: int, total: int, description: str = "") -> None:
        """Progress callback for operations."""
        if self._progress and self._task_id is not None:
            update_kwargs = {"completed": current, "total": total}
            if description:
                update_kwargs["description"] = f"{self._description}: {description}"
            self._progress.update(self._task_id, **update_kwargs)
