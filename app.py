from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from inventario import Inventario, crear_tablas
from productos import PersistenciaArchivos
from Conexion.conexion import obtener_conexion
from models import Usuario, obtener_usuario_por_email, obtener_usuario_por_id

app = Flask(__name__)
app.secret_key = "clave_secreta"

# ================= FLASK LOGIN =================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ================= CREAR TABLAS =================
crear_tablas()

inventario = Inventario()
archivos = PersistenciaArchivos()

# ================= CARGAR USUARIO =================
@login_manager.user_loader
def load_user(user_id):
    return obtener_usuario_por_id(user_id)

# ================= INICIO =================
@app.route('/')
def inicio():
    nombre = current_user.nombre if current_user.is_authenticated else None
    return render_template('index.html', nombre=nombre)

# ================= CONTACTOS (RECUPERADO) =================
@app.route('/contactos')
def contactos():
    return render_template('contactos.html')

# ================= SOBRE NOSOTROS (RECUPERADO) =================
@app.route('/sobre-nosotros')
def about():
    return render_template('sobre-nosotros.html')

# ================= LOGIN =================
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        usuario = request.form['usuario']   # 🔥 CAMBIO: ahora es usuario
        password = request.form['password']

        # 🔥 NUEVA CONSULTA DIRECTA A MYSQL
        conexion = obtener_conexion()

        if conexion is None:
            return "Error de conexión a la base de datos"

        cursor = conexion.cursor(dictionary=True)

        sql = "SELECT * FROM usuarios WHERE usuario = %s"
        cursor.execute(sql, (usuario,))
        user_data = cursor.fetchone()

        conexion.close()

        # 🔥 VALIDACIÓN
        if user_data and user_data['password'] == password:
            user = Usuario(
                id_usuario=user_data['id_usuario'],
                usuario=user_data['usuario'],
                nombre=user_data['nombre'],
                email=user_data['email'],
                password=user_data['password']
            )

            login_user(user)
            return redirect(url_for('ver_inventario'))
        else:
            return "Credenciales incorrectas"

    return render_template('login.html')

# ================= LOGOUT =================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/registro', methods=['GET','POST'])
def registro():

    if request.method == 'POST':

        usuario = request.form['usuario']
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']

        conexion = obtener_conexion()

        if conexion is None:
            return "Error de conexión a la base de datos"

        cursor = conexion.cursor()

        sql = """
        INSERT INTO usuarios (usuario, nombre, email, password)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(sql,(usuario,nombre,email,password))

        conexion.commit()
        conexion.close()

        return redirect(url_for('login'))

    return render_template('registro.html')



# ================= INVENTARIO (PROTEGIDO) =================
@app.route('/inventario')
@login_required
def ver_inventario():
    productos = inventario.obtener_todos()
    return render_template('inventario.html', productos=productos)

# ================= AGREGAR PRODUCTO =================
@app.route('/agregar', methods=['GET','POST'])
@login_required
def agregar():

    if request.method == 'POST':

        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])

        inventario.agregar_producto(nombre,cantidad,precio)

        productos = inventario.obtener_todos()
        ultimo = productos[-1]

        id = ultimo[0]

        archivos.guardar_txt(id,nombre,cantidad,precio)
        archivos.guardar_json(id,nombre,cantidad,precio)
        archivos.guardar_csv(id,nombre,cantidad,precio)

        return redirect(url_for('ver_inventario'))

    return render_template('agregar_producto.html')

# ================= EDITAR PRODUCTO =================
@app.route('/editar/<int:id>', methods=['GET','POST'])
@login_required
def editar_producto(id):

    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])

        inventario.actualizar_producto(id, nombre, cantidad, precio)
        return redirect(url_for('ver_inventario'))

    producto = inventario.obtener_por_id(id)
    return render_template('editar_producto.html', producto=producto)

# ================= ELIMINAR PRODUCTO =================
@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    inventario.eliminar_producto(id)
    return redirect(url_for('ver_inventario'))

# ================= DATOS (PROTEGIDO) =================
@app.route("/datos")
@login_required
def ver_datos():

    datos_txt = archivos.leer_txt()
    datos_json = archivos.leer_json()
    datos_csv = archivos.leer_csv()

    return render_template(
        "datos.html",
        txt=datos_txt,
        json=datos_json,
        csv=datos_csv
    )

# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)