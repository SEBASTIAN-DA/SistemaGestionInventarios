from repositories.order_repository import OrderRepository
from repositories.table_repository import TableRepository

class OrderService:
    def __init__(self, order_repo, table_repo):
        self.order_repo = order_repo
        self.table_repo = table_repo

    # ===================== CREAR O TOMAR PEDIDO =====================
    def take_order(self, table_id, waiter_id):
        """Crear un nuevo pedido y marcar la mesa como ocupada"""
        print(f"🟡 OrderService.take_order - table_id: {table_id}, waiter_id: {waiter_id}")
        
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)

        try:
            print(f"🔍 Verificando mesa {table_id}...")
            cursor.execute("SELECT * FROM restaurant_tables WHERE id=%s", (table_id,))
            table = cursor.fetchone()
            
            if not table:
                print(f"❌ Mesa {table_id} no encontrada")
                raise ValueError("Table not found")

            print(f"📊 Estado de la mesa {table_id}: {table['status']}")

            if table['status'] == 'occupied':
                print(f"🔄 Mesa {table_id} ya está ocupada, buscando pedido activo...")
                cursor.execute(
                    "SELECT * FROM orders WHERE table_id=%s AND status IN ('open','confirmed')",
                    (table_id,)
                )
                order = cursor.fetchone()
                cursor.close()
                
                if order:
                    print(f"✅ Pedido activo encontrado: {order['id']}")
                    return order
                else:
                    print(f"⚠️ Mesa ocupada pero sin pedido activo")
                    raise ValueError("Table occupied but no active order found")

            print(f"🟡 Creando nuevo pedido para mesa {table_id}...")
            cursor.execute(
                "INSERT INTO orders (table_id, waiter_id, total, status, created_at) "
                "VALUES (%s, %s, %s, 'open', NOW())",
                (table_id, waiter_id, 0)
            )
            order_id = cursor.lastrowid
            print(f"✅ Pedido creado con ID: {order_id}")

            print(f"🟡 Marcando mesa {table_id} como ocupada...")
            cursor.execute(
                "UPDATE restaurant_tables SET status='occupied' WHERE id=%s",
                (table_id,)
            )

            self.order_repo.mysql.connection.commit()
            print(f"✅ Transacción completada - Pedido {order_id} creado y mesa ocupada")

            cursor.close()

            return {
                "order_id": order_id,
                "table_id": table_id,
                "waiter_id": waiter_id,
                "status": "open"
            }

        except Exception as e:
            print(f"❌ Error en take_order: {str(e)}")
            # Asegurarse de cerrar el cursor en caso de error
            if cursor:
                cursor.close()
            raise e

    # ===================== AGREGAR PRODUCTO =====================
    def add_product_to_order(self, order_id, product_id, quantity):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM orders WHERE id=%s", (order_id,))
        order = cursor.fetchone()

        if not order:
            raise ValueError("Order not found")

        if order['status'] != 'open':
            raise ValueError("Order cannot be modified. Must create a new order.")

        cursor.execute(
            "SELECT id, stock_quantity, sale_price FROM products WHERE id=%s",
            (product_id,)
        )
        product = cursor.fetchone()

        if not product:
            raise ValueError("Product not found")

        if product['stock_quantity'] < quantity:
            raise ValueError("Not enough stock")

        cursor.execute(
            "INSERT INTO order_details (order_id, product_id, quantity, unit_price) "
            "VALUES (%s, %s, %s, %s)",
            (order_id, product_id, quantity, product['sale_price'])
        )

        total_increase = product['sale_price'] * quantity

        cursor.execute(
            "UPDATE orders SET total = total + %s WHERE id=%s",
            (total_increase, order_id)
        )

        cursor.execute(
            "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id=%s",
            (quantity, product_id)
        )

        self.order_repo.mysql.connection.commit()
        cursor.close()

        return {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "added_price": total_increase
        }

    # ===================== MODIFICAR PRODUCTO =====================
    def update_product_quantity(self, detail_id, quantity):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT od.*, o.status, o.id AS order_id
            FROM order_details od
            JOIN orders o ON od.order_id = o.id
            WHERE od.id = %s
        """, (detail_id,))
        detail = cursor.fetchone()

        if not detail:
            raise ValueError("Order detail not found")

        if detail['status'] != 'open':
            raise ValueError("El pedido no puede modificarse. Debe registrar un nuevo pedido.")

        cursor.execute(
            "SELECT stock_quantity, sale_price FROM products WHERE id=%s",
            (detail['product_id'],)
        )
        product = cursor.fetchone()

        if not product:
            raise ValueError("Product not found")

        diff = quantity - detail['quantity']

        if diff > 0 and product['stock_quantity'] < diff:
            raise ValueError("Not enough stock for this update")

        price_diff = diff * product['sale_price']

        cursor.execute(
            "UPDATE order_details SET quantity=%s WHERE id=%s",
            (quantity, detail_id)
        )

        cursor.execute(
            "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id=%s",
            (diff, detail['product_id'])
        )

        cursor.execute(
            "UPDATE orders SET total = total + %s WHERE id=%s",
            (price_diff, detail['order_id'])
        )

        self.order_repo.mysql.connection.commit()
        cursor.close()

        return {
            "detail_id": detail_id,
            "new_quantity": quantity,
            "price_change": price_diff
        }

    # ===================== CONFIRMAR PEDIDO =====================
    def confirm_order(self, order_id):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM orders WHERE id=%s", (order_id,))
        order = cursor.fetchone()

        if not order:
            raise ValueError("Order not found")

        if order['status'] != 'open':
            raise ValueError("Order cannot be confirmed")

        cursor.execute(
            "UPDATE orders SET status='confirmed' WHERE id=%s",
            (order_id,)
        )

        self.order_repo.mysql.connection.commit()
        cursor.close()

        return {"order_id": order_id, "status": "confirmed"}

    # ===================== PAGAR PEDIDO =====================
    def pay_order(self, order_id, cashier_id, payment_method='cash'):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM orders WHERE id=%s AND status IN ('open','confirmed')",
            (order_id,)
        )
        order = cursor.fetchone()

        if not order:
            raise ValueError("Order not found or already closed")

        cursor.execute(
            "INSERT INTO payments (order_id, cashier_id, payment_method, amount, payment_date) "
            "VALUES (%s, %s, %s, %s, NOW())",
            (order_id, cashier_id, payment_method, order['total'])
        )

        cursor.execute("UPDATE orders SET status='closed' WHERE id=%s", (order_id,))
        cursor.execute(
            "UPDATE restaurant_tables SET status='available' WHERE id=%s",
            (order['table_id'],)
        )

        self.order_repo.mysql.connection.commit()
        cursor.close()

        return {
            "order_id": order_id,
            "total": order['total'],
            "status": "closed"
        }

    # ===================== ALGORITMO MOCHILA (NUEVO) =====================
    def suggest_products_knapsack(self, budget):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, name, sale_price
            FROM products
            WHERE stock_quantity > 0
        """)
        products = cursor.fetchall()
        cursor.close()

        n = len(products)
        W = int(budget)

        # Tabla DP (mochila)
        dp = [[0 for _ in range(W + 1)] for _ in range(n + 1)]

        for i in range(1, n + 1):
            price = int(products[i - 1]['sale_price'])
            for w in range(W + 1):
                if price <= w:
                    dp[i][w] = max(
                        price + dp[i - 1][w - price],
                        dp[i - 1][w]
                    )
                else:
                    dp[i][w] = dp[i - 1][w]

        # Reconstruir solución
        result = []
        w = W

        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                product = products[i - 1]
                result.append(product)
                w -= int(product['sale_price'])

        return {
            "budget": budget,
            "total": dp[n][W],
            "products": result
        }

    # ===================== MÉTODOS ADICIONALES (para los nuevos endpoints) =====================
    
    def get_order_by_id(self, order_id):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)
        
        # Obtener información básica del pedido
        cursor.execute("""
            SELECT o.*, rt.table_number 
            FROM orders o 
            LEFT JOIN restaurant_tables rt ON o.table_id = rt.id 
            WHERE o.id=%s
        """, (order_id,))
        order = cursor.fetchone()
        
        if not order:
            cursor.close()
            raise ValueError("Order not found")
        
        # Obtener los items del pedido
        cursor.execute("""
            SELECT od.*, p.name as product_name 
            FROM order_details od 
            JOIN products p ON od.product_id = p.id 
            WHERE od.order_id=%s
        """, (order_id,))
        items = cursor.fetchall()
        
        cursor.close()
        
        order['items'] = items
        return order

    def get_orders_by_table(self, table_id):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT o.*, rt.table_number 
            FROM orders o 
            LEFT JOIN restaurant_tables rt ON o.table_id = rt.id 
            WHERE o.table_id=%s 
            ORDER BY o.created_at DESC
        """, (table_id,))
        orders = cursor.fetchall()
        
        # Para cada orden, obtener sus items
        for order in orders:
            cursor.execute("""
                SELECT od.*, p.name as product_name 
                FROM order_details od 
                JOIN products p ON od.product_id = p.id 
                WHERE od.order_id=%s
            """, (order['id'],))
            order['items'] = cursor.fetchall()
        
        cursor.close()
        return orders

    def get_active_orders(self):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT o.*, rt.table_number 
            FROM orders o 
            LEFT JOIN restaurant_tables rt ON o.table_id = rt.id 
            WHERE o.status IN ('open','confirmed') 
            ORDER BY o.created_at DESC
        """)
        orders = cursor.fetchall()
        
        for order in orders:
            cursor.execute("""
                SELECT od.*, p.name as product_name 
                FROM order_details od 
                JOIN products p ON od.product_id = p.id 
                WHERE od.order_id=%s
            """, (order['id'],))
            order['items'] = cursor.fetchall()
        
        cursor.close()
        return orders

    def get_all_orders(self):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT o.*, rt.table_number 
            FROM orders o 
            LEFT JOIN restaurant_tables rt ON o.table_id = rt.id 
            ORDER BY o.created_at DESC
        """)
        orders = cursor.fetchall()
        
        for order in orders:
            cursor.execute("""
                SELECT od.*, p.name as product_name 
                FROM order_details od 
                JOIN products p ON od.product_id = p.id 
                WHERE od.order_id=%s
            """, (order['id'],))
            order['items'] = cursor.fetchall()
        
        cursor.close()
        return orders

    def close_order(self, order_id):
        cursor = self.order_repo.mysql.connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM orders WHERE id=%s AND status IN ('open','confirmed')",
            (order_id,)
        )
        order = cursor.fetchone()

        if not order:
            raise ValueError("Order not found or already closed")

        cursor.execute("UPDATE orders SET status='closed' WHERE id=%s", (order_id,))
        cursor.execute(
            "UPDATE restaurant_tables SET status='available' WHERE id=%s",
            (order['table_id'],)
        )

        self.order_repo.mysql.connection.commit()
        cursor.close()

        return {
            "order_id": order_id,
            "status": "closed"
        }