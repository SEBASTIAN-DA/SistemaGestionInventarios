from flask_mysql_connector import MySQL

mysql = MySQL()

def init_mysql(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'admin'
    app.config['MYSQL_DATABASE'] = 'dbgestioninventarios' 
    app.config['MYSQL_DB'] = 'dbgestioninventarios'      

    mysql.init_app(app)
    return mysql
