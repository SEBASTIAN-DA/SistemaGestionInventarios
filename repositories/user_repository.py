from flask import current_app

def get_user_by_username(username):
    cur = current_app.mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    return user

def get_user_by_national_id(national_id):
    cur = current_app.mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE national_id = %s", (national_id,))
    user = cur.fetchone()
    cur.close()
    return user

def update_user_password(user_id, new_password_hash):
    cur = current_app.mysql.connection.cursor()
    cur.execute("""
        UPDATE users 
        SET password = %s, password_expiration = DATE_ADD(CURRENT_DATE, INTERVAL 90 DAY)
        WHERE id = %s
    """, (new_password_hash, user_id))
    current_app.mysql.connection.commit()
    cur.close()

def save_password_to_history(user_id, password_hash):
    cur = current_app.mysql.connection.cursor()
    cur.execute("""
        INSERT INTO password_history (user_id, password_hash)
        VALUES (%s, %s)
    """, (user_id, password_hash))
    current_app.mysql.connection.commit()
    cur.close()

def get_last_password_hashes(user_id, limit=5):
    cur = current_app.mysql.connection.cursor()
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
    cur = current_app.mysql.connection.cursor()
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
