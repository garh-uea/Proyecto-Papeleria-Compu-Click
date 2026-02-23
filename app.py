from flask import Flask, render_template

app = Flask(__name__)

# ================== INICIO ==================
@app.route('/')
def inicio():
    return render_template('index.html')

# ================== CONTACTOS ==================
@app.route('/contactos')
def contactos():
    return render_template('contactos.html')

# ================== SOBRE NOSOTROS ==================
@app.route('/sobre-nosotros')
def about():
    return render_template('sobre-nosotros.html')

# ================== REGISTRO ==================
@app.route('/registro')
def registro():
    return render_template('registro.html')

# ================== USUARIO DINÁMICO ==================
@app.route('/usuario/<nombre>')
def usuario(nombre):
    return render_template('index.html', nombre=nombre)

# ================== CONTACTOS ==================
@app.route('/contactos')
def contactos_dinamico():
    return render_template('contactos.html')

if __name__ == '__main__':
    app.run(debug=True)