from flask import Flask, render_template, request, redirect, url_for
from modelos import Inventario, crear_tablas

app = Flask(__name__)

# Crear tabla automáticamente
crear_tablas()

inventario = Inventario()

# ================= INICIO =================
@app.route('/')
def inicio():
    return render_template('index.html')


# ================= CONTACTOS =================
@app.route('/contactos')
def contactos():
    return render_template('contactos.html')


# ================= SOBRE NOSOTROS =================
@app.route('/sobre-nosotros')
def about():
    return render_template('sobre-nosotros.html')


# ================= REGISTRO =================
@app.route('/registro')
def registro():
    return render_template('registro.html')


# ================= INVENTARIO =================
@app.route('/inventario')
def ver_inventario():
    productos = inventario.obtener_todos()
    return render_template('inventario.html', productos=productos)


# ================= AGREGAR PRODUCTO =================
@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])

        inventario.agregar_producto(nombre, cantidad, precio)
        return redirect(url_for('ver_inventario'))

    return render_template('agregar_producto.html')


# ================= EDITAR PRODUCTO =================
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
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
def eliminar(id):
    inventario.eliminar_producto(id)
    return redirect(url_for('ver_inventario'))


if __name__ == '__main__':
    app.run(debug=True)