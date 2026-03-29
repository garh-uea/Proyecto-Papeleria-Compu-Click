from flask_login import UserMixin
from Conexion.conexion import obtener_conexion

class Usuario(UserMixin):
    def __init__(self, id_usuario, usuario, nombre, email, password):
        self.id = id_usuario
        self.usuario = usuario
        self.nombre = nombre
        self.email = email
        self.password = password


def obtener_usuario_por_id(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = "SELECT * FROM usuarios WHERE id_usuario = %s"
    cursor.execute(sql, (id_usuario,))
    user = cursor.fetchone()

    conexion.close()

    if user:
        return Usuario(
            user['id_usuario'],
            user['usuario'],
            user['nombre'],
            user['email'],
            user['password']
        )
    return None