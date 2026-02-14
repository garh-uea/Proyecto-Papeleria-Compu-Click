from flask import Flask
app = Flask(__name__)
@app.route('/')
def Hello_world():
    return "Bienevenido a Papelería Compu Click en la ciudad de Tena"

@app.route('/usuario/<nombre>')
def usuario(nombre):
    return f'¡Hola {nombre}! Qué gusto tenerte en Papelería Compu Click!'

@app.route('/contactos')
def contactos():
    return f'📩 Escríbenos a compuclick_tena@gmail.com o al WhatsApp 0999532532. ¡Estamos listos para ayudarte!'

if __name__ == '__main__':
    app.run(debug=True)