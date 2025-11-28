class OrderRepository:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_order_by_id(self, order_id):
        cursor = self.mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders WHERE id=%s", (order_id,))
        order = cursor.fetchone()
        cursor.close()
        return order

    def get_active_orders(self, branch_id=None):
        cursor = self.mysql.connection.cursor(dictionary=True)
        
        if branch_id:
            # ✅ Filtrar por branch_id si se proporciona
            cursor.execute("""
                SELECT DISTINCT o.*, 
                       rt.table_number,
                       u.full_name as waiter_name
                FROM orders o
                LEFT JOIN restaurant_tables rt ON o.table_id = rt.id
                LEFT JOIN users u ON o.waiter_id = u.id
                WHERE o.status IN ('open', 'confirmed')
                AND rt.branch_id = %s
                ORDER BY o.created_at DESC
            """, (branch_id,))
        else:
            # ✅ Mostrar todos si no hay branch_id
            cursor.execute("""
                SELECT DISTINCT o.*, 
                       rt.table_number,
                       u.full_name as waiter_name
                FROM orders o
                LEFT JOIN restaurant_tables rt ON o.table_id = rt.id
                LEFT JOIN users u ON o.waiter_id = u.id
                WHERE o.status IN ('open', 'confirmed')
                ORDER BY o.created_at DESC
            """)
        
        orders = cursor.fetchall()
        cursor.close()
        
        # Cargar items para cada pedido
        for order in orders:
            order['items'] = self.get_order_items(order['id'])
            order['total'] = self.calculate_order_total(order['id'])
        
        return orders

    def get_order_items(self, order_id):
        cursor = self.mysql.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT od.*, p.name as product_name 
            FROM order_details od 
            LEFT JOIN products p ON od.product_id = p.id 
            WHERE od.order_id=%s
        """, (order_id,))
        items = cursor.fetchall()
        cursor.close()
        return items

    def calculate_order_total(self, order_id):
        cursor = self.mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT SUM(subtotal) as total FROM order_details WHERE order_id=%s", (order_id,))
        total = cursor.fetchone()['total'] or 0
        cursor.close()
        return total

    def get_order_total(self, order_id):
        cursor = self.mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT SUM(subtotal) as total FROM order_details WHERE order_id=%s", (order_id,))
        total = cursor.fetchone()['total'] or 0
        cursor.close()
        return total

    def insert_payment(self, order_id, cashier_id, amount, payment_method):
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO payments (order_id, cashier_id, payment_method, amount, payment_date) VALUES (%s, %s, %s, %s, NOW())",
            (order_id, cashier_id, payment_method, amount)
        )
        self.mysql.connection.commit()
        cursor.close()

    def update_order_status(self, order_id, status, total):
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "UPDATE orders SET status=%s, total=%s WHERE id=%s",
            (status, total, order_id)
        )
        self.mysql.connection.commit()
        cursor.close()