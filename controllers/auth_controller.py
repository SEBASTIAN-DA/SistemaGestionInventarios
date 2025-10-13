from flask import Blueprint, request, jsonify, session
from services.auth_service import validate_credentials, register_user

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    print("DEBUG - JSON recibido:", data)

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"success": False, "message": "Incomplete data"}), 400

    username = data['username']
    password = data['password']

    is_valid, user, message = validate_credentials(username, password)
    print("DEBUG - Resultado de validación:", is_valid, user, message)

    if is_valid and isinstance(user, dict):
        user_id = user.get('id')
        role_id = user.get('role_id')

        if user_id:
            role_map = {1: "admin", 2: "user", 3: "guest"}
            role = role_map.get(role_id, "unassigned") if role_id is not None else "unassigned"

            session.permanent = True
            session['user_id'] = user_id
            session['role'] = role

            return jsonify({
                "success": True,
                "message": message,
                "role": role
            }), 200

        print("ERROR - Usuario válido pero incompleto:", user)
        return jsonify({"success": False, "message": "User data incomplete"}), 500

    return jsonify({"success": False, "message": message}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({
        "success": True,
        "message": "Session closed successfully"
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    from flask import session  # asegúrate de tenerlo importado arriba

    # ✅ Solo admin puede registrar
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({
            "success": False,
            "message": "Acceso denegado. Solo administradores pueden registrar usuarios."
        }), 403

    data = request.get_json(silent=True)
    print("DEBUG - Datos recibidos para registro:", data)

    required_fields = ['username', 'password', 'national_id', 'full_name']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"success": False, "message": "All required fields must be provided"}), 400

    success, message = register_user(data)

    if success:
        return jsonify({"success": True, "message": message}), 201
    elif "exists" in message.lower():
        return jsonify({"success": False, "message": message}), 409
    elif "password" in message.lower():
        return jsonify({"success": False, "message": message}), 422
    else:
        return jsonify({"success": False, "message": message}), 400
