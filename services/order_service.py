from repositories.order_repository import OrderRepository
from repositories.table_repository import TableRepository

class OrderService:
    def __init__(self, order_repo, table_repo):
        self.order_repo = order_repo
        self.table_repo = table_repo

    def take_order(self, table_id, waiter_id):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)

        # Verificar que la mesa esté disponible
        cursor.execute(
            "SELECT * FROM restaurant_tables WHERE id=%s AND status='available'", 
            (table_id,)
        )
        table = cursor.fetchone()
        if not table:
            raise ValueError("Table not available or does not exist")

        # Crear la orden
        cursor.execute(
            "INSERT INTO orders (table_id, waiter_id, total, status, created_at) "
            "VALUES (%s, %s, %s, 'open', NOW())",
            (table_id, waiter_id, 0)
        )
        order_id = cursor.lastrowid

        # Marcar la mesa como ocupada
        cursor.execute(
            "UPDATE restaurant_tables SET status='occupied' WHERE id=%s", 
            (table_id,)
        )

        self.order_repo.mysql.connection.commit()
        cursor.close()

        return {"order_id": order_id, "table_id": table_id, "waiter_id": waiter_id, "status": "open"}

    def add_product_to_order(self, order_id, product_id, quantity):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)

        # Verificar que la orden exista y esté abierta
        cursor.execute("SELECT * FROM orders WHERE id=%s AND status='open'", (order_id,))
        order = cursor.fetchone()
        if not order:
            raise ValueError("Order not found or closed")

        # Verificar inventario y obtener sale_price
        cursor.execute(
            "SELECT id, name, stock_quantity, sale_price FROM products WHERE id=%s", 
            (product_id,)
        )
        product = cursor.fetchone()
        if not product:
            raise ValueError("Product not found")
        if product['stock_quantity'] < quantity:
            raise ValueError("Not enough stock for this product")

        # Insertar detalle de orden
        cursor.execute(
            "INSERT INTO order_details (order_id, product_id, quantity, unit_price) "
            "VALUES (%s, %s, %s, %s)",
            (order_id, product_id, quantity, product['sale_price'])
        )

        # Actualizar total de la orden
        total_increase = product['sale_price'] * quantity
        cursor.execute(
            "UPDATE orders SET total = total + %s WHERE id=%s", 
            (total_increase, order_id)
        )

        # Reducir stock
        cursor.execute(
            "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id=%s", 
            (quantity, product_id)
        )

        self.order_repo.mysql.connection.commit()
        cursor.close()

        return {"order_id": order_id, "product_id": product_id, "quantity": quantity, "added_price": total_increase}

    def update_product_quantity(self, detail_id, quantity):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)

        # Verificar detalle de orden
        cursor.execute("SELECT * FROM order_details WHERE id=%s", (detail_id,))
        detail = cursor.fetchone()
        if not detail:
            raise ValueError("Order detail not found")

        # Verificar stock
        cursor.execute(
            "SELECT stock_quantity, sale_price FROM products WHERE id=%s", 
            (detail['product_id'],)
        )
        product = cursor.fetchone()
        if product['stock_quantity'] < (quantity - detail['quantity']):
            raise ValueError("Not enough stock for this update")

        # Calcular diferencia de cantidad y precio
        stock_diff = quantity - detail['quantity']
        price_diff = product['sale_price'] * stock_diff

        # Actualizar detalle y stock
        cursor.execute(
            "UPDATE order_details SET quantity=%s WHERE id=%s", 
            (quantity, detail_id)
        )
        cursor.execute(
            "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id=%s", 
            (stock_diff, detail['product_id'])
        )

        # Actualizar total de la orden
        cursor.execute(
            "UPDATE orders SET total = total + %s WHERE id=%s", 
            (price_diff, detail['order_id'])
        )

        self.order_repo.mysql.connection.commit()
        cursor.close()

        return {"detail_id": detail_id, "new_quantity": quantity, "price_change": price_diff}

    def get_order_details(self, order_id):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)

        # Obtener la orden
        cursor.execute("SELECT * FROM orders WHERE id=%s", (order_id,))
        order = cursor.fetchone()
        if not order:
            raise ValueError("Order not found")

        # Obtener detalles de productos
        cursor.execute("""
            SELECT od.id AS detail_id, p.id AS product_id, p.name, od.quantity, od.unit_price
            FROM order_details od
            JOIN products p ON od.product_id = p.id
            WHERE od.order_id=%s
        """, (order_id,))
        items = cursor.fetchall()
        cursor.close()

        return {"order": order, "items": items}

    def pay_order(self, order_id, cashier_id, payment_method='cash'):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)

        # Verificar que la orden esté abierta
        cursor.execute("SELECT * FROM orders WHERE id=%s AND status='open'", (order_id,))
        order = cursor.fetchone()
        if not order:
            raise ValueError("Order not found or already closed")

        # Insertar pago
        cursor.execute(
            "INSERT INTO payments (order_id, cashier_id, payment_method, amount, payment_date) "
            "VALUES (%s, %s, %s, %s, NOW())",
            (order_id, cashier_id, payment_method, order['total'])
        )

        # Cerrar orden y liberar mesa
        cursor.execute("UPDATE orders SET status='closed' WHERE id=%s", (order_id,))
        cursor.execute("UPDATE restaurant_tables SET status='available' WHERE id=%s", (order['table_id'],))

        self.order_repo.mysql.connection.commit()
        cursor.close()

        return {"order_id": order_id, "total": order['total'], "status": "closed"}
