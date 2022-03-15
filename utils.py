import sqlite3
import pandas as pd
import locale


def init_db(db: str):
    conn = create_connection(db)
    # create tables
    if conn is not None:
        # create projects table
        # create_table_file = f'"""{open("create_table.sql", "r").read()}"""'
        create_table_file = """CREATE TABLE IF NOT EXISTS pulse_data (
                    date timestamp,
                    systolic integer,
                    diastolic integer,
                    pulse integer,
                    notes text,
                    measurement_method text,
                    row_hash text,
                    last_update timestamp
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
        print(e)
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
        print(e)


def get_critical_values(df: pd.DataFrame) -> list:
    critical_list = []
    for i, row in df.iterrows():
        if (
            row.iloc[1] > 140
            or row.iloc[2] > 90
            or row.iloc[3] > 100
            or row.iloc[3] < 60
        ):
            critical_list.append(row["Datum"])
    return critical_list


def transform_df_date(df: pd.DataFrame) -> pd.DataFrame:
    locale.setlocale(locale.LC_ALL, "de_DE")
    df["Datum"] = pd.to_datetime(df["Datum"] + df["Zeit"], format="%d. %B %Y%H:%M")
    df.drop(columns="Zeit", inplace=True)
    return df
