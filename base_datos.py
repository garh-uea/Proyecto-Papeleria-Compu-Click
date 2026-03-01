import sqlite3

# Función para conectar a la base de datos
def obtener_conexion():
    conexion = sqlite3.connect("inventario.db")
    conexion.row_factory = sqlite3.Row
    return conexion

# Crear tablas
def crear_tablas():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        precio REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        correo TEXT
    )
    """)

    conexion.commit()
    conexion.close()