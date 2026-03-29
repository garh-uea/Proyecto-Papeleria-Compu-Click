from Conexion.conexion import obtener_conexion

class Inventario:

    def agregar_producto(self, nombre, precio, stock, imagen):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        sql = """
        INSERT INTO producto (nombre, precio, stock, imagen)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(sql, (nombre, precio, stock, imagen))
        conexion.commit()
        conexion.close()

    def obtener_todos(self):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM producto")
        datos = cursor.fetchall()

        conexion.close()
        return datos

    def buscar(self, texto):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        sql = "SELECT * FROM producto WHERE nombre LIKE %s"
        cursor.execute(sql, (f"%{texto}%",))
        datos = cursor.fetchall()

        conexion.close()
        return datos

    def obtener_por_id(self, id):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM producto WHERE id_producto=%s", (id,))
        dato = cursor.fetchone()

        conexion.close()
        return dato

    def actualizar_producto(self, id, nombre, precio, stock):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        sql = """
        UPDATE producto 
        SET nombre=%s, precio=%s, stock=%s 
        WHERE id_producto=%s
        """

        cursor.execute(sql, (nombre, precio, stock, id))
        conexion.commit()
        conexion.close()

    def eliminar_producto(self, id):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM producto WHERE id_producto=%s", (id,))
        conexion.commit()
        conexion.close()