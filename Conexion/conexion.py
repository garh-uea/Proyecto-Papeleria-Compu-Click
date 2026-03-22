import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="compu_click",
            port=3306,
            auth_plugin='mysql_native_password',
            use_pure=True
        )

        if conexion.is_connected():
            return conexion

    except Error as e:
        print("ERROR MYSQL:")
        print(e)
        return None