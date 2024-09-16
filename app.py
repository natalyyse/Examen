from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify
import psycopg2
import os

app = Flask(__name__, template_folder='templates')

# Configuración de la base de datos
DB_HOST = 'dpg-crka4s9u0jms73bikjqg-a.oregon-postgres.render.com'
DB_NAME = 'nubes'
DB_USER = 'nubes_user'
DB_PASSWORD = 'CVnZl5Y3QemAATTQPD3gzr2R7tAdHe8m'


def conectar_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
        return conn
    except psycopg2.Error as e:
        print("Error al conectar a la base de datos:", e)


def crear_persona(dni, nombre, apellido, direccion, telefono):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO personas (dni, nombre, apellido, direccion, telefono) VALUES (%s, %s, %s, %s, %s)",
                   (dni, nombre, apellido, direccion, telefono))
    conn.commit()
    conn.close()

def obtener_registros():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM personas order by apellido")
    registros = cursor.fetchall()
    conn.close()
    return registros

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    dni = request.form['dni']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    direccion = request.form['direccion']
    telefono = request.form['telefono']
    crear_persona(dni, nombre, apellido, direccion, telefono)
    mensaje_confirmacion = "Registro Exitoso"
    return redirect(url_for('index', mensaje_confirmacion=mensaje_confirmacion))

@app.route('/administrar')
def administrar():
    registros=obtener_registros()
    return render_template('administrar.html',registros=registros)

from flask import Flask, render_template, redirect, url_for, flash
import psycopg2
from psycopg2 import sql

app = Flask(__name__, template_folder='templates')
app.secret_key = 'una_clave_secreta_muy_segura'  # Necesario para usar flash

# Configuración de la base de datos
DB_HOST = 'dpg-crka4s9u0jms73bikjqg-a.oregon-postgres.render.com'
DB_NAME = 'nubes'
DB_USER = 'nubes_user'
DB_PASSWORD = 'CVnZl5Y3QemAATTQPD3gzr2R7tAdHe8m'

def obtener_registros():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personas ORDER BY apellido")
    registros = cursor.fetchall()
    conn.close()
    return registros

@app.route('/administrar')
def administrar():
    registros = obtener_registros()
    return render_template('administrar.html', registros=registros)

@app.route('/eliminar/<dni>', methods=['POST'])
def eliminar_registro(dni):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
        cursor = conn.cursor()
        
        # Usar parámetros con la consulta SQL para prevenir inyección SQL
        query = sql.SQL("DELETE FROM personas WHERE dni = %s")
        cursor.execute(query, (dni,))
        
        # Verificar si se eliminó algún registro
        if cursor.rowcount == 0:
            flash(f"No se encontró ningún registro con DNI {dni}", "warning")
        else:
            flash(f"Se eliminó exitosamente el registro con DNI {dni}", "success")
        
        conn.commit()
    except psycopg2.Error as e:
        flash(f"Error al eliminar el registro: {str(e)}", "error")
        conn.rollback()  # Revertir cambios en caso de error
    finally:
        if conn:
            conn.close()
    
    return redirect(url_for('administrar'))

if __name__ == '__main__':
    #Esto es nuevo
    port = int(os.environ.get('PORT',5000))    
    app.run(host='0.0.0.0', port=port, debug=True)
