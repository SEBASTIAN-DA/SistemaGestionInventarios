from flask import Blueprint, request, jsonify, current_app

payment_bp = Blueprint('payments', __name__, url_prefix='/payments')

@payment_bp.route('/', methods=['POST'])
def create_payment():
    data = request.json or {}
    
    order_id = data.get('order_id')
    cashier_id = data.get('cashier_id')
    amount = data.get('amount')
    payment_method = data.get('payment_method', 'cash')
    
    if not all([order_id, cashier_id, amount]):
        return jsonify({
            "success": False,
            "message": "order_id, cashier_id, and amount are required"
        }), 400
    
    cursor = current_app.mysql.connection.cursor(dictionary=True)
    
    try:
        # Verificar que la orden existe
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            return jsonify({
                "success": False,
                "message": "Order not found"
            }), 404
        
        # Insertar el pago
        cursor.execute("""
            INSERT INTO payments (order_id, cashier_id, payment_method, amount, payment_date)
            VALUES (%s, %s, %s, %s, NOW())
        """, (order_id, cashier_id, payment_method, amount))
        
        current_app.mysql.connection.commit()
        
        payment_id = cursor.lastrowid
        
        return jsonify({
            "success": True,
            "data": {
                "payment_id": payment_id,
                "order_id": order_id,
                "amount": amount,
                "payment_method": payment_method
            }
        }), 201
        
    except Exception as e:
        current_app.mysql.connection.rollback()
        return jsonify({
            "success": False,
            "message": f"Error creating payment: {str(e)}"
        }), 500
    finally:
        cursor.close()

@payment_bp.route('/order/<int:order_id>', methods=['GET'])
def get_payments_by_order(order_id):
    cursor = current_app.mysql.connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT p.*, u.username as cashier_name
            FROM payments p
            LEFT JOIN users u ON p.cashier_id = u.id
            WHERE p.order_id = %s
            ORDER BY p.payment_date DESC
        """, (order_id,))
        payments = cursor.fetchall()
        
        return jsonify({
            "success": True,
            "data": payments
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error retrieving payments: {str(e)}"
        }), 500
    finally:
        cursor.close()

@payment_bp.route('/', methods=['GET'])
def get_all_payments():
    cursor = current_app.mysql.connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT p.*, u.username as cashier_name, o.table_id
            FROM payments p
            LEFT JOIN users u ON p.cashier_id = u.id
            LEFT JOIN orders o ON p.order_id = o.id
            ORDER BY p.payment_date DESC
        """)
        payments = cursor.fetchall()
        
        return jsonify({
            "success": True,
            "data": payments
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error retrieving payments: {str(e)}"
        }), 500
    finally:
        cursor.close()