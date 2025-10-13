
from flask import Blueprint, request, jsonify
from services.recovery_service import recover_password

recovery_bp = Blueprint('recovery_bp', __name__)

@recovery_bp.route('/admin/recover-password', methods=['POST'])
def recover_password_route():
    data = request.get_json()

    if not data or 'national_id' not in data or 'new_password' not in data:
        return jsonify({"success": False, "message": "Datos incompletos. Se requiere cédula y nueva contraseña."}), 400

    national_id = data['national_id']
    new_password = data['new_password']

    success, message = recover_password(national_id, new_password)

    status_code = 200 if success else 400
    return jsonify({"success": success, "message": message}), status_code
