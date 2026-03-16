import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="papeleria_compu_click",
            port=3306,
            use_pure=True  # evita el error del conector C
        )

        return conexion

    except Error as e:
        print("ERROR DE CONEXIÓN MYSQL:")
        print(e)
        return None