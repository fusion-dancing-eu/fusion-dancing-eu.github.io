from pathlib import Path
import sys
import pandas as pd
import yaml
from io import StringIO
import requests

HERE = Path(__file__).parent


def main(sheet_csv_url: str, output_yaml_file_path: Path, time_zone: str):
    # Google Sheet CSV URL
    response = requests.get(sheet_csv_url)
    response.raise_for_status()

    # Read CSV into DataFrame
    df = pd.read_csv(
        StringIO(response.text),
        usecols=["Title", "Start", "End", "Location", "Added", "Link"],
        parse_dates=["Start", "End"],
    )
    df = df.rename(columns={c: c.lower() for c in df.columns})

    df = df.fillna("")

    df["start_utc"] = (
        df["start"]
        .dt.tz_localize(time_zone)
        .dt.tz_convert("UTC")
        .dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    df["start"] = df["start"].dt.strftime("%Y-%m-%dT%H:%M:%S")
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


if __name__ == "__main__":
    errors = False
    for name, time_zone, url in [
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
    ]:
        try:
            main(
                sheet_csv_url=url,
                output_yaml_file_path=HERE.parent / "data" / f"{name}.yaml",
                time_zone=time_zone,
            )
        except Exception as e:
            print(f"Error for ${name}:", e)
            errors = True
    if errors:
        sys.exit(1)
