from flask import Flask, request, jsonify, session
from dotenv import load_dotenv
import bcrypt
import os
from flask_cors import CORS

# ================== CARGAR VARIABLES DE ENTORNO ==================
load_dotenv()

app = Flask(__name__)

CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:4200"]
)

# ================== CONFIGURACIÓN BASE DE DATOS ==================
from config.db_config import init_mysql
mysql = init_mysql(app)

# 🔹 Adjuntar mysql al app para usar current_app.mysql en los Blueprints
app.mysql = mysql

# ================== CLAVE SECRETA PARA SESIONES ==================
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# ================== BLUEPRINTS ==================
from controllers.recovery_controller import recovery_bp
from controllers.auth_controller import auth_bp
from controllers.user_mgmt_controller import user_bp

app.register_blueprint(recovery_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)

# ================== FUNCIÓN PARA ENCRIPTAR CONTRASEÑAS ==================
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# ================== PROBAR CONEXIÓN MYSQL ==================
with app.app_context():
    try:
        cur = app.mysql.connection.cursor()
        cur.execute("SELECT 1")
        cur.close()
        print("✅ Conexión a MySQL exitosa.")
    except Exception as e:
        print("❌ Error al conectar con MySQL:", e)

# ================== RUTA DE DASHBOARD (API JSON) ==================
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized access"}), 401

    return jsonify({
        "success": True,
        "user_id": session['user_id'],
        "role": session['role']
    }), 200

# ================== RUTA DE LOGOUT (API JSON) ==================
@app.route('/session/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({
        "success": True,
        "message": "Session closed successfully"
    }), 200

# ================== EJECUCIÓN PRINCIPAL ==================
if __name__ == '__main__':
    print("Iniciando aplicación Flask...")
    print("🔍 Rutas registradas en Flask:")
    for rule in app.url_map.iter_rules():
        print(f"{rule} -> métodos: {list(rule.methods)}")

    app.run(debug=True)
