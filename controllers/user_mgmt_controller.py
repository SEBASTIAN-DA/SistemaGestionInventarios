from flask import Blueprint, request, jsonify, session
from services.user_mgmt_service import (
    update_user as service_update_user,
    delete_user as service_delete_user,
    get_all_users as service_get_all_users,  # <- nuevo import
    get_user_by_id as service_get_user_by_id 
)

print("User controller cargado correctamente")

user_bp = Blueprint('user_bp', __name__, url_prefix='/user')


# ========== GET ALL USERS ==========
@user_bp.route('/s', methods=['GET'])  # /user/s
def get_all_users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({"success": False, "message": "Acceso denegado. Solo administradores pueden ver los usuarios."}), 403

    users_data = service_get_all_users()

    # Manejar si el servicio devuelve [True, users]
    if isinstance(users_data, (list, tuple)) and len(users_data) == 2 and isinstance(users_data[1], list):
        users = users_data[1]
    else:
        users = users_data

    if users is None:
        return jsonify({"success": False, "message": "Error al obtener los usuarios."}), 500

    return jsonify(users), 200


# ========== GET CURRENT USER PROFILE ==========
@user_bp.route('/profile', methods=['GET'])
def get_current_user_profile():
    # Verificar que el usuario esté autenticado (cualquier rol)
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Acceso denegado. Debe iniciar sesión."}), 401
    
    # Obtener el ID del usuario actual desde la sesión
    current_user_id = session.get('user_id')
    
    # Importar aquí para evitar circular imports
    from services.user_mgmt_service import get_user_by_id
    
    # Obtener los datos completos del usuario
    user_data = get_user_by_id(current_user_id)
    
    if not user_data:
        return jsonify({"success": False, "message": "Usuario no encontrado."}), 404
    
    return jsonify(user_data), 200


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

