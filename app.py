from flask import Flask, request, jsonify, session
from dotenv import load_dotenv
import os
from flask_cors import CORS
from datetime import timedelta

# ================== CARGAR VARIABLES DE ENTORNO ==================
load_dotenv()

app = Flask(__name__)

# ================== CONFIGURACIÓN DE SESIONES ==================
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,  # False en desarrollo
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_PATH='/'
)

# ================== CONFIGURACIÓN DE CORS ==================
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:4200"],
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# ================== CONFIGURACIÓN BASE DE DATOS ==================
from config.db_config import init_mysql
mysql = init_mysql(app)
app.mysql = mysql

# ================== BLUEPRINTS ==================
from controllers.auth_controller import auth_bp
from controllers.recovery_controller import recovery_bp
from controllers.user_mgmt_controller import user_bp
from controllers.inventory_controller import inventory_bp
from controllers.order_controller import order_bp
from controllers.table_controller import tables_bp

app.register_blueprint(auth_bp)
app.register_blueprint(recovery_bp)
app.register_blueprint(user_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(order_bp)
app.register_blueprint(tables_bp)

# ================== MIDDLEWARE MEJORADO ==================
@app.before_request
def before_request():
    # Permitir OPTIONS (CORS preflight)
    if request.method == 'OPTIONS':
        return '', 204

    # Rutas públicas (exact match)
    public_routes = [
        '/login',
        '/register', 
        '/logout',
        '/session/check',
        '/admin/recover-password'
    ]

    # Si es una ruta pública, permitir sin sesión
    if request.path in public_routes:
        return

    # Verificar sesión para rutas protegidas
    if 'user_id' not in session:
        print(f"🔐 Acceso denegado a {request.path}")
        print(f"📦 Sesión actual: {dict(session)}")
        print(f"🔍 User-Agent: {request.headers.get('User-Agent')}")
        print(f"🔍 Origin: {request.headers.get('Origin')}")
        return jsonify({"success": False, "message": "Unauthorized - Please login"}), 401

    print(f"✅ Acceso permitido a {request.path} para usuario {session['user_id']}")

# ================== RUTAS PRINCIPALES ==================
@app.route('/session/check', methods=['GET'])
def check_session():
    print(f"🔍 Verificando sesión - Sesión: {dict(session)}")
    
    if 'user_id' in session:
        return jsonify({
            "success": True,
            "user": {
                "id": session['user_id'],
                "role": session['role'],
                "username": session.get('username', '')
            }
        }), 200
    else:
        return jsonify({"success": False, "message": "No active session"}), 401

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    return jsonify({
        "success": True,
        "user_id": session['user_id'],
        "role": session['role'],
        "username": session.get('username', '')
    }), 200

# ================== EJECUCIÓN PRINCIPAL ==================
if __name__ == '__main__':
    print("\n🚀 Iniciando servidor Flask...")
    print("🔍 Todas las rutas registradas:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        methods = ','.join(sorted(rule.methods - {'OPTIONS', 'HEAD'}))
        print(f"  {rule.rule} -> {rule.endpoint} [{methods}]")
    
    print(f"\n⚙️  Configuración de cookies:")
    print(f"  - SameSite: {app.config['SESSION_COOKIE_SAMESITE']}")
    print(f"  - Secure: {app.config['SESSION_COOKIE_SECURE']}")
    print(f"  - HttpOnly: {app.config['SESSION_COOKIE_HTTPONLY']}")
    
app.run(debug=True, host='localhost', port=5000) 