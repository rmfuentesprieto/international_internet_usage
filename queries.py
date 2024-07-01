from data_definition import InternationalUsage


def query_all_international_usage(db, filter_year, filter_country):
    cursor = db.cursor()
    query = """
    SELECT country, year, source, usage_percentage from international_usage
    """

    filters: list[str] = []
    params = []
    if filter_year is not None:
        filters.append("year = ?")
        params.append(filter_year)

    if filter_country is not None:
        filters.append("country = ?")
        params.append(filter_country)

    query_filters = " AND ".join(filters)

    query = f"{query} where {query_filters}" if query_filters else query

    response = cursor.execute(query, params)

    data = []
    for (country, year, source, usage_percentage) in response.fetchall():
        data.append(
            InternationalUsage(
                country,
                year,
                usage_percentage,
                source,
            )
        )
    return data


def delete_international_usage(db, country, year):
    query = """
        delete from international_usage where country = ? and year = ?
        """
    cursor = db.cursor()
    cursor.execute(query, (country, year))
    db.commit()


def add_international_usage(db, data):
    cursor = db.cursor()
    cursor.execute("""
    INSERT into international_usage(country, year, source, usage_percentage) values(
        ?,?,?,?
    )
    """, [data.Country, data.Year, data.Source, data.UsagePercentage])

    db.commit()

    return data


def __get_one_international_usage(db, country, year):
    query = """
           SELECT country, year, source, usage_percentage FROM international_usage WHERE country = ? AND year = ?
           """
    cursor = db.cursor()
    response = cursor.execute(query, (country, year))
    return response.fetchone()


def update_international_usage(db, country, year, new_fields: dict) -> (InternationalUsage, bool):
    existing = __get_one_international_usage(db, country, year)
    if existing is not None:
        data = InternationalUsage(
            existing[0],
            existing[1],
            existing[3],
            existing[2],
        )

        for k, v in new_fields.items():
            if k == "UsagePercentage":
                data.UsagePercentage = v
            elif k == "Source":
                data.Source = v

        cursor = db.cursor()
        cursor.execute(
            """
                UPDATE international_usage 
                SET source = ?, usage_percentage = ? 
                WHERE country = ? AND year = ?
            """,
            (data.Source, data.UsagePercentage, data.Country, data.Year),
        )

        db.commit()
        return data, True
    else:
        new_fields["Country"] = country
        new_fields["Year"] = year
        new_insert = InternationalUsage(**new_fields)
        add_international_usage(db, new_insert)
        return new_insert, False
