# -*- coding: utf-8 -*-

import psycopg2
import sqlalchemy.pool as pool


def get_connection():
    """ """
    connection = psycopg2.connect(user="foo", host="127.0.0.1", port=5432, dbname="foo")
    return connection


connection_poll = pool.QueuePool(get_connection, max_overflow=10, pool_size=50)
