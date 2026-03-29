from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from inventario import Inventario
from productos import PersistenciaArchivos
from Conexion.conexion import obtener_conexion
from models import Usuario, obtener_usuario_por_id
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from werkzeug.utils import secure_filename
import time
import os

app = Flask(__name__)
app.secret_key = "clave_secreta"

# CARPETA PARA IMÁGENES
CARPETA_IMAGENES = "static/img_productos"
app.config['CARPETA_IMAGENES'] = CARPETA_IMAGENES

# ================= FLASK LOGIN =================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

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

# ================= CONTACTOS =================
@app.route('/contactos')
def contactos():
    return render_template('contactos.html')

# ================= SOBRE NOSOTROS =================
@app.route('/sobre-nosotros')
def about():
    return render_template('sobre-nosotros.html')

# ================= LOGIN =================
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        usuario = request.form['usuario']
        password = request.form['password']

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        sql = "SELECT * FROM usuarios WHERE usuario = %s"
        cursor.execute(sql, (usuario,))
        user = cursor.fetchone()

        conexion.close()

        if user and check_password_hash(user['password'], password):

            user_obj = Usuario(
                id_usuario=user['id_usuario'],
                usuario=user['usuario'],
                nombre=user['nombre'],
                email=user['email'],
                password=user['password']
            )

            login_user(user_obj)
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

# ================= REGISTRO =================
@app.route('/registro', methods=['GET','POST'])
def registro():

    if request.method == 'POST':

        usuario = request.form['usuario']
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']

        password_encriptada = generate_password_hash(password)

        conexion = obtener_conexion()

        if conexion is None:
            return "Error de conexión a la base de datos"

        try:
            cursor = conexion.cursor()

            sql = """
            INSERT INTO usuarios (usuario, nombre, email, password)
            VALUES (%s, %s, %s, %s)
            """

            cursor.execute(sql,(usuario,nombre,email,password_encriptada))
            conexion.commit()

        except Exception as e:
            return f"Error al registrar: {e}"

        finally:
            cursor.close()
            conexion.close()

        return redirect(url_for('login'))

    return render_template('registro.html')


# ================= INVENTARIO =================
@app.route('/inventario', methods=['GET','POST'])
@login_required
def ver_inventario():

    if request.method == 'POST':
        texto = request.form['buscar']
        productos = inventario.buscar(texto)
    else:
        productos = inventario.obtener_todos()

    return render_template('inventario.html', productos=productos)


# ================= AGREGAR PRODUCTO =================
@app.route('/agregar', methods=['GET','POST'])
@login_required
def agregar():

    if request.method == 'POST':

        nombre = request.form['nombre']
        stock = int(request.form['stock'])
        precio = float(request.form['precio'])

        archivo = request.files.get('imagen')
        nombre_imagen = ""

        # Asegurar que exista la carpeta
        os.makedirs(app.config['CARPETA_IMAGENES'], exist_ok=True)

        # Validar imagen
        if archivo and archivo.filename != "":
            
            # Limpiar nombre Y evitar duplicados
            nombre_seguro = secure_filename(archivo.filename)
            nombre_imagen = f"{int(time.time())}_{nombre_seguro}"

            ruta = os.path.join(app.config['CARPETA_IMAGENES'], nombre_imagen)

            archivo.save(ruta)

        # GUARDAR EN BASE DE DATOS
        inventario.agregar_producto(nombre, precio, stock, nombre_imagen)

        productos = inventario.obtener_todos()
        ultimo = productos[-1]

        id = ultimo[0]

        archivos.guardar_txt(id, nombre, stock, precio)
        archivos.guardar_json(id, nombre, stock, precio)
        archivos.guardar_csv(id, nombre, stock, precio)

        return redirect(url_for('ver_inventario'))

    return render_template('agregar_producto.html')


