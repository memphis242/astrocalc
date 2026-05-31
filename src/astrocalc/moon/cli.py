import click
from astrocalc.moon.alti import run_alti

@click.group()
def moon():
    """astrocalc moon subcommand base"""
    click.echo("Hello world, from astrocalc moon")

# Leaf commands for the moon subcommand
@moon.command("alti")
@click.argument('target_alti', type=float, metavar="TARGET_ALTITUDE_ANGLE")
@click.option("--location",            required=True, help="'<city>, <country>' or '<lat>, <lon>' location to calculate for")
@click.option("--date",    "date_str", required=True, help="mm/dd/yyyy")
def alti(target_alti: float, location: str, date_str: str) -> None:
    """Command to calculate when the moon reaches a target altitude"""
    print("Hello world, from astrocalc moon alti")
    result = run_alti(target_alti, location, date_str)
    print(result)
