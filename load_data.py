from pathlib import Path

from db_setup import create_connection
from queries import add_international_usage

from data_definition import InternationalUsage

import csv


def retrieve_csv_data(file: Path, skip_lines):
    if not file.exists():
        raise Exception("file does not exits " + str(file))

    data = []

    region_counter = 0
    with file.open() as lFile:
        csv_reader = csv.DictReader(lFile, delimiter=",")

        for row in csv_reader:
            if region_counter + 1 > skip_lines:
                year = int(row["Year"])
                usage_percentage = float(row["Percentage of individuals using the internet"])
                data.append(
                    InternationalUsage(
                        row["Region/Country/Area"],
                        year,
                        usage_percentage,
                        row["Source"],
                    )
                )
            region_counter += 1

    return data


def load_and_insert(file: Path, skip_lines, db_name="prod.db"):
    data_to_insert = retrieve_csv_data(file, skip_lines)
    db = create_connection(db_name)
    for record in data_to_insert:
        add_international_usage(db, record)


if __name__ == '__main__':
    load_and_insert(
        Path("UN_SYB63_314_202009_Internet_Usage - Sheet1 (1).csv"),
        138,
    )
