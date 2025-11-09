from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from passlib.hash import pbkdf2_sha256


# Inicializamos la aplicación Flask
app = Flask(__name__, template_folder='Templates')

app.secret_key = 'appsecretkey' #clave secreta para la sesion

mysql=MySQL() #inicializa la conexion a la DB

# conexion a la DB
app.config['MYSQL_HOST'] = 'bfpkhtu6hrcqo4x8mwkj-mysql.services.clever-cloud.com'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'up1m5qhdh34bkteh'
app.config['MYSQL_PASSWORD'] = 'rvJ9lIwGD0suD3TdPTC4'
app.config['MYSQL_DB'] = 'bfpkhtu6hrcqo4x8mwkj'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql.init_app(app) #inicializa la conexion a la DB

@app.route('/accesologin', methods=['GET', 'POST'])
def accesologin():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuario WHERE email = %s', (email, ))
        user = cursor.fetchone()
        cursor.close()

        if user and pbkdf2_sha256.verify(password, user['password']):
            session['usuario'] = user['email']
            session['rol'] = user['id_rol']
            
            # Redirige según el rol del usuario
            if user['id_rol'] == 1:
                return redirect(url_for('admin'))  # Redirige a la página de administrador
            else:
                return redirect(url_for('panel_usuario')) # Redirige al panel de usuario normal
        else:
            flash ('Usuario y contraseña son incorrectos', 'danger')
        return render_template("login.html")

@app.route('/panel_usuario')
def panel_usuario():
    if 'usuario' in session:
        # Asegúrate de que el usuario no sea un administrador (id_rol = 1)
        if session.get('rol') != 1:
            return render_template("panel_usuario.html", usuario=session['usuario'])
        else:
            flash('Acceso denegado. Eres un administrador.', 'warning')
            return redirect(url_for('admin')) # Si es admin, redirige al panel de admin
    else:
        flash('Debes iniciar sesión para acceder a esta página.', 'info')
        return redirect(url_for('login'))

          
 
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
        password = pbkdf2_sha256.hash (request.form.get('password'))
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

@app.route('/acercaDe')
def acercaDe():
    return render_template("acercaDe.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect (url_for('inicio'))

@app.route('/tareas_agregadas', methods=['GET', 'POST'])
def tareas_agregadas():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha_creacion = request.form['fecha_creacion']
        fecha_vencimiento = request.form['fecha_vencimiento']
        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO tareas (titulo, descripcion, fecha_creacion, fecha_vencimiento)
                VALUES (%s, %s, %s, %s)
            """, (titulo, descripcion, fecha_creacion, fecha_vencimiento))
            mysql.connection.commit()
            cursor.close()
            flash('Tarea agregada exitosamente.', 'success')
            return redirect(url_for('tareas_agregadas'))
        except Exception as e:
            flash(f'Error al agregar la tarea: {e}', 'danger')
            return redirect(url_for('tareas_agregadas'))

    # Si es GET, obtenemos las tareas y renderizamos la plantilla
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tareas")
    tareas = cursor.fetchall()
    cursor.close()
    return render_template("tareas_agregadas.html", tareas=tareas)

   
@app.route('/listar_tarea')
def listar_tarea():
 cursor = mysql.connection.cursor()
 cursor.execute("SELECT id, titulo, descripcion, fecha_creacion, fecha_vencimiento, estado FROM tareas")
 tareas = cursor.fetchall()
 cursor.close()
 return render_template("listar_tarea.html", tareas=tareas)


@app.route('/editar_tareas', methods=['POST'])
def editar_tarea():
    if request.method == 'POST':
        id = request.form['id']
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha_vencimiento = request.form['fecha_vencimiento']
        
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE tareas
            SET titulo = %s,
                descripcion = %s,
                fecha_vencimiento = %s
            WHERE id = %s
        """, (titulo, descripcion, fecha_vencimiento, id))
        mysql.connection.commit()
        cur.close()
        flash('Tarea actualizada correctamente')
        return redirect(url_for('listar_tarea'))

