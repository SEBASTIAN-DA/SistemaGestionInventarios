from flask import Blueprint, request, jsonify, current_app, session

product_bp = Blueprint('products', __name__, url_prefix='/products')

@product_bp.route('/', methods=['GET'])
def get_products():
    cursor = current_app.mysql.connection.cursor(dictionary=True)
    
    try:
        # ✅ Obtener branch_id y rol de la sesión
        branch_id = session.get('branch_id')
        user_id = session.get('user_id')
        role = session.get('role')
        
        print(f"🏢 PRODUCTOS - Usuario: {user_id}, Rol: {role}, Sede: {branch_id}")
        
        # ✅ Si el usuario es admin (role = 'admin'), mostrar todos los productos
        if role == 'admin':
            print("👑 Admin detectado - mostrando todos los productos de todas las sedes")
            cursor.execute("""
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
                    b.name as branch_name,
                    p.is_active,
                    p.created_at
                FROM products p
                LEFT JOIN branches b ON p.branch_id = b.id
                WHERE p.stock_quantity > 0 AND p.is_active = TRUE
                ORDER BY b.name, p.category, p.name
            """)
        elif branch_id:
            # ✅ Filtrar por sede si el usuario NO es admin pero tiene branch_id
            print(f"🏪 Usuario regular - filtrando por sede: {branch_id}")
            cursor.execute("""
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
                    b.name as branch_name,
                    p.is_active,
                    p.created_at
                FROM products p
                LEFT JOIN branches b ON p.branch_id = b.id
                WHERE p.stock_quantity > 0 
                AND p.is_active = TRUE
                AND p.branch_id = %s
                ORDER BY p.category, p.name
            """, (branch_id,))
        else:
            # ✅ Si no hay branch_id ni es admin, mostrar productos sin sede específica
            cursor.execute("""
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
                    b.name as branch_name,
                    p.is_active,
                    p.created_at
                FROM products p
                LEFT JOIN branches b ON p.branch_id = b.id
                WHERE p.stock_quantity > 0 AND p.is_active = TRUE
                ORDER BY p.category, p.name
            """)
        
        products = cursor.fetchall()
        
        print(f"✅ {len(products)} productos encontrados")
        if role == 'admin':
            # Mostrar estadísticas por sede para admin
            sedes = {}
            for product in products:
                sede = product['branch_name'] or 'Sin sede'
                sedes[sede] = sedes.get(sede, 0) + 1
            print(f"🏢 Distribución por sede: {sedes}")
        
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
        # ✅ También filtrar por sede en la búsqueda individual
        branch_id = session.get('branch_id')
        
        if branch_id:
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
                WHERE id = %s AND branch_id = %s
            """, (product_id, branch_id))
        else:
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
        # ✅ Filtrar búsqueda por sede
        branch_id = session.get('branch_id')
        
        if branch_id:
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
                    branch_id
                FROM products 
                WHERE (name LIKE %s OR code LIKE %s) 
                AND stock_quantity > 0 
                AND is_active = TRUE
                AND branch_id = %s
                ORDER BY name
            """, (f'%{search_term}%', f'%{search_term}%', branch_id))
        else:
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
                    branch_id
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