from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from scipy.optimize import brentq
from skyfield.api import load, wgs84

# TODO: May want to move skyfield loading and common astro object retrieval upstream
#       since many subcommands will likely do similar things

# Need to load skyfield's "time system object" to talk in skyfield's time-language
_ts = load.timescale()

# Then load the NASA/JPL ephemeris file with calculate positions of solar system
# bodies, including the Earth and the Moon
_astro_objects = load("de421.bsp")
# Pull the specific Earth and Moon positions...
_earth = _astro_objects["earth"]
_moon = _astro_objects["moon"]


@dataclass(frozen=True)
class ObserverLocation:
    name: str
    latitude: float
    longitude: float
    timezone_name: str


_KNOWN_LOCATIONS = {
    "houston": ObserverLocation("Houston, US", 29.7604, -95.3698, "America/Chicago"),
    "houston, us": ObserverLocation("Houston, US", 29.7604, -95.3698, "America/Chicago"),
    "houston, usa": ObserverLocation("Houston, US", 29.7604, -95.3698, "America/Chicago"),
    "houston, tx": ObserverLocation("Houston, TX", 29.7604, -95.3698, "America/Chicago"),
    "houston, texas": ObserverLocation("Houston, TX", 29.7604, -95.3698, "America/Chicago"),
    "chicago": ObserverLocation("Chicago, US", 41.8781, -87.6298, "America/Chicago"),
    "chicago, us": ObserverLocation("Chicago, US", 41.8781, -87.6298, "America/Chicago"),
    "new york": ObserverLocation("New York, US", 40.7128, -74.0060, "America/New_York"),
    "new york, us": ObserverLocation("New York, US", 40.7128, -74.0060, "America/New_York"),
    "london": ObserverLocation("London, UK", 51.5072, -0.1276, "Europe/London"),
    "london, uk": ObserverLocation("London, UK", 51.5072, -0.1276, "Europe/London"),
}


def _parse_location(location: str) -> ObserverLocation:
    normalized = " ".join(location.strip().lower().split())
    if normalized in _KNOWN_LOCATIONS:
        return _KNOWN_LOCATIONS[normalized]

    parts = [part.strip() for part in location.split(",")]
    if len(parts) == 2:
        try:
            latitude = float(parts[0])
            longitude = float(parts[1])
        except ValueError:
            pass
        else:
            if not -90.0 <= latitude <= 90.0:
                raise ValueError("Latitude must be between -90 and 90 degrees.")
            if not -180.0 <= longitude <= 180.0:
                raise ValueError("Longitude must be between -180 and 180 degrees.")
            return ObserverLocation(location.strip(), latitude, longitude, "UTC")

    raise ValueError(
        "Unknown location. Use '<latitude>, <longitude>' or one of: "
        + ", ".join(sorted(location.name for location in set(_KNOWN_LOCATIONS.values())))
        + "."
    )


def _moon_alt_deg(observer, input_time: datetime) -> float:
    """Calculate the moon's altitude at a given time"""
    t = _ts.from_datetime(input_time)
    moon_relative_apparent_pos = observer.at(t).observe(_moon).apparent()
    alt, _, _ = moon_relative_apparent_pos.altaz()
    return alt.degrees


def run_alti(target_alti: float, location: str, observation_date: date) -> str:
    """Run the alti command calculation to determine when the _moon will reach a
       target altitude (angle of elevation) in the sky above the horizon"""

    if target_alti < -90.0 or target_alti > 90.0:
        raise ValueError(
            f"Target altitude {target_alti} is outside of the valid range: -90 to 90 degrees."
        )

    parsed_location = _parse_location(location)
    location_timezone = ZoneInfo(parsed_location.timezone_name)
    observer = _earth + wgs84.latlon(parsed_location.latitude, parsed_location.longitude)

    def _f(dt: datetime) -> float:
        return _moon_alt_deg(observer, dt) - target_alti

    start_local = datetime.combine(observation_date, time.min, tzinfo=location_timezone)
    end_local = start_local + timedelta(days=1)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)

    events = []
    step = timedelta(minutes=5)
    t0 = start_utc
    f0 = _f(t0)

    while t0 < end_utc:
        t1 = min(t0 + step, end_utc)
        f1 = _f(t1)

        if f0 == 0.0:
            events.append(t0)
        elif f0 * f1 < 0:
            root_seconds = brentq(
                lambda seconds: _f(t0 + timedelta(seconds=seconds)),
                0,
                (t1 - t0).total_seconds(),
            )
            event_utc = t0 + timedelta(seconds=root_seconds)
            events.append(event_utc)

        t0 = t1
        f0 = f1

    if not events:
        return (
            f"The Moon does not reach {target_alti:g} degrees altitude over "
            f"{parsed_location.name} on {observation_date:%m/%d/%Y}."
        )

    lines = [
        f"Moon altitude crossings for {parsed_location.name}",
        f"Date: {observation_date:%m/%d/%Y}",
        f"Target altitude: {target_alti:g} degrees",
    ]
    for event_utc in events:
        event_local = event_utc.astimezone(location_timezone)
        lines.append(f"- {event_local:%Y-%m-%d %H:%M:%S %Z} ({event_utc:%H:%M:%S} UTC)")

    return "\n".join(lines)
