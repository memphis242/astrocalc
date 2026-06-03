from datetime import date, datetime

import click

from astrocalc.moon.alti import run_alti


def _parse_date(date_str: str) -> date:
    date_parts = date_str.strip().split()
    if len(date_parts) not in {1, 2}:
        raise ValueError
    return datetime.strptime(date_parts[0], "%m/%d/%Y").date()

@click.group()
def moon() -> None:
    """astrocalc moon subcommand base"""

# Leaf commands for the moon subcommand
@moon.command("alti")
@click.argument("target_alti", type=float, metavar="TARGET_ALTITUDE_ANGLE")
@click.option(
    "--location",
    required=True,
    help="'<city>, <country>' or '<latitude>, <longitude>' location to calculate for.",
)
@click.option(
    "--date",
    "date_str",
    required=True,
    help="Date in mm/dd/yyyy format, optionally followed by a timezone abbreviation.",
)
def alti(target_alti: float, location: str, date_str: str) -> None:
    """Command to calculate when the moon reaches a target altitude"""
    try:
        parsed_date = _parse_date(date_str)
    except ValueError:
        raise click.BadParameter(
            "Date must be in mm/dd/yyyy format, e.g., 05/31/2026 or 05/31/2026 CDT",
            param_hint="--date",
        ) from None

    try:
        result = run_alti(target_alti, location, parsed_date)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(result)
