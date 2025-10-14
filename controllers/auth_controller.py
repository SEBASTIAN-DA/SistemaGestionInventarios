from flask import Blueprint, request, jsonify, session, make_response
from services.auth_service import validate_credentials, register_user

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print("DEBUG - JSON recibido:", data)

        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"success": False, "message": "Datos incompletos"}), 400

        username = data['username']
        password = data['password']

        is_valid, user, message = validate_credentials(username, password)
        print("DEBUG - Resultado de validación:", is_valid, user, message)

        if is_valid and user:
            user_id = user.get('id')
            role_id = user.get('role_id')
            username = user.get('username', username)

            if user_id:
                role_map = {1: "admin", 2: "user", 3: "guest"}
                role = role_map.get(role_id, "unassigned")

                # ESTABLECER SESIÓN
                session.permanent = True
                session['user_id'] = user_id
                session['role'] = role
                session['username'] = username

                print(f"✅ Sesión iniciada - UserID: {user_id}, Role: {role}")
                print(f"📦 Cookie de sesión: {dict(session)}")

                # Crear respuesta
                response = make_response(jsonify({
                    "success": True,
                    "message": "Login exitoso",
                    "role": role,
                    "user_id": user_id
                }), 200)

                return response

            return jsonify({"success": False, "message": "Datos de usuario incompletos"}), 500

        return jsonify({"success": False, "message": message}), 401

    except Exception as e:
        print(f"❌ Error en login: {e}")
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    user_id = session.get('user_id')
    session.clear()
    print(f"✅ Sesión cerrada - UserID: {user_id}")
    
    response = make_response(jsonify({
        "success": True,
        "message": "Sesión cerrada exitosamente"
    }), 200)
    
    # Limpiar cookie
    response.set_cookie('session', '', expires=0)
    return response

@auth_bp.route('/register', methods=['POST'])
def register():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({
            "success": False,
            "message": "Acceso denegado. Solo administradores pueden registrar usuarios."
        }), 403

    try:
        data = request.get_json()
        print("DEBUG - Datos recibidos para registro:", data)

        required_fields = ['username', 'password', 'national_id', 'full_name']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"success": False, "message": "Todos los campos son requeridos"}), 400

        success, message = register_user(data)

        if success:
            return jsonify({"success": True, "message": message}), 201
        elif "exists" in message.lower():
            return jsonify({"success": False, "message": message}), 409
        else:
            return jsonify({"success": False, "message": message}), 400

    except Exception as e:
        print(f"❌ Error en registro: {e}")
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500