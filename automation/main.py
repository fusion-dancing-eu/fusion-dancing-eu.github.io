from pathlib import Path
import sys
import pandas as pd
import yaml
from io import StringIO
import requests

HERE = Path(__file__).parent


def main(sheet_csv_url: str, output_yaml_file_path: Path):
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

    df["start"] = pd.to_datetime(df["start"]).dt.strftime("%Y-%m-%dT%H:%M:%S")
    df["end"] = pd.to_datetime(df["end"]).dt.strftime("%Y-%m-%dT%H:%M:%S")

    # # Extract year and group by it
    # df["year"] = pd.to_datetime(df["start"], errors="coerce").dt.year
    # grouped_data = (
    #     df.groupby("year")
    #     .apply(lambda x: x.drop(columns=["year"]).to_dict(orient="records"))
    #     .to_dict()
    # )

    yaml_output = yaml.dump(
        df.to_dict(orient="records"), sort_keys=False, allow_unicode=True
    )
    output_yaml_file_path.write_text(yaml_output)


if __name__ == "__main__":
    errors = False
    for name, url in {
        "darmstadt": "https://docs.google.com/spreadsheets/d/1xH5iBL0r9ex9bE934b-IPXQeCnpiV-oxsgWJVqLrzCY/gviz/tq?tqx=out:csv&sheet=Darmstadt",
        "frankfurt": "https://docs.google.com/spreadsheets/d/1xH5iBL0r9ex9bE934b-IPXQeCnpiV-oxsgWJVqLrzCY/gviz/tq?tqx=out:csv&sheet=Frankfurt",
        "heidelberg": "https://docs.google.com/spreadsheets/d/1xH5iBL0r9ex9bE934b-IPXQeCnpiV-oxsgWJVqLrzCY/gviz/tq?tqx=out:csv&sheet=Heidelberg",
    }.items():
        try:
            main(
                sheet_csv_url=url,
                output_yaml_file_path=HERE.parent / "data" / f"{name}.yaml",
            )
        except Exception as e:
            print(f"Error for ${name}:", e)
            errors = True
    if errors:
        sys.exit(1)
