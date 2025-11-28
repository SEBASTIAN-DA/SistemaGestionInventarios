class SalesReportRepository:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_sales_report(self, start_date, end_date, branch_id=None):
        cursor = self.mysql.connection.cursor(dictionary=True)

        # ✅ CORREGIDO: Query mejorada con JOINs correctos y cálculo de valor_venta
        query = """
            SELECT 
                DATE(o.created_at) AS fecha,
                b.name AS sede,
                p.code AS codigo_producto,
                p.name AS nombre_producto,
                SUM(od.quantity) AS cantidad_vendida,
                AVG(p.cost_price) AS costo,
                AVG(p.sale_price) AS precio_venta,
                SUM(od.quantity * p.sale_price) AS valor_venta,
                SUM((p.sale_price - p.cost_price) * od.quantity) AS ganancia
            FROM order_details od
            JOIN orders o ON od.order_id = o.id
            JOIN products p ON od.product_id = p.id
            JOIN restaurant_tables rt ON o.table_id = rt.id
            JOIN branches b ON rt.branch_id = b.id
            WHERE o.status = 'closed'  -- ✅ Solo pedidos cerrados/pagados
            AND DATE(o.created_at) BETWEEN %s AND %s
        """

        params = [start_date, end_date]

        if branch_id:
            query += " AND b.id = %s"
            params.append(branch_id)

        query += """
            GROUP BY 
                DATE(o.created_at),
                b.name,
                p.code,
                p.name
            ORDER BY ganancia DESC
        """

        print(f"🔍 Ejecutando query: {query}")
        print(f"🔍 Parámetros: {params}")

        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        cursor.close()

        print(f"📊 Resultados obtenidos: {len(results)} registros")
        return results