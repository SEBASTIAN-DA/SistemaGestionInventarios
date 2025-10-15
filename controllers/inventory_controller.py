from flask import Blueprint, request, jsonify, session
from services.inventory_service import (
    list_products,
    create_product,
    update_product_info,
    remove_product
)

inventory_bp = Blueprint('inventory_bp', __name__)

# =========================
# GET - Listar productos
# =========================
@inventory_bp.route('/inventory/products', methods=['GET'])
def get_products():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión."}), 401

    products = list_products()
    return jsonify({"success": True, "data": products}), 200


# =========================
# POST - Agregar producto (solo admin o cajero)
# =========================
@inventory_bp.route('/inventory/products', methods=['POST'])
def add_product():
    if 'user_id' not in session or 'role' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión."}), 401

    if session['role'] not in ['admin', 'cajero']:
        return jsonify({
            "success": False,
            "message": "Acceso denegado. Solo administradores o cajeros pueden agregar productos."
        }), 403

    data = request.get_json()
    success, message = create_product(data)
    status_code = 200 if success else 400
    return jsonify({"success": success, "message": message}), status_code


# =========================
# PUT - Editar producto (solo admin o cajero)
# =========================
@inventory_bp.route('/inventory/products/<int:product_id>', methods=['PUT'])
def edit_product(product_id):
    if 'user_id' not in session or 'role' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión."}), 401

    if session['role'] not in ['admin', 'cajero']:
        return jsonify({
            "success": False,
            "message": "Acceso denegado. Solo administradores o cajeros pueden modificar productos."
        }), 403

    data = request.get_json()
    success, message = update_product_info(product_id, data)
    status_code = 200 if success else 400
    return jsonify({"success": success, "message": message}), status_code


# =========================
# DELETE - Eliminar producto (solo admin o cajero)
# =========================
@inventory_bp.route('/inventory/products/<int:product_id>', methods=['DELETE'])
def delete_product_route(product_id):
    if 'user_id' not in session or 'role' not in session:
        return jsonify({"success": False, "message": "Debes iniciar sesión."}), 401

    if session['role'] not in ['admin', 'cajero']:
        return jsonify({
            "success": False,
            "message": "Acceso denegado. Solo administradores o cajeros pueden eliminar productos."
        }), 403

    success, message = remove_product(product_id)
    status_code = 200 if success else 400
    return jsonify({"success": success, "message": message}), status_code
