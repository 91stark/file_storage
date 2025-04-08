from flask_mysqldb import MySQL

def init_mysql(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'root'  
    app.config['MYSQL_DB'] = 'file_storage'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    return MySQL(app)
