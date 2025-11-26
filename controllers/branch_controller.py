from flask import Blueprint, jsonify, session
from services.branch_service import get_all_branches

print("Branch controller cargado correctamente")

branch_bp = Blueprint('branch_bp', __name__, url_prefix='/branches')

# ========== GET ALL BRANCHES ==========
@branch_bp.route('', methods=['GET'])
def list_branches():
    if 'user_id' not in session:
        return jsonify({
            "success": False,
            "message": "No autorizado. Inicie sesión."
        }), 401

    branches = get_all_branches()

    if branches is None:
        return jsonify({
            "success": False,
            "message": "Error al obtener sedes."
        }), 500

    return jsonify(branches), 200
