import sqlite3
import os

# Ruta absoluta de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_DB = os.path.join(BASE_DIR, "papeleria.db")


# ================== CREAR TABLAS ==================
def crear_tablas():
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()


# ================== CLASE INVENTARIO ==================
class Inventario:

    def agregar_producto(self, nombre, cantidad, precio):
        conexion = sqlite3.connect(RUTA_DB)
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
            (nombre, cantidad, precio)
        )

        conexion.commit()
        conexion.close()

    def obtener_todos(self):
        conexion = sqlite3.connect(RUTA_DB)
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()

        conexion.close()
        return productos

    def obtener_por_id(self, id):
        conexion = sqlite3.connect(RUTA_DB)
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM productos WHERE id = ?", (id,))
        producto = cursor.fetchone()

        conexion.close()
        return producto

    def actualizar_producto(self, id, nombre, cantidad, precio):
        conexion = sqlite3.connect(RUTA_DB)
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE productos
            SET nombre = ?, cantidad = ?, precio = ?
            WHERE id = ?
        """, (nombre, cantidad, precio, id))

        conexion.commit()
        conexion.close()

    def eliminar_producto(self, id):
        conexion = sqlite3.connect(RUTA_DB)
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM productos WHERE id = ?", (id,))
        conexion.commit()

        conexion.close()