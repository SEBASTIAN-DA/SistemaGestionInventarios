from flask import current_app

def get_user_by_username(username):
    cur = current_app.mysql.connection.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    return user
def get_all_users_db():
    cur = current_app.mysql.connection.cursor(dictionary=True)
    cur.execute("""
        SELECT 
            u.id,
            u.username,
            u.full_name,
            u.national_id,
            u.role_id,
            r.name AS role,
            u.branch_id,
            b.name AS branch_name,
            u.is_active,
            u.created_at
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
        LEFT JOIN branches b ON u.branch_id = b.id
        ORDER BY u.id ASC
    """)
    rows = cur.fetchall()
    cur.close()

    users = []
    for row in rows:
        users.append({
            "id": row["id"],
            "username": row["username"],
            "full_name": row["full_name"],
            "national_id": row["national_id"],
            "role_id": row["role_id"],
            "role": row["role"],
            "branch_id": row["branch_id"],
            "branch_name": row.get("branch_name"),
            "is_active": bool(row["is_active"]),
            "created_at": row["created_at"]
        })

    return users



def get_user_by_national_id(national_id):
    cur = current_app.mysql.connection.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE national_id = %s", (national_id,))
    user = cur.fetchone()
    cur.close()
    return user

def update_user_password(user_id, new_password_hash):
    cur = current_app.mysql.connection.cursor(dictionary=True)
    cur.execute("""
        UPDATE users 
        SET password = %s, password_expiration = DATE_ADD(CURRENT_DATE, INTERVAL 90 DAY)
        WHERE id = %s
    """, (new_password_hash, user_id))
    current_app.mysql.connection.commit()
    cur.close()

def save_password_to_history(user_id, password_hash):
    cur = current_app.mysql.connection.cursor(dictionary=True)
    cur.execute("""
        INSERT INTO password_history (user_id, password_hash)
        VALUES (%s, %s)
    """, (user_id, password_hash))
    current_app.mysql.connection.commit()
    cur.close()

def get_last_password_hashes(user_id, limit=5):
    cur = current_app.mysql.connection.cursor(dictionary=True)
    cur.execute("""
        SELECT password_hash 
        FROM password_history 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s
    """, (user_id, limit))
    rows = cur.fetchall()
    cur.close()
    return [row['password_hash'] for row in rows]

def insert_user(username, password_hash, national_id, full_name, role_id=None, branch_id=None):
    cur = current_app.mysql.connection.cursor(dictionary=True)
    if branch_id is not None and role_id is not None:
        cur.execute("""
            INSERT INTO users (username, password, national_id, full_name, role_id, branch_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, password_hash, national_id, full_name, role_id, branch_id))
    elif role_id is not None:
        cur.execute("""
            INSERT INTO users (username, password, national_id, full_name, role_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, password_hash, national_id, full_name, role_id))
    else:
        cur.execute("""
            INSERT INTO users (username, password, national_id, full_name)
            VALUES (%s, %s, %s, %s)
        """, (username, password_hash, national_id, full_name))
    current_app.mysql.connection.commit()
    cur.close()

def update_user_db(user_id, data):
    """
    Actualiza dinámicamente los campos de un usuario.
    """
    cur = current_app.mysql.connection.cursor(dictionary=True)

    fields = []
    values = []

    for key, value in data.items():
        if key.isidentifier():
            fields.append(f"{key} = %s")
            values.append(value)

    if not fields:
        cur.close()
        return False

    values.append(user_id)
    query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"

    cur.execute(query, tuple(values))
    current_app.mysql.connection.commit()
    affected = cur.rowcount

    cur.close()
    return affected > 0


def delete_user_db(user_id):
    """
    Elimina un usuario de la base de datos por su ID.
    """
    cur = current_app.mysql.connection.cursor(dictionary=True)
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    current_app.mysql.connection.commit()
    affected = cur.rowcount
    cur.close()
    return affected > 0