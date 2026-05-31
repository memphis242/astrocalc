import click
from astrocalc.moon.cli import moon

@click.group()
def astrocalc() -> None:
    """astrocalc base command"""
    click.echo("Hello world, from astrocalc")

astrocalc.add_command(moon)

if __name__ == "__main__":
    astrocalc()
