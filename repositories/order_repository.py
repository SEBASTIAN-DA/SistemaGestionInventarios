class OrderRepository:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_order_by_id(self, order_id):
        cursor = self.mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders WHERE id=%s", (order_id,))
        order = cursor.fetchone()
        cursor.close()
        return order

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
