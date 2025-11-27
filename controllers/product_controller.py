from flask import Blueprint, request, jsonify, current_app

product_bp = Blueprint('products', __name__, url_prefix='/products')

@product_bp.route('/', methods=['GET'])
def get_products():
    cursor = current_app.mysql.connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                id, 
                code,
                name, 
                category, 
                cost_price, 
                sale_price, 
                stock_quantity, 
                min_stock_level,
                branch_id,
                is_active,
                created_at
            FROM products 
            WHERE stock_quantity > 0 AND is_active = TRUE
            ORDER BY category, name
        """)
        products = cursor.fetchall()
        
        print(f"✅ {len(products)} productos encontrados")
        
        return jsonify({
            "success": True,
            "data": products
        }), 200
        
    except Exception as e:
        print(f"❌ Error al obtener productos: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error retrieving products: {str(e)}"
        }), 500
    finally:
        cursor.close()

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    cursor = current_app.mysql.connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                id, 
                code,
                name, 
                category, 
                cost_price, 
                sale_price, 
                stock_quantity, 
                min_stock_level,
                branch_id,
                is_active,
                created_at
            FROM products 
            WHERE id = %s
        """, (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({
                "success": False,
                "message": "Product not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": product
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error retrieving product: {str(e)}"
        }), 500
    finally:
        cursor.close()

@product_bp.route('/search', methods=['GET'])
def search_products():
    search_term = request.args.get('q', '')
    
    if not search_term:
        return jsonify({
            "success": False,
            "message": "Search term is required"
        }), 400
    
    cursor = current_app.mysql.connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                id, 
                code,
                name, 
                category, 
                cost_price, 
                sale_price, 
                stock_quantity, 
                min_stock_level
            FROM products 
            WHERE (name LIKE %s OR code LIKE %s) 
            AND stock_quantity > 0 AND is_active = TRUE
            ORDER BY name
        """, (f'%{search_term}%', f'%{search_term}%'))
        products = cursor.fetchall()
        
        return jsonify({
            "success": True,
            "data": products
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error searching products: {str(e)}"
        }), 500
    finally:
        cursor.close()