import os
import re
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ANSWERS = {
    "trip_name": "ICIS 2026",
    "trip_year": 2026,
    "destination": "Sydney, Australia",
    "start_date": "2026-12-01",
    "end_date": "2026-12-05",
}


def test_copier_generates_rendered_trip(tmp_path):
    destination = tmp_path / "2026-12-ICIS"
    command = [
        "copier",
        "copy",
        "--trust",
        "--defaults",
    ]
    for key, value in ANSWERS.items():
        command.extend(["--data", f"{key}={value}"])
    command.extend([
        str(ROOT),
        str(destination),
    ])
    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = os.devnull

    subprocess.run(command, check=True, cwd=tmp_path, env=env, capture_output=True, text=True)

    trip = yaml.safe_load((destination / "trip.yml").read_text())
    assert trip["trip_name"] == ANSWERS["trip_name"]
    assert trip["destination"] == ANSWERS["destination"]
    assert trip["start_date"] == ANSWERS["start_date"]
    assert trip["end_date"] == ANSWERS["end_date"]
    assert trip["year"] == ANSWERS["trip_year"]
    assert isinstance(trip["year"], int)

    rendered_files = [path for path in destination.rglob("*") if path.is_file()]
    for path in rendered_files:
        content = path.read_text(errors="replace")
        assert re.search(r"{{.*?}}", content, re.DOTALL) is None, path

    itinerary = (destination / "itinerary.md").read_text()
    readme = (destination / "README.md").read_text()
    assert ANSWERS["trip_name"] in itinerary
    assert ANSWERS["start_date"] in itinerary
    assert ANSWERS["end_date"] in itinerary
    for value in (ANSWERS["trip_name"], ANSWERS["destination"], ANSWERS["start_date"], ANSWERS["end_date"]):
        assert value in readme
