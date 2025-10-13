from repositories.user_repository import (
    insert_user,
    get_user_by_username,
    get_user_by_national_id
)
import bcrypt
import re

def validate_credentials(username, password):
    user = get_user_by_username(username)
    print("DEBUG - Usuario obtenido:", user)

    if not user:
        return False, None, "User not found"

    stored_password = user['password'].encode('utf-8')
    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
        return True, user, "Login successful"

    return False, None, "Incorrect password"

def is_password_valid(password, personal_data=[]):
    requirements_message = (
        "Password requirements:\n"
        "- Minimum length: 12 characters\n"
        "- At least one uppercase letter\n"
        "- At least one lowercase letter\n"
        "- At least one number\n"
        "- At least one special character (!@#$%^&*)"
    )

    if len(password) < 12 or \
       not re.search(r'[A-Z]', password) or \
       not re.search(r'[a-z]', password) or \
       not re.search(r'\d', password) or \
       not re.search(r'[!@#$%^&*]', password):
        return False, requirements_message

    lowered = password.lower()
    for item in personal_data:
        if item and item.lower() in lowered:
            return False, "Password must not contain personal data like name or ID."

    return True, "Password is valid"

def register_user(data):
    username = data['username']
    password = data['password']
    national_id = data['national_id']
    full_name = data['full_name']
    branch_id = data.get('branch_id')  # optional
    role_id = 1  # default role for new users

    personal_data = [username, national_id, full_name]

    # Check if user already exists
    if get_user_by_username(username):
        return False, "Username already exists"

    if get_user_by_national_id(national_id):
        return False, "National ID already exists"

    # Validate password
    is_valid, msg = is_password_valid(password, personal_data)
    if not is_valid:
        return False, msg

    # Hash password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Insert user
    try:
        insert_user(username, hashed, national_id, full_name, role_id, branch_id)
        return True, "User registered successfully"
    except Exception as e:
        print("ERROR - Registration failed:", e)
        return False, f"Database error: {str(e)}"