# ================= EDITAR PRODUCTO =================
@app.route('/editar/<int:id>', methods=['GET','POST'])
@login_required
def editar_producto(id):

    producto = inventario.obtener_por_id(id)

    if request.method == 'POST':

        nombre = request.form['nombre']
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])

        archivo = request.files.get('imagen')
        nombre_imagen = producto[4]  # mantener imagen actual

        # asegurar carpeta
        os.makedirs(app.config['CARPETA_IMAGENES'], exist_ok=True)

        # Si se sube nueva imagen
        if archivo and archivo.filename != "":
            nombre_seguro = secure_filename(archivo.filename)
            nombre_imagen = f"{int(time.time())}_{nombre_seguro}"

            ruta = os.path.join(app.config['CARPETA_IMAGENES'], nombre_imagen)
            archivo.save(ruta)

        # Actualizar en Base de Datos
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        sql = """
        UPDATE producto 
        SET nombre=%s, precio=%s, stock=%s, imagen=%s
        WHERE id_producto=%s
        """

        cursor.execute(sql, (nombre, precio, stock, nombre_imagen, id))
        conexion.commit()
        conexion.close()

        return redirect(url_for('ver_inventario'))

    return render_template('editar_producto.html', producto=producto)


# ================= ELIMINAR PRODUCTO =================
@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    inventario.eliminar_producto(id)
    return redirect(url_for('ver_inventario'))


# ================= REPORTE PDF =================
@app.route('/reporte_pdf')
@login_required
def reporte_pdf():

    productos = inventario.obtener_todos()

    archivo = "reporte_productos.pdf"
    doc = SimpleDocTemplate(archivo)

    estilos = getSampleStyleSheet()
    elementos = []

    # ================= LOGO =================
    logo_path = "static/Multimedia/Compu_Click.png"
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=120, height=60)
        elementos.append(logo)

    elementos.append(Spacer(1, 15))

    # ================= TITULO =================
    titulo = Paragraph(
        "<para align='center'><b>REPORTE DE PRODUCTOS - COMPU CLICK</b></para>",
        estilos['Title']
    )
    elementos.append(titulo)

    elementos.append(Spacer(1, 25))

    # ================= TABLA =================
    data = [["ID", "Nombre", "Precio", "Stock", "Imagen"]]

    for p in productos:

        imagen_path = f"static/img_productos/{p[4]}" if p[4] else None

        if imagen_path and os.path.exists(imagen_path):
            img = Image(imagen_path, width=50, height=50)
        else:
            img = "Sin imagen"
        
        estilos = getSampleStyleSheet()
        estilo_celda = estilos["BodyText"]

        data.append([
            p[0],
            Paragraph(p[1], estilo_celda),
            f"${p[2]:.2f}",
            p[3],
            img
        ])
            
        tabla = Table(data, colWidths=[50, 120, 80, 60, 80])

    # ================= TABLA =================
    tabla.setStyle(TableStyle([

        # Encabezado
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),

        # Cuerpo
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('ALIGN', (0,1), (-2,-1), 'CENTER'),

        # Bordes
        ('GRID', (0,0), (-1,-1), 1, colors.black),

        # Filas alternas (zebra)
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),

        # Padding
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),

    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return send_file(archivo, as_attachment=True)


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

# ================= VENTAS =================
@app.route('/ventas', methods=['GET','POST'])
@login_required
def ventas():

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    # Consultar productos
    cursor.execute("SELECT id_producto, nombre, precio FROM producto")
    productos = cursor.fetchall()

    if request.method == 'POST':

        fecha = request.form.get('fecha')
        id_cliente = request.form.get('id_cliente')
        producto_id = request.form.get('producto_id')
        cantidad = request.form.get('cantidad')

        if not fecha or not id_cliente or not producto_id or not cantidad:
            return "⚠️ Todos los campos son obligatorios"

        try:
            id_cliente = int(id_cliente)
            producto_id = int(producto_id)
            cantidad = int(cantidad)
        except ValueError:
            return "⚠️ Datos inválidos"

        # Obtener precio
        cursor.execute("SELECT precio FROM producto WHERE id_producto=%s", (producto_id,))
        producto = cursor.fetchone()

        if not producto:
            return "⚠️ Producto no encontrado"

        precio = float(producto['precio'])
        total = precio * cantidad

        # Guardar venta
        sql = """
        INSERT INTO ventas (fecha, total, id_cliente)
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (fecha, total, id_cliente))
        conexion.commit()

        conexion.close()

        # MENSAJE EMERGENTE
        from flask import flash
        flash("✅ Venta registrada satisfactoriamente", "success")

        return redirect(url_for('ventas'))

    conexion.close()
    return render_template('ventas.html', productos=productos)


if __name__ == '__main__':
    app.run(debug=True)