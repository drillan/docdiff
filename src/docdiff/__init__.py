"""docdiff - Document structure analysis and translation management tool."""

__version__ = "0.1.0"


def main() -> None:
    """Main entry point for the CLI."""
    from docdiff.cli.main import run

    run()