@app.route('/borrar_tareas/<string:id>')
def borrar_tareas(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tareas WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Tarea eliminada correctamente')
    return redirect(url_for('listar_tarea'))


@app.route('/listar')
def listar():
   cur = mysql.connection.cursor()
   cur.execute("SELECT * FROM usuario")
   usuarios = cur.fetchall()
   cur.close()
   return render_template("perfil.html", usuarios=usuarios)
 
@app.route('/admin')
def admin():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) as total_usuarios FROM usuario")
    total_usuarios = cur.fetchone()['total_usuarios']
    cur.execute("SELECT COUNT(*) as total_tareas FROM tareas")
    total_tareas = cur.fetchone()['total_tareas']
    cur.close()
    return render_template ("admin.html", total_usuarios=total_usuarios, total_tareas=total_tareas)



@app.route('/updateUsuario', methods=['POST'])
def updateUsuario():
    id_usuario = request.form['id']
    nombre = request.form['nombre']
    email = request.form['email']
    password = request.form.get('password')

    cur = mysql.connection.cursor()

    if password:
        password = pbkdf2_sha256.hash(password)
        cur.execute("UPDATE usuario SET nombre = %s, email = %s, password = %s WHERE id_usuario = %s", (nombre, email, password, id_usuario))
    else:
        cur.execute("UPDATE usuario SET nombre = %s, email = %s WHERE id_usuario = %s", (nombre, email, id_usuario))

    mysql.connection.commit()
    cur.close()
    flash('Usuario actualizado correctamente')
    return redirect(url_for('listar'))

@app.route('/borrarUser/<string:id_usuario>', methods=['GET'])
def borrarUser(id_usuario):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuario WHERE id_usuario=%s", (id_usuario,))
    mysql.connection.commit()
    cur.close()
    flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('listar'))

@app.route('/actualizar_estado_tarea/<int:id_tarea>', methods=['POST'])
def actualizar_estado_tarea(id_tarea):
    nuevo_estado = request.json.get('estado')
    if not nuevo_estado:
        return jsonify({'success': False, 'message': 'Estado no proporcionado'}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE tareas SET estado = %s WHERE id = %s", (nuevo_estado, id_tarea))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'message': 'Estado de tarea actualizado correctamente'})
    except Exception as e:
        print(f"Error al actualizar estado de tarea: {e}")
        return jsonify({'success': False, 'message': f'Error al actualizar estado: {e}'}), 500

@app.route('/estadisticas')
def estadisticas():
    cur = mysql.connection.cursor()

    # 1. Estado de las tareas
    cur.execute("SELECT estado, COUNT(*) as total FROM tareas GROUP BY estado")
    estado_tareas = cur.fetchall()

    # 2. Tareas creadas por día
    cur.execute("SELECT DATE(fecha_creacion) as dia, COUNT(*) as total FROM tareas GROUP BY DATE(fecha_creacion)")
    tareas_por_dia = cur.fetchall()

    # 3. Promedio de duración planificada para tareas completadas
    cur.execute("SELECT AVG(DATEDIFF(fecha_vencimiento, fecha_creacion)) as promedio_dias FROM tareas WHERE estado = 'Completada'")
    promedio_finalizacion = cur.fetchone()

    cur.close()

    # Formatear datos para los gráficos
    labels_estado = [item['estado'] for item in estado_tareas]
    datos_estado = [item['total'] for item in estado_tareas]

    labels_tareas_dia = [item['dia'].strftime('%Y-%m-%d') for item in tareas_por_dia]
    datos_tareas_dia = [item['total'] for item in tareas_por_dia]
    
    promedio_dias = promedio_finalizacion['promedio_dias'] if promedio_finalizacion and promedio_finalizacion['promedio_dias'] is not None else 0


    return render_template('estadisticas.html', 
                           labels_estado=labels_estado, 
                           datos_estado=datos_estado,
                           labels_tareas_dia=labels_tareas_dia,
                           datos_tareas_dia=datos_tareas_dia,
                           promedio_dias=promedio_dias)

@app.route('/guardar_usuario', methods=['GET', 'POST'])
def guardar_usuario():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = pbkdf2_sha256.hash (request.form.get('password'))
        id_rol = request.form.get('id_rol', 2)  # Rol usuario por defecto

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, %s)",
                    (nombre, email, password, id_rol))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('listar'))

    return render_template("guardar_usuario.html")


       
# ----------------- MAIN -----------------
if __name__ == '__main__':
    app.run(debug=True, port=8000)