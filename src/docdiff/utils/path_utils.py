"""Path utility functions for safe path operations."""

from pathlib import Path


def safe_relative_to(path: Path, base: Path) -> Path:
    """Get relative path safely, handling paths outside base directory.

    Args:
        path: Path to make relative
        base: Base path to make relative to

    Returns:
        Relative path if path is under base, otherwise returns the path itself
    """
    try:
        return path.relative_to(base)
    except ValueError:
        # Path is not under base, return the path as is
        # or use just the file name
        return Path(path.name)


def get_display_path(path: Path, base: Path) -> str:
    """Get a display-friendly path string.

    Args:
        path: Path to display
        base: Base path for relative display

    Returns:
        String representation suitable for display
    """
    try:
        return str(path.relative_to(base))
    except ValueError:
        # If not relative to base, just show the file name
        return path.name
