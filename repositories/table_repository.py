class TableRepository:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_table_by_id(self, table_id):
        cursor = self.mysql.connection.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM restaurant_tables WHERE id = %s", (table_id,))
        table = cursor.fetchone()
        cursor.close()
        return table

    def update_table_status(self, table_id, status):
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "UPDATE restaurant_tables SET status = %s WHERE id = %s",
            (status, table_id)
        )
        self.mysql.connection.commit()
        cursor.close()

    def list_tables(self, branch_id=None):
        cursor = self.mysql.connection.cursor(dictionary=True, buffered=True)
        if branch_id:
            cursor.execute(
                "SELECT * FROM restaurant_tables WHERE branch_id=%s ORDER BY table_number",
                (branch_id,)
            )
        else:
            cursor.execute("SELECT * FROM restaurant_tables ORDER BY table_number")

        rows = cursor.fetchall()
        cursor.close()
        return rows

    # ✅ NUEVO - Para algoritmo voraz
    def get_available_tables(self, branch_id=None):
        cursor = self.mysql.connection.cursor(dictionary=True, buffered=True)

        if branch_id:
            cursor.execute("""
                SELECT id, table_number, capacity, status
                FROM restaurant_tables
                WHERE status='available' AND branch_id=%s
                ORDER BY capacity
            """, (branch_id,))
        else:
            cursor.execute("""
                SELECT id, table_number, capacity, status
                FROM restaurant_tables
                WHERE status='available'
                ORDER BY capacity
            """)

        tables = cursor.fetchall()
        cursor.close()
        return tables
