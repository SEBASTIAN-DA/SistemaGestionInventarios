from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import bcrypt
import os
from dotenv import load_dotenv

# ================== CARGAR VARIABLES DE ENTORNO ==================
load_dotenv()

app = Flask(__name__)

# ================== CONFIGURACIÓN BASE DE DATOS ==================
app.config['MYSQL_HOST'] = os.getenv("DB_HOST", "localhost")
app.config['MYSQL_USER'] = os.getenv("DB_USER", "root")
app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASSWORD", "")
app.config['MYSQL_DB'] = os.getenv("DB_NAME", "inventory_system")
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# ================== CLAVE SECRETA PARA SESIONES ==================
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# ================== FUNCIÓN PARA ENCRIPTAR CONTRASEÑAS ==================
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# ================== PROBAR CONEXIÓN MYSQL ==================
with app.app_context():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        cur.close()
        print("✅ Conexión a MySQL exitosa.")
    except Exception as e:
        print("❌ Error al conectar con MySQL:", e)

# ================== RUTA DE INICIO ==================
@app.route('/')
def home():
    return render_template('login.html')

# ================== RUTA DE LOGIN ==================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user:
            stored_password = user['password'].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                session['user_id'] = user['user_id']
                session['role'] = user['role']
                flash("Inicio de sesión exitoso ✅", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Contraseña incorrecta ❌", "danger")
        else:
            flash("Usuario no encontrado ⚠️", "warning")

    return render_template('login.html')

# ================== RUTA DE DASHBOARD ==================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Por favor, inicia sesión primero.", "warning")
        return redirect(url_for('home'))
    return f"""
        <h2>Bienvenido, usuario ID: {session['user_id']} | Rol: {session['role']}</h2>
        <a href='/logout'>Cerrar sesión</a>
    """

# ================== RUTA DE LOGOUT ==================
@app.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for('home'))

# ================== EJECUCIÓN PRINCIPAL ==================
if __name__ == '__main__':
    print("🚀 Iniciando aplicación Flask...")
    app.run(debug=True)
