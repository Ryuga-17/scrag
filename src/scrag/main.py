from core.cli import main as cli_main


def main() -> None:
    """Delegate to the Typer CLI entrypoint."""

    cli_main()


if __name__ == "__main__":
    main()
