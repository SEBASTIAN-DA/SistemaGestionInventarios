from config.db_config import mysql

def fetch_all_branches():
    try:
        conn = mysql.connection
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, name, address, phone, created_at FROM branches")
        result = cursor.fetchall()

        cursor.close()
        return result

    except Exception as e:
        print("❌ ERROR EN BRANCH_REPOSITORY 🚨")
        print(str(e))
        return None
