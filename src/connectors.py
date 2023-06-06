# -*- coding: UTF-8 -*-
import concurrent.futures
import os
import sys
from time import perf_counter

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from psycopg2 import Error as psycopgError
from psycopg2.extensions import AsIs, register_adapter
from psycopg2.pool import ThreadedConnectionPool

from src.queries import (
    get_carbonates_mr,
    get_carbonates_mindat
)
from src.utils import prepare_minerals

register_adapter(np.int64, AsIs)
load_dotenv(".envs/.local/.mindat")
load_dotenv(".envs/.local/.mr")


class Connection:
    def __init__(self):
        self.mindat_connection_params = (
            f"mysql+pymysql://"
            f"{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@127.0.0.1/"
            f"{os.getenv('MYSQL_DATABASE')}"
        )
        self.mr_connection_params = {
            "dbname": os.getenv("POSTGRES_DB"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "host": os.getenv("POSTGRES_HOST"),
            "port": os.getenv("POSTGRES_PORT"),
        }
        self.pool = None

        self.carbonates_mr = None
        self.carbonates_mindat = None

    def connect_db(self):

        try:
            self.pool = ThreadedConnectionPool(
                minconn=1, maxconn=50, **self.mr_connection_params
            )
            print("Pool with MR database created.")
        except psycopgError as e:
            print("An error occurred when establishing a connection with mr db: %s" % e)
            sys.exit(1)

    def disconnect_db(self):
        print("disconnecting from db...")
        self.pool.closeall()

    def fetch_tables(self):

            s = perf_counter()
            queries = [
                { "obj_name": "carbonates_mr", "query": get_carbonates_mr },
            ]

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_table = {
                    executor.submit(self.psql_pd_get, **query): query for query in queries
                }
                for future in concurrent.futures.as_completed(future_to_table):
                    try:
                        future.result()
                    except Exception as e:
                        print("an error occurred when running query: %s" % e)

            elapsed = perf_counter() - s
            print(f"Tables generated in {elapsed:0.2f} seconds.")

    def psql_pd_get(self, query, obj_name):
        try:
            conn = self.pool.getconn()
            retrieved_ = (
                pd.read_sql_query(
                    query,
                    conn,
                )
                .fillna(value=np.nan)
                .reset_index(drop=True)
            )
            setattr(self, obj_name, retrieved_)

        except Exception as e:
            print("An error occurred when creating %s: %s" % (obj_name, e))

        finally:
            self.pool.putconn(conn)

    def get_minerals(self):

        try:
            minerals_ = (
                pd.read_sql_query(
                    get_carbonates_mindat,
                    self.mindat_connection_params,
                )
                .fillna(value=np.nan)
                .sort_values("name")
                .reset_index(drop=True)
            )
            self.carbonates_mindat = prepare_minerals(minerals_)

        except Exception as e:
            print(f"An error occurred when creating minerals: {e}")
