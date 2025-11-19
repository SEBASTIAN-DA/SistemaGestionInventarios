from flask import Blueprint, request, jsonify, current_app
from repositories.table_repository import TableRepository
from services.table_service import TableService

tables_bp = Blueprint('tables', __name__, url_prefix='/tables')

@tables_bp.route('/take', methods=['POST'])
def take_table():
    data = request.json or {}
    table_id = data.get('table_id')
    waiter_id = data.get('waiter_id')

    if not table_id:
        return jsonify({"success": False, "message": "table_id is required"}), 400

    repo = TableRepository(current_app.mysql)
    service = TableService(repo)

    try:
        res = service.take_table(table_id, waiter_id)
        return jsonify({"success": True, "data": res}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

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

