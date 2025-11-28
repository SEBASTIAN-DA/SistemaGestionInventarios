from flask import current_app

def get_all_products(branch_id=None):
    cur = current_app.mysql.connection.cursor()
    
    if branch_id:
        # ✅ Filtrar por branch_id si se proporciona
        cur.execute("""
            SELECT 
                p.id,
                p.code,
                p.name,
                p.category,
                p.cost_price,
                p.sale_price,
                p.stock_quantity,
                p.min_stock_level,
                p.branch_id,
                b.name AS branch_name,
                p.is_active,
                p.created_at
            FROM products p
            LEFT JOIN branches b ON p.branch_id = b.id
            WHERE p.branch_id = %s AND p.is_active = TRUE
            ORDER BY p.category, p.name ASC
        """, (branch_id,))
    else:
        # ✅ Mostrar todos si no hay branch_id (para admin)
        cur.execute("""
            SELECT 
                p.id,
                p.code,
                p.name,
                p.category,
                p.cost_price,
                p.sale_price,
                p.stock_quantity,
                p.min_stock_level,
                p.branch_id,
                b.name AS branch_name,
                p.is_active,
                p.created_at
            FROM products p
            LEFT JOIN branches b ON p.branch_id = b.id
            WHERE p.is_active = TRUE
            ORDER BY p.category, p.name ASC
        """)
    
    rows = cur.fetchall()
    cur.close()
    return rows

# El resto de las funciones se mantienen igual
def get_product_by_code(code):
    cur = current_app.mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE code = %s", (code,))
    product = cur.fetchone()
    cur.close()
    return product

def insert_product(code, name, category, cost_price, sale_price, stock_quantity, min_stock_level, branch_id):
    cur = current_app.mysql.connection.cursor()
    cur.execute("""
        INSERT INTO products (code, name, category, cost_price, sale_price, stock_quantity, min_stock_level, branch_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (code, name, category, cost_price, sale_price, stock_quantity, min_stock_level, branch_id))
    current_app.mysql.connection.commit()
    cur.close()

def update_product(product_id, data):
    cur = current_app.mysql.connection.cursor()

    fields = []
    values = []

    for key, value in data.items():
        if key.isidentifier():
            fields.append(f"{key} = %s")
            values.append(value)

    if not fields:
        cur.close()
        return False

    values.append(product_id)
    query = f"UPDATE products SET {', '.join(fields)} WHERE id = %s"
    cur.execute(query, tuple(values))
    current_app.mysql.connection.commit()
    affected = cur.rowcount

    cur.close()
    return affected > 0

def delete_product(product_id):
    cur = current_app.mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
    current_app.mysql.connection.commit()
    affected = cur.rowcount
    cur.close()
    return affected > 0