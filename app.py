from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask import make_response, send_file
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Inicializamos la aplicación Flask
app = Flask(__name__, template_folder='Templates')

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

    # Si es GET, simplemente renderiza la plantilla
    return render_template("tareas_agregadas.html")

   
@app.route('/listar_tarea')
def listar_tarea():
 cursor = mysql.connection.cursor()
 cursor.execute("SELECT * FROM tareas")
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
    return render_template ("admin.html")

@app.route('/updateUsuario', methods=['POST'])
def updateUsuario():
    id = request.form['id']
    nombre = request.form['nombre']
    email = request.form['email']
    password = request.form['password']
    sql="UPDATE usuario SET nombre=%s, email=%s, password=%s WHERE id=%s"
    datos=(nombre, email, password, id)
    
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    flash('Usuario actualizado correctamente')
    return redirect(url_for('listar'))

@app.route('/borrarUser/<string:id>', methods=['GET'])
def borrarUser(id):
    flash('Usuario eliminado correctamente', 'quetion')
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuario WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('listar'))

@app.route('/guardar_usuario', methods=['GET', 'POST'])
def guardar_usuario():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        id_rol = request.form.get('id_rol', 2)  # Rol usuario por defecto

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, %s)",
                    (nombre, email, password, id_rol))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('listar'))

    return render_template("guardar_usuario.html")

@app.route('/exportar_excel')
def exportar_excel():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tareas")
    tareas = cursor.fetchall()
    cursor.close()

    # Crear DataFrame
    df = pd.DataFrame(tareas)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='tareas')

    output.seek(0)
    return send_file(output,
                     as_attachment=True,
                     download_name="tareas.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ✅ Exportar tareas a PDF
@app.route('/exportar_pdf')
def exportar_pdf():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tareas")
    tareas = cursor.fetchall()
    cursor.close()

    # Crear PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, 750, "Listado de tareas")

    y = 710
    p.setFont("Helvetica", 10)
    for tarea in tareas:
        linea = f"ID: {tarea['id']} | {tarea['titulo']} | decripcion: ${tarea['descripcion']} | fecha_creacion: {tarea['fecha_creacion']} | fecha_vencimiento: {tarea['fecha_vencimiento']}"
        p.drawString(50, y, linea)
        y -= 20
        if y < 50:
            p.showPage()
            y = 750

    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="tareas.pdf", mimetype="application/pdf")

       
# ----------------- MAIN -----------------
if __name__ == '__main__':
    app.run(debug=True, port=8000)

