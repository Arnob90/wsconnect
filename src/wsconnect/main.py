import subprocess
import sys
import shutil
import typer
from typing import Optional

# Initialize the Typer app
app = typer.Typer(help="A fast fzf-based selector for Windscribe VPN.")


def check_dependencies():
    """Ensure required system binaries are available."""
    for tool in ["windscribe-cli", "fzf"]:
        if not shutil.which(tool):
            typer.secho(
                f"Error: {tool} not found in PATH.", fg=typer.colors.RED, err=True
            )
            raise typer.Exit(code=1)


@app.command()
def connect(
    pro: bool = typer.Option(False, "--pro", help="Include Pro locations in the list"),
    filter_query: Optional[str] = typer.Option(
        None, "--filter", "-f", help="Pre-filter locations"
    ),
):
    """
    Interactively select and connect to a Windscribe location using fzf.
    """
    check_dependencies()

    # 1. Fetch locations
    result = subprocess.run(
        ["windscribe-cli", "locations"], capture_output=True, text=True
    )

    location_list = result.stdout.splitlines()

    # 2. Filter logic
    if not pro:
        location_list = [loc for loc in location_list if "(Pro)" not in loc]

    if filter_query:
        location_list = [
            loc for loc in location_list if filter_query.lower() in loc.lower()
        ]

    # 3. Interactive selection via fzf
    selected_proc = subprocess.run(
        ["fzf"], input="\n".join(location_list), capture_output=True, text=True
    )

    if selected_proc.returncode != 0:
        typer.echo("Selection cancelled.")
        raise typer.Exit()

    # 4. Parsing logic
    selected_location = selected_proc.stdout.strip()
    # Handle the 'City - Nickname' format
    selected_nick = selected_location.split(" - ")[-1]
    clean_nick = selected_nick.removesuffix("(10 Gbps)").strip()
    # 5. Run
    subprocess.run(
        ["windscribe-cli", "connect", clean_nick],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


if __name__ == "__main__":
    app()
