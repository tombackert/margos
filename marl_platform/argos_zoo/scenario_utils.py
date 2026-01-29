"""Utilities for preparing ARGoS scenario files."""

import tempfile
from pathlib import Path
from typing import Optional


def get_plugin_paths() -> tuple[Path, Path]:
    """Get absolute paths to built platform plugin libraries.

    Returns:
        Tuple of (controller_lib_path, loop_functions_lib_path)

    Raises:
        FileNotFoundError: If plugins are not built
    """
    # Find repo root by looking for argos_plugins directory
    current = Path(__file__).resolve()
    repo_root = current.parent.parent.parent  # argos_zoo -> marl_platform -> repo_root

    controller = repo_root / "argos_plugins/build/controllers/libmy_ipc_controller.dylib"
    loop_fn = repo_root / "argos_plugins/build/loop_functions/libzoo_loop_functions.dylib"

    if not controller.exists():
        raise FileNotFoundError(
            f"Controller plugin not built. Run: cd argos_plugins/build && cmake .. && make\n"
            f"Expected: {controller}"
        )
    if not loop_fn.exists():
        raise FileNotFoundError(
            f"Loop functions plugin not built. Run: cd argos_plugins/build && cmake .. && make\n"
            f"Expected: {loop_fn}"
        )

    return controller.resolve(), loop_fn.resolve()


def prepare_scenario(
    template_path: str | Path,
    output_path: Optional[str | Path] = None,
) -> str:
    """Prepare a scenario file by substituting library paths.

    Takes a scenario template with placeholders:
    - MARL_PLATFORM_CONTROLLER_LIB
    - MARL_PLATFORM_LOOP_LIB

    And substitutes them with absolute paths to the built plugins.

    Args:
        template_path: Path to scenario template file
        output_path: Optional output path. If None, creates a temp file.

    Returns:
        Path to the prepared scenario file

    Raises:
        FileNotFoundError: If template or plugins not found
    """
    template_path = Path(template_path)
    if not template_path.exists():
        raise FileNotFoundError(f"Scenario template not found: {template_path}")

    controller_lib, loop_lib = get_plugin_paths()

    content = template_path.read_text()
    content = content.replace("MARL_PLATFORM_CONTROLLER_LIB", str(controller_lib))
    content = content.replace("MARL_PLATFORM_LOOP_LIB", str(loop_lib))

    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".argos", prefix="scenario_")
        Path(output_path).write_text(content)
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)

    return str(output_path)
