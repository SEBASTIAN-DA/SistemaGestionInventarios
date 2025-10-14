from flask import Blueprint, request, jsonify, session
from services.user_mgmt_service import (
    update_user as service_update_user,
    delete_user as service_delete_user,
    get_all_users as service_get_all_users  # <- nuevo import
)

print("User controller cargado correctamente")

user_bp = Blueprint('user_bp', __name__, url_prefix='/user')


# ========== GET ALL USERS ==========
@user_bp.route('s', methods=['GET'])  # /user + s → /users
def get_all_users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({"success": False, "message": "Acceso denegado. Solo administradores pueden ver los usuarios."}), 403

    users = service_get_all_users()
    if users is None:
        return jsonify({"success": False, "message": "Error al obtener los usuarios."}), 500

    return jsonify(users), 200


# ========== UPDATE USER ==========
@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({"success": False, "message": "Acceso denegado. Solo administradores pueden editar usuarios."}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    success, message = service_update_user(user_id, data)
    status_code = 200 if success else 400
    return jsonify({"success": success, "message": message}), status_code


# ========== DELETE USER ==========
@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({"success": False, "message": "Acceso denegado. Solo administradores pueden eliminar usuarios."}), 403

    success, message = service_delete_user(user_id)
    status_code = 200 if success else 400
    return jsonify({"success": success, "message": message}), status_code
