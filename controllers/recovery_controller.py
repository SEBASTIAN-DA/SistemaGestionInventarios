from flask import Blueprint, request, jsonify, session
from services.recovery_service import recover_password

recovery_bp = Blueprint('recovery_bp', __name__)

@recovery_bp.route('/admin/recover-password', methods=['POST'])
def recover_password_route():
    # ✅ 1. Verificar sesión activa
    if 'user_id' not in session or 'role' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión."}), 401

    # ✅ 2. Verificar que el usuario sea admin
    if session['role'] != 'admin':
        return jsonify({"success": False, "message": "Acceso denegado. Solo administradores pueden cambiar contraseñas."}), 403

    # ✅ 3. Obtener datos del body
    data = request.get_json()
    if not data or 'national_id' not in data or 'new_password' not in data:
        return jsonify({"success": False, "message": "Datos incompletos. Se requiere cédula y nueva contraseña."}), 400

    national_id = data['national_id']
    new_password = data['new_password']

    # ✅ 4. Ejecutar recuperación
    success, message = recover_password(national_id, new_password)
    status_code = 200 if success else 400
    return jsonify({"success": success, "message": message}), status_code
