from repositories.user_repository import update_user_db, delete_user_db

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
