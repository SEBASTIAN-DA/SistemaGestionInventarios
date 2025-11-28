from repositories.inventory_repository import (
    get_all_products,
    get_product_by_code,
    insert_product,
    update_product,
    delete_product
)

def list_products(branch_id=None):
    return get_all_products(branch_id)

def create_product(data):
    required_fields = ["code", "name", "category", "cost_price", "sale_price", "branch_id"]
    if not all(field in data for field in required_fields):
        return False, "Faltan campos obligatorios."

    # Validar si el producto ya existe
    existing = get_product_by_code(data["code"])
    if existing:
        return False, "Ya existe un producto con ese código."

    insert_product(
        data["code"],
        data["name"],
        data["category"],
        data["cost_price"],
        data["sale_price"],
        data.get("stock_quantity", 0),
        data.get("min_stock_level", 5),
        data["branch_id"]
    )
    return True, "Producto agregado correctamente."

def update_product_info(product_id, data):
    updated = update_product(product_id, data)
    if not updated:
        return False, "No se pudo actualizar el producto."
    return True, "Producto actualizado correctamente."

def remove_product(product_id):
    deleted = delete_product(product_id)
    if not deleted:
        return False, "No se pudo eliminar el producto."
    return True, "Producto eliminado correctamente."