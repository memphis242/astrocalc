from skyfield.api import load, wgs84 # module to do astronomy position calculations
from scipy.optimize import brentq # 1D scalar root-finder to numerically solve for time → tgt ° alt
from datetime import datetime, timedelta, timezone # represent various time/date quantities

# TODO: May want to move skyfield loading and common astro object retrieval upstream
#       since many subcommands will likely do similar things

# Need to load skyfield's "time system object" to talk in skyfield's time-language
_ts  = load.timescaler()

# Then load the NASA/JPL ephemeris file with calculate positions of solar system
# bodies, including the Earth and the Moon
_astro_objects = load("de421.bsp")
# Pull the specific Earth and Moon positions...
_earth = _astro_objects["_earth"]
_moon  = _astro_objects["_moon"]

def _moon_alt_deg(input_time):
    """Calculate the moon's altitude at a given time"""
    t = _ts.from_datetime(input_time)
    moon_relative_apparent_pos = houston.at(t).observe(_moon).apparent()
    alt, _, _ = moon_relative_apparent_pos.altaz()
    return alt.degrees

def run_alti(target_alti: float, location: str, date_str: datetime.date) -> str:
    """Run the alti command calculation to determine when the _moon will reach a
       target altitude (angle of elevation) in the sky above the horizon"""

    # TODO: validate sensible range of target_alti
    if target_alti < 0.0 or target_alti > 90.0:
        raise click.BadParameter(f"Target altitude {target_alti}° is outside of valid range: 0° - 90°")

    # Calculate location arg's position within skyfield's coordinate system
    _loc = _earth + wgs84.latlon(29.7604, -95.3698) # FIXME: fixed to houston

    # Function to optimize
    def _f(dt):
        return _moon_alt_deg(dt) - target_alti

    _start = datetime(2026, 5, 30, 0, 0, tzinfo=timezone.utc)
    _end   = _start + timedelta(days=2)

    _step = timedelta(minutes=5)
    t0 = _start
    while t0 < _end:
        t1 = t0 + _step
        if _f(t0) + _f(t1) < 0:
            root_seconds = brentq( lambda s: _f(t0 + timedelta(seconds=s)),
                                   0,
                                  _step.total_seconds() )
            event_utc = t0 + timedelta(seconds=root_seconds)
            print('Moon cross 10° atltitude at UTC: ', event_utc)
            print('Houston local time: ', event_utc.astimezone())
        to = t1

    return '8:51pm CDT'
