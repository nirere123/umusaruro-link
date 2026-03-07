# ================================================================
# FILE        : db.py
# MEMBER      : Benjamin
# PURPOSE     : Single place to create the MySQL connection.
#               Every other file imports get_db() from here.
#               Change DB settings here once — it updates everywhere.
# ================================================================

import mysql.connector
from flask import g, current_app


def get_db():
    """
    Returns a MySQL connection.
    Flask's 'g' object stores it for the duration of one request,
    so we don't open a new connection for every query.
    """
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host     = current_app.config['MYSQL_HOST'],
            user     = current_app.config['MYSQL_USER'],
            password = current_app.config['MYSQL_PASSWORD'],
            database = current_app.config['MYSQL_DB']
        )
    return g.db


def close_db(e=None):
    """Close the database connection at the end of each request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()
