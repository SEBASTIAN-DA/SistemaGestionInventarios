from flask import Blueprint, request, jsonify, current_app, session, send_file
from repositories.sales_report_repository import SalesReportRepository
import pandas as pd
import io

sales_report_bp = Blueprint('sales_report', __name__, url_prefix='/reports')

# ✅ Reporte JSON (el que ya tienes)
@sales_report_bp.route('/sales', methods=['GET'])
def get_sales_report():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        branch_id = request.args.get('branch_id', type=int)  # ✅ Convertir a int

        if not start_date or not end_date:
            return jsonify({
                "success": False,
                "message": "start_date and end_date are required"
            }), 400

        print(f"📊 Generando reporte: {start_date} a {end_date}, branch_id: {branch_id}")
        print(f"👤 Usuario: {session.get('user_id')}, Rol: {session.get('role')}")

        # ✅ CORREGIDO: Manejo correcto de branch_id para admin vs otros roles
        user_role = session.get("role")
        user_branch_id = session.get("branch_id")
        
        # Si NO es admin y tiene branch_id, forzar su sede
        if user_role != "admin" and user_branch_id:
            branch_id = user_branch_id
            print(f"🔒 Usuario no admin, forzando branch_id: {branch_id}")
        # Si es admin y no se especificó branch_id, mostrar todas las sedes (branch_id=None)
        elif user_role == "admin" and branch_id is None:
            print("👑 Admin viendo todas las sedes")
        # Si es admin y se especificó branch_id, usar el especificado
        elif user_role == "admin" and branch_id is not None:
            print(f"👑 Admin filtrando por sede: {branch_id}")

        repo = SalesReportRepository(current_app.mysql)
        data = repo.get_sales_report(start_date, end_date, branch_id)

        return jsonify({
            "success": True,
            "algorithm": "Greedy - Ordenado por mayor ganancia",
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "branch_id": branch_id
            },
            "count": len(data),
            "data": data
        }), 200

    except Exception as e:
        print(f"❌ Error en reporte de ventas: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error generating report: {str(e)}"
        }), 500
# ✅ NUEVO: Exportar a Excel
@sales_report_bp.route('/sales/excel', methods=['GET'])
def export_sales_excel():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        branch_id = request.args.get('branch_id')

        if not start_date or not end_date:
            return jsonify({
                "success": False,
                "message": "start_date and end_date are required"
            }), 400

        # Seguridad por rol
        if session.get("role") != "admin":
            branch_id = session.get("branch_id")

        repo = SalesReportRepository(current_app.mysql)
        data = repo.get_sales_report(start_date, end_date, branch_id)

        if not data:
            return jsonify({
                "success": False,
                "message": "No hay datos para generar el reporte"
            }), 404

        # Convertir a DataFrame
        df = pd.DataFrame(data)

        # Nombres de columnas más legibles
        df.rename(columns={
            "fecha": "Fecha",
            "sede": "Sede",
            "codigo_producto": "Código Producto",
            "cantidad_vendida": "Cantidad Vendida",
            "costo": "Costo",
            "valor_venta": "Valor Venta",
            "ganancia": "Ganancia"
        }, inplace=True)

        # Guardar Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Reporte Ventas")

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name=f"reporte_ventas_{start_date}_a_{end_date}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
