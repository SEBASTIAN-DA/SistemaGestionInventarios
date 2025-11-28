from flask import Blueprint, request, jsonify, current_app
from repositories.table_repository import TableRepository
from repositories.order_repository import OrderRepository
from services.table_service import TableService
from services.order_service import OrderService

tables_bp = Blueprint('tables', __name__, url_prefix='/tables')

@tables_bp.route('/take', methods=['POST'])
def take_table():
    data = request.json or {}
    table_id = data.get('table_id')
    waiter_id = data.get('waiter_id')

    print(f"📋 Recibiendo solicitud para tomar mesa - table_id: {table_id}, waiter_id: {waiter_id}")

    if not table_id or not waiter_id:
        print("❌ Faltan parámetros requeridos")
        return jsonify({
            "success": False,
            "message": "table_id and waiter_id are required"
        }), 400

    table_repo = TableRepository(current_app.mysql)
    order_repo = OrderRepository(current_app.mysql)

    order_service = OrderService(order_repo, table_repo)

    try:
        print(f"🟡 Intentando crear pedido para mesa {table_id} con mesero {waiter_id}")
        
        # ✅ SOLO llamar a order_service.take_order - esto maneja todo
        order = order_service.take_order(table_id, waiter_id)
        
        print(f"✅ Pedido creado exitosamente: {order}")

        return jsonify({
            "success": True,
            "message": "Mesa ocupada y pedido creado correctamente",
            "data": order
        }), 200

    except ValueError as e:
        print(f"❌ Error de valor: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        print(f"❌ ERROR INTERNO DEL SERVIDOR: {str(e)}")
        import traceback
        print("📝 Stack trace completo:")
        traceback.print_exc()
        return jsonify({"success": False, "message": "Internal server error"}), 500

# ✅ NUEVO ENDPOINT: algoritmo voraz para asignar mesa automáticamente
@tables_bp.route('/assign', methods=['POST'])
def assign_table():
    data = request.json or {}
    people = data.get('people')
    branch_id = data.get('branch_id')

    if not people:
        return jsonify({
            "success": False,
            "message": "people is required"
        }), 400

    table_repo = TableRepository(current_app.mysql)
    table_service = TableService(table_repo)

    try:
        result = table_service.assign_table_greedy(
            int(people),
            branch_id
        )

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

@tables_bp.route('/release', methods=['POST'])
def release_table():
    data = request.json or {}
    table_id = data.get('table_id')

    if not table_id:
        return jsonify({"success": False, "message": "table_id is required"}), 400

    repo = TableRepository(current_app.mysql)
    service = TableService(repo)

    try:
        res = service.release_table(table_id)
        return jsonify({"success": True, "data": res}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

@tables_bp.route('/', methods=['GET'])
def list_tables():
    repo = TableRepository(current_app.mysql)
    service = TableService(repo)
    
    # ✅ Obtener branch_id del query parameter
    branch_id = request.args.get('branch_id', type=int)
    
    tables = service.get_all_tables(branch_id)
    return jsonify({"success": True, "data": tables}), 200