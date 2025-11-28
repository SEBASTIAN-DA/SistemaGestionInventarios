from repositories.user_repository import (
    update_user_db,
    delete_user_db,
    get_all_users_db,
    get_user_by_id_db
)

def get_all_users():
    try:
        users = get_all_users_db()
        return True, users
    except Exception as e:
        print("ERROR - Fetch users failed:", e)
        return False, f"Database error: {str(e)}"


def update_user(user_id, data):
    try:
        updated = update_user_db(user_id, data)
        if updated:
            return True, "User updated successfully"
        return False, "No fields were updated or user not found"
    except Exception as e:
        print("ERROR - Update failed:", e)
        return False, f"Database error: {str(e)}"


def delete_user(user_id):
    try:
        deleted = delete_user_db(user_id)
        if deleted:
            return True, "User deleted successfully"
        return False, "User not found"
    except Exception as e:
        print("ERROR - Delete failed:", e)
        return False, f"Database error: {str(e)}"

def get_user_by_id(user_id):
    """
    Obtiene un usuario por su ID con toda la información completa
    """
    try:
        user = get_user_by_id_db(user_id)
        if user:
            return {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "national_id": user["national_id"],
                "role_id": user["role_id"],
                "role": user["role"],
                "branch_id": user["branch_id"],
                "branch_name": user.get("branch_name"),
                "is_active": bool(user["is_active"]),
                "created_at": user["created_at"].isoformat() if user["created_at"] else None,
                "password_expiration": user["password_expiration"].isoformat() if user["password_expiration"] else None
            }
        else:
            return None
            
    except Exception as e:
        print(f"Error en servicio get_user_by_id: {e}")
        return None