# config/db_config.py

from flask_mysqldb import MySQL
import os

def init_mysql(app):
    app.config['MYSQL_HOST'] = os.getenv("DB_HOST", "localhost")
    app.config['MYSQL_USER'] = os.getenv("DB_USER", "root")
    app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASSWORD", "")
    app.config['MYSQL_DB'] = os.getenv("DB_NAME", "inventory_system")
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    mysql = MySQL(app)
    app.mysql = mysql  
    return mysql
