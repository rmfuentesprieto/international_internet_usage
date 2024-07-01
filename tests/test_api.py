import contextlib
import json
import os
from pathlib import Path

import pytest
from api import app as app_test
from load_data import load_and_insert

base_dir = Path(os.path.dirname(os.path.realpath(__file__)))


@contextlib.contextmanager
def api_setup(db_name: Path, data_files: Path):
    if db_name.exists():
        db_name.unlink()

    app_test.config.update({
        "TESTING": True,
        "DB_NAME": db_name
    })

    load_and_insert(data_files, 0, db_name)

    yield app_test


def test_get_all():
    with api_setup(base_dir.joinpath("test_get_all.db"), base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()
        a = client.get("/internet-usage")
        assert a.status_code == 200
        json_data = json.loads(a.data)
        assert len(json_data) == 8


def test_use_one_filter_year():
    with api_setup(base_dir.joinpath("test_use_one_filter_year.db"), base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()
        a = client.get("/internet-usage?year=2015")
        assert a.status_code == 200
        json_data = json.loads(a.data)
        assert len(json_data) == 2

        assert json_data[0]["Year"] == 2015
        assert json_data[1]["Year"] == 2015

        if json_data[0]["Country"] == "Burundi":
            assert json_data[0]["UsagePercentage"] == 4.8662
            assert json_data[1]["UsagePercentage"] == 42.68
        else:
            assert json_data[1]["UsagePercentage"] == 4.8662
            assert json_data[0]["UsagePercentage"] == 42.68


def test_use_one_filter_country():
    with api_setup(base_dir.joinpath("test_use_one_filter_country.db"), base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()
        a = client.get("/internet-usage?country=Burundi")
        assert a.status_code == 200
        json_data = json.loads(a.data)
        assert len(json_data) == 3

        assert json_data[0]["Country"] == "Burundi"
        assert json_data[1]["Country"] == "Burundi"
        assert json_data[2]["Country"] == "Burundi"


def test_use_filter_country_and_name():
    with api_setup(base_dir.joinpath("test_use_filter_country_and_name.db"), base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()
        a = client.get("/internet-usage?country=Burundi&year=2017")
        assert a.status_code == 200
        json_data = json.loads(a.data)
        assert len(json_data) == 1

        assert json_data[0]["Country"] == "Burundi"
        assert json_data[0]["Year"] == 2017
        assert json_data[0]["UsagePercentage"] == 2.6607


def test_filter_year_not_exist():
    with api_setup(base_dir.joinpath("test_filter_year_not_exist.db"), base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()
        a = client.get("/internet-usage?year=1990")
        assert a.status_code == 200
        json_data = json.loads(a.data)
        assert len(json_data) == 0


def test_filter_country_not_exist():
    with api_setup(base_dir.joinpath("test_get_filter_year_not_exist.db"), base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()
        a = client.get("/internet-usage?country=Chile")
        assert a.status_code == 200
        json_data = json.loads(a.data)
        assert len(json_data) == 0


def test_add_data():
    with api_setup(base_dir.joinpath("test_add_data.db"), base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()
        a = client.post("/internet-usage", json={
            "Country": "Chile",
            "Year": 2015,
            "UsagePercentage": 3.2,
            "Source": "entel",
        })
        assert a.status_code == 201
        json_data = json.loads(a.data)

        assert json_data["Country"] == "Chile"
        assert json_data["Year"] == 2015
        assert json_data["UsagePercentage"] == 3.2
        assert json_data["Source"] == "entel"


def test_add_data_missing_filed():
    with api_setup(base_dir.joinpath("test_add_data_missing_filed.db"), base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()
        a = client.post("/internet-usage", json={
            "Country": "Chile",
            "Year": 2015,
            "UsagePercentage": 3.2,
        })
        assert a.status_code == 400


def test_add_data_repeated_field():
    with api_setup(base_dir.joinpath("test_add_data_repeated_field.db"), base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()
        a = client.post("/internet-usage", json={
            "Country": "Burundi",
            "Year": 2015,
            "UsagePercentage": 4.8662,
            "Source": "International Telecommunication Union (ITU)",
        })
        assert a.status_code == 400


def test_remove_data():
    with api_setup(base_dir.joinpath("test_remove_data.db"), base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()

        resp = client.get("/internet-usage")
        assert resp.status_code == 200
        json_data = json.loads(resp.data)
        assert len(json_data) == 8

        resp = client.delete("/internet-usage/Burundi/2015")
        assert resp.status_code == 204

        resp = client.get("/internet-usage")
        assert resp.status_code == 200
        json_data = json.loads(resp.data)
        assert len(json_data) == 7


def test_remove_data_pair_does_not_exist():
    with api_setup(base_dir.joinpath("test_remove_data_pair_does_not_exist.db"),
                   base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()

        resp = client.delete("/internet-usage/Chile/2015")
        assert resp.status_code == 204

        resp = client.delete("/internet-usage/Chile/2015")
        assert resp.status_code == 204


def test_update_existing_data():
    with api_setup(base_dir.joinpath("test_update_existing_data.db"), base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()

        resp = client.put("/internet-usage/Burundi/2015", json={
            "UsagePercentage": 3.2,
        })
        assert resp.status_code == 200

        resp = client.get("/internet-usage?country=Burundi&year=2015")
        assert resp.status_code == 200
        json_data = json.loads(resp.data)

        assert json_data[0]["Country"] == "Burundi"
        assert json_data[0]["Year"] == 2015
        assert json_data[0]["UsagePercentage"] == 3.2
        assert json_data[0]["Source"] == "International Telecommunication Union (ITU)"


def test_update_existing_data_mismatch_year():
    with api_setup(base_dir.joinpath("test_update_existing_data_mismatch_year.db"),
                   base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()

        resp = client.put("/internet-usage/Burundi/2015", json={
            "UsagePercentage": 3.2,
            "Year": 2000
        })
        assert resp.status_code == 400


def test_update_new_data():
    with api_setup(base_dir.joinpath("test_update_new_data.db"), base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()

        resp = client.put("/internet-usage/Burundi/2014", json={
            "UsagePercentage": 3.2,
            "Source": "International Telecommunication Union (ITU)",
        })
        assert resp.status_code == 201

        resp = client.get("/internet-usage?country=Burundi&year=2014")
        assert resp.status_code == 200
        json_data = json.loads(resp.data)

        assert json_data[0]["Country"] == "Burundi"
        assert json_data[0]["Year"] == 2014
        assert json_data[0]["UsagePercentage"] == 3.2
        assert json_data[0]["Source"] == "International Telecommunication Union (ITU)"


def test_update_new_data_missing_filed():
    with api_setup(base_dir.joinpath("test_update_new_data_missing_filed.db"),
                   base_dir.joinpath("test_data.csv")) as app:
        client = app.test_client()

        resp = client.put("/internet-usage/Burundi/2014", json={
            "UsagePercentage": 3.2,
        })
        assert resp.status_code == 400
