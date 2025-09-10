from flask import Flask, render_template, request, redirect, url_for, Response, session, flash
from flask_mysqldb import MySQL

# Inicializamos la aplicación Flask
app = Flask(__name__)

app.secret_key = 'appsecretkey' #clave secreta para la sesion

mysql=MySQL() #inicializa la conexion a la DB

# conexion a la DB
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ventas'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql.init_app(app) #inicializa la conexion a la DB

@app.route('/accesologin', methods=['GET', 'POST'])
def accesologin():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuario WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['usuario'] = user['email']
            session['rol'] = user['id_rol']
            
            # Redirige según el rol del usuario
            if user['id_rol'] == 1:
                return render_template("admin.html" , usuario=user['email'])  # Página de administrador
            else:
                return render_template("index.html" , usuario=user['email'])
            
        else:
            flash ('Usuario y contraseña son incorrectos', 'danger')
        return render_template("login.html")
          
 

# ----------------- RUTAS -----------------

@app.route('/')
def inicio():
    return render_template("index.html")
@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    user = {'nombre': '', 'email': '', 'mensaje': ''}
    if request.method == 'GET':
        user['nombre'] = request.args.get('nombre', '')
        user['email'] = request.args.get('email', '')
        user['mensaje'] = request.args.get('mensaje', '')
    return render_template("contacto.html", usuario=user)

@app.route('/contactopost', methods=['GET', 'POST'])
def contactopost():
    user = {'nombre': '', 'email': '', 'mensaje': ''}
    if request.method == 'POST':
        user['nombre'] = request.form.get('nombre', '')
        user['email'] = request.form.get('email', '')
        user['mensaje'] = request.form.get('mensaje', '')
    return render_template("contactopost.html", usuario=user)

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/Registro', methods=['GET', 'POST'])
def Registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        id_rol = 2  # Rol usuario por defecto

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, %s)",
                    (nombre, email, password, id_rol))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('inicio'))

    return render_template("registro.html")

@app.route('/usuario')
def usuario():
    return render_template("usuario.html")

@app.route('/acercade')
def acercade():
    return render_template("acercade.html")
   

# ----------------- MAIN -----------------
if __name__ == '__main__':
    app.run(debug=True, port=8000)
