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

    if not table_id or not waiter_id:
        return jsonify({
            "success": False,
            "message": "table_id and waiter_id are required"
        }), 400

    table_repo = TableRepository(current_app.mysql)
    order_repo = OrderRepository(current_app.mysql)

    table_service = TableService(table_repo)
    order_service = OrderService(order_repo, table_repo)

    try:
        current_status = table_service.get_table_status(table_id)

        # ✅ Si ya está ocupada, devuelvo pedido activo
        if current_status == "OCCUPIED":
            order = order_service.get_active_order_by_table(table_id)
            return jsonify({
                "success": True,
                "message": "Mesa ya ocupada. Pedido activo retornado.",
                "data": order
            }), 200

        # ✅ Tomar mesa
        table_service.take_table(table_id, waiter_id)

        # ✅ Crear pedido automático
        order = order_service.take_order(table_id, waiter_id)

        return jsonify({
            "success": True,
            "message": "Mesa ocupada y pedido creado correctamente",
            "data": order
        }), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


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

    tables = service.get_all_tables()
    return jsonify({"success": True, "data": tables}), 200
