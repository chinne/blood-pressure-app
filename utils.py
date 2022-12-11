import sqlite3
import pandas as pd
import locale
import logging


def init_db(db: str):
    # Create a connection to the database
    conn = create_connection(db)

    # Create the "pulse_data" table if it doesn't exist
    if conn is not None:
        create_table_file = """CREATE TABLE IF NOT EXISTS pulse_data (
                                    date timestamp,
                                    systolic integer,
                                    diastolic integer,
                                    pulse integer,
                                    notes text,
                                    measurement_method text,
                                    row_hash text,
                                    last_update timestamp default now()
                                );"""
        create_table(conn, create_table_file)

    return conn


def create_connection(db_file: str):
    """create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        logging.error(e)
    return conn


def create_table(conn, create_table_sql: str):
    """create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        logging.error(e)


def get_critical_values(df: pd.DataFrame) -> list:
    critical_list = []
    # Get the columns that we want to check
    systolic = df["systolic"]
    diastolic = df["diastolic"]
    pulse = df["pulse"]
    date = df["date"]

    # Iterate over the rows of the DataFrame
    for i in range(len(df)):
        # Check if any of the values are critical
        if (
                systolic.iloc[i] > 140
                or diastolic.iloc[i] > 90
                or pulse.iloc[i] > 100
                or pulse.iloc[i] < 60
        ):
            critical_list.append(date.iloc[i])

    return critical_list


def transform_df_date(df: pd.DataFrame) -> pd.DataFrame:
    # Set the locale to German
    locale.setlocale(locale.LC_ALL, "de_DE")

    # Create a new "date" column by combining the "Datum" and "Zeit" columns
    df["date"] = pd.to_datetime(df["Datum"] + df["Zeit"], format="%d. %B %Y%H:%M")

    # Drop the "Datum" and "Zeit" columns
    df.drop(columns=["Datum", "Zeit"], inplace=True)
    return df
