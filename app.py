from flask import Flask

app = Flask(__name__)  # ¡Solo una asignación!

@app.route('/')
def home():
    return "¡Hola mundo!"

@app.route('/contacto')  # Asegúrate de que no haya espacios ni errores
def contacto():
    return "Página de contacto"

@app.route('/about')
def about():
    return "Página about"

@app.route('/servicios/<nombre>')
def servicios(nombre):
    return "elnombre del servicio es : %s" %nombre

@app.route('/edad/<edad>')
def edad(edad):
    return "la edad es : {} años" .format(edad)

@app.route('/suma/<int:num1>/<int:num2>')
def suma(num1,num2):
    resultado=num1+num2
    return "la suma de : {} y {} es: {}" .format(num1,num2,resultado)


@app.route('/edadvalor/<int:edad>')   # Ruta con parámetro entero
def edadvalor(edad):
    if edad < 18:
        return 'Eres menor de edad'
    elif edad >= 18 and edad < 65:
        return 'Eres mayor de edad tienes {} años'.format(edad)
    else:
        return 'Eres un adulto mayor, tienes {} años'.format(edad)





if __name__ == '__main__':
    app.run(debug=True, port=8000)  # Usará el puerto 8000