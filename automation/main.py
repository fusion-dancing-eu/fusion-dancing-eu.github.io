from pathlib import Path
import sys
import pandas as pd
import yaml
from io import StringIO
import requests

HERE = Path(__file__).parent

SOURCES = [
    (
        "darmstadt",
        "Europe/Berlin",
        "https://docs.google.com/spreadsheets/d/1xH5iBL0r9ex9bE934b-IPXQeCnpiV-oxsgWJVqLrzCY/gviz/tq?tqx=out:csv&sheet=Darmstadt",
    ),
    (
        "frankfurt",
        "Europe/Berlin",
        "https://docs.google.com/spreadsheets/d/1xH5iBL0r9ex9bE934b-IPXQeCnpiV-oxsgWJVqLrzCY/gviz/tq?tqx=out:csv&sheet=Frankfurt",
    ),
    (
        "heidelberg",
        "Europe/Berlin",
        "https://docs.google.com/spreadsheets/d/1xH5iBL0r9ex9bE934b-IPXQeCnpiV-oxsgWJVqLrzCY/gviz/tq?tqx=out:csv&sheet=Heidelberg",
    ),
    (
        "stuttgart",
        "Europe/Berlin",
        "https://docs.google.com/spreadsheets/d/1xH5iBL0r9ex9bE934b-IPXQeCnpiV-oxsgWJVqLrzCY/gviz/tq?tqx=out:csv&sheet=Stuttgart",
    ),
]

GROUPS = {
    "rhein-main-neckar": ["darmstadt", "heidelberg", "frankfurt", "stuttgart"],
}


def to_yaml_file_path(name: str) -> Path:
    return HERE.parent / "data" / f"{name}.yaml"


def fetch_events(sheet_csv_url: str, output_yaml_file_path: Path, time_zone: str):
    # Google Sheet CSV URL
    response = requests.get(sheet_csv_url)
    response.raise_for_status()

    # Read CSV into DataFrame
    df = pd.read_csv(
        StringIO(response.text),
        usecols=["Title", "Start", "End", "Location", "Added", "Link"],
    )
    df = df.rename(columns={c: c.lower() for c in df.columns})

    df = df.fillna("")

    df["start"] = pd.to_datetime(df["start"], format="mixed")
    df["start_utc"] = (
        df["start"]
        .dt.tz_localize(time_zone)
        .dt.tz_convert("UTC")
        .dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    df["start"] = df["start"].dt.strftime("%Y-%m-%dT%H:%M:%S")

    df["end"] = pd.to_datetime(df["end"], format="mixed")
    df["end_utc"] = (
        df["end"]
        .dt.tz_localize(time_zone)
        .dt.tz_convert("UTC")
        .dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    df["end"] = df["end"].dt.strftime("%Y-%m-%dT%H:%M:%S")

    yaml_output = yaml.dump(
        df.to_dict(orient="records"), sort_keys=False, allow_unicode=True
    )
    output_yaml_file_path.write_text(yaml_output)


def generate_group(group: str, members: list[str]):
    events = []
    for member in members:
        events.extend(yaml.safe_load(to_yaml_file_path(member).read_text()))
    yaml_output = yaml.dump(events, sort_keys=False, allow_unicode=True)
    to_yaml_file_path(group).write_text(yaml_output)


if __name__ == "__main__":
    errors = False
    for name, time_zone, url in SOURCES:
        try:
            fetch_events(
                sheet_csv_url=url,
                output_yaml_file_path=to_yaml_file_path(name),
                time_zone=time_zone,
            )
        except Exception as e:
            print(f"Error fetching events for {name}:", e)
            errors = True
    if errors:
        sys.exit(1)

    for group, members in GROUPS.items():
        generate_group(group, members)
