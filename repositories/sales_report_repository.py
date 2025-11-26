class SalesReportRepository:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_sales_report(self, start_date, end_date, branch_id=None):
        cursor = self.mysql.connection.cursor(dictionary=True)

        query = """
            SELECT 
                o.created_at AS fecha,
                b.name AS sede,
                p.code AS codigo_producto,
                SUM(od.quantity) AS cantidad_vendida,
                p.cost_price AS costo,
                p.sale_price AS precio_venta,
                SUM((p.sale_price - p.cost_price) * od.quantity) AS ganancia
            FROM order_details od
            JOIN orders o ON od.order_id = o.id
            JOIN products p ON od.product_id = p.id
            JOIN restaurant_tables t ON o.table_id = t.id
            JOIN branches b ON t.branch_id = b.id
            WHERE o.created_at BETWEEN %s AND %s
        """

        params = [start_date, end_date]

        if branch_id:
            query += " AND b.id = %s"
            params.append(branch_id)

        query += """
            GROUP BY 
                o.created_at,
                b.name,
                p.code,
                p.cost_price,
                p.sale_price
            ORDER BY ganancia DESC
        """

        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        cursor.close()

        return results
