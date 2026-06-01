import click
from astrocalc.moon.alti import run_alti
from datetime import datetime
from zoneinfo import ZoneInfo

@click.group()
def moon():
    """astrocalc moon subcommand base"""

# Leaf commands for the moon subcommand
@moon.command("alti")
@click.argument('target_alti', type=float, metavar="TARGET_ALTITUDE_ANGLE")
@click.option("--location",            required=True, help="'<city>, <country>' or '<lat>, <lon>' location to calculate for")
@click.option("--date",    "date_str", required=True, help="mm/dd/yyyy")
def alti(target_alti: float, location: str, date_str: str) -> None:
    """Command to calculate when the moon reaches a target altitude"""
    # Parse the location into latitude/longitude coordinates
    # TODO
    parsed_loc = location

    # Parse the date entry into a datetime object
    try:
        parsed_date = datetime.strptime(datetime_str, "%m/%d/%Y").date()
        parsed_date_tz = parsed_date.replace(tzinfo=ZoneInfo("
    except ValueError:
        raise click.BadParameter("Date must be in mm/dd/yyyy format, e.g., 05/31/2026")
    # TODO: Catch other exceptions...

    result = run_alti(target_alti, parse_loc, parsed_date)
    print(result)
