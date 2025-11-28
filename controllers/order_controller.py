from flask import Blueprint, request, jsonify, current_app
from repositories.order_repository import OrderRepository
from repositories.table_repository import TableRepository
from services.order_service import OrderService

order_bp = Blueprint('orders', __name__, url_prefix='/orders')

def _make_service():
    order_repo = OrderRepository(current_app.mysql)
    table_repo = TableRepository(current_app.mysql)
    return OrderService(order_repo, table_repo)

@order_bp.route('/create', methods=['POST'])
def create_order():
    data = request.json or {}
    table_id = data.get('table_id')
    waiter_id = data.get('waiter_id')

    print(f"📋 Creando pedido - table_id: {table_id}, waiter_id: {waiter_id}")

    if not table_id or not waiter_id:
        return jsonify({"success": False, "message": "table_id and waiter_id are required"}), 400

    service = _make_service()
    try:
        # ✅ Usar take_order que maneja tanto mesas disponibles como ocupadas
        res = service.take_order(table_id, waiter_id)
        return jsonify({"success": True, "data": res}), 200
    except ValueError as e:
        print(f"❌ Error al crear pedido: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 400

@order_bp.route('/add-product', methods=['POST'])
def add_product():
    data = request.json or {}
    order_id = data.get('order_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not order_id or not product_id or quantity is None:
        return jsonify({"success": False, "message": "order_id, product_id and quantity are required"}), 400

    service = _make_service()
    try:
        res = service.add_product_to_order(order_id, product_id, quantity)
        return jsonify({"success": True, "data": res}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

@order_bp.route('/details/<int:order_id>', methods=['GET'])
def order_details(order_id):
    service = _make_service()
    try:
        res = service.get_order_details(order_id)
        return jsonify({"success": True, "data": res}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404

@order_bp.route('/update-product', methods=['PUT'])
def update_product():
    data = request.json or {}
    detail_id = data.get('detail_id')
    quantity = data.get('quantity')

    if not detail_id or quantity is None:
        return jsonify({"success": False, "message": "detail_id and quantity are required"}), 400

    service = _make_service()
    try:
        res = service.update_product_quantity(detail_id, quantity)
        return jsonify({"success": True, "data": res}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

@order_bp.route('/pay', methods=['POST'])
def pay():
    data = request.json or {}
    order_id = data.get('order_id')
    cashier_id = data.get('cashier_id')
    payment_method = data.get('payment_method', 'cash')

    if not order_id or not cashier_id:
        return jsonify({"success": False, "message": "order_id and cashier_id are required"}), 400

    service = _make_service()
    try:
        res = service.pay_order(order_id, cashier_id, payment_method)
        return jsonify({"success": True, "data": res}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@order_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    service = _make_service()
    try:
        res = service.get_order_by_id(order_id)
        return jsonify({"success": True, "data": res}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404

@order_bp.route('/table/<int:table_id>', methods=['GET'])
def get_orders_by_table(table_id):
    service = _make_service()
    try:
        res = service.get_orders_by_table(table_id)
        return jsonify({"success": True, "data": res}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404

# En tu orders_bp.py o donde tengas el endpoint de pedidos activos
@order_bp.route('/active', methods=['GET'])
def get_active_orders():
    try:
        # ✅ Obtener branch_id del query parameter
        branch_id = request.args.get('branch_id', type=int)
        print(f"🏢 Backend recibió branch_id para pedidos activos: {branch_id}")
        
        order_repo = OrderRepository(current_app.mysql)
        orders = order_repo.get_active_orders(branch_id)  # Pasar branch_id al repositorio
        
        return jsonify({
            "success": True,
            "data": orders
        }), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo pedidos activos: {e}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500

@order_bp.route('/', methods=['GET'])
def get_all_orders():
    service = _make_service()
    try:
        res = service.get_all_orders()
        return jsonify({"success": True, "data": res}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

@order_bp.route('/close', methods=['POST'])
def close_order():
    data = request.json or {}
    order_id = data.get('order_id')
    
    if not order_id:
        return jsonify({"success": False, "message": "order_id is required"}), 400

    service = _make_service()
    try:
        res = service.close_order(order_id)
        return jsonify({"success": True, "data": res}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

@order_bp.route('/confirm', methods=['POST'])
def confirm_order():
    data = request.json or {}
    order_id = data.get('order_id')
    
    if not order_id:
        return jsonify({"success": False, "message": "order_id is required"}), 400

    service = _make_service()
    try:
        res = service.confirm_order(order_id)
        return jsonify({"success": True, "data": res}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400