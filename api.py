from dataclasses import asdict
from sqlite3 import IntegrityError

from db_setup import create_connection
from flask import Flask, g, request

from queries import query_all_international_usage, update_international_usage, add_international_usage, \
    delete_international_usage
from data_definition import InternationalUsage

app = Flask(__name__)
app.config['DB_NAME'] = 'prod.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = create_connection(app.config['DB_NAME'])
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/internet-usage")
def handler_internet_usage():
    country = request.args.get('country')
    year = request.args.get('year')
    db = get_db()
    data = query_all_international_usage(db, year, country)
    return [asdict(a) for a in data]


@app.route("/internet-usage", methods=['POST'])
def handler_add_internet_usage():
    db = get_db()
    content = request.json

    try:
        body_data = InternationalUsage(**content)
    except TypeError:
        return "error in attribute(s) name(s)", 400
    try:
        data = add_international_usage(db, body_data)
    except IntegrityError:
        return "record for the country an year already exists", 400
    return asdict(data), 201


@app.route("/internet-usage/<country>/<year>", methods=['PUT'])
def handler_update_internet_usage(country, year):
    db = get_db()
    new_fields = request.json
    if "Country" in new_fields:
        if new_fields["Country"] != country:
            return "country in body is different than country in url", 400
        else:
            del new_fields["Country"]
    if "Year" in new_fields:
        if new_fields["Year"] != country:
            return "year in body is different than year in url", 400
        else:
            del new_fields["Year"]

    try:
        data, updated = update_international_usage(db, country, year, new_fields)
    except TypeError:
        return "error in attribute(s) name(s)", 400

    if updated:
        return asdict(data)
    else:
        return asdict(data), 201


@app.route("/internet-usage/<country>/<year>", methods=['DELETE'])
def handler_delete_internet_usage(country, year):
    db = get_db()
    print(country, year)
    delete_international_usage(db, country, year)
    return "", 204
