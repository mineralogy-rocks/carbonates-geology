# -*- coding: UTF-8 -*-
import concurrent.futures
import os
import re
import sys
from datetime import datetime
from time import perf_counter

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from psycopg2 import Error as psycopgError
from psycopg2.extensions import AsIs, register_adapter
from psycopg2.extras import execute_values
from psycopg2.pool import ThreadedConnectionPool

from src.queries import (
    get_minerals
)

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

        self.mineral_log = None
        self.mineral_history = None
        self.mineral_formula = None
        self.mineral_relation_suggestion = None

        self.minerals = None

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