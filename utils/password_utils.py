
import re
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def is_valid_password(password, user_data):
    """
    user_data: lista de datos personales como [nombre, cedula, correo]
    """
    if len(password) < 12:
        return False, "La contraseña debe tener al menos 12 caracteres."
    if not re.search(r'[A-Z]', password):
        return False, "Debe contener al menos una letra mayúscula."
    if not re.search(r'[a-z]', password):
        return False, "Debe contener al menos una letra minúscula."
    if not re.search(r'\d', password):
        return False, "Debe contener al menos un número."
    if not re.search(r'[!@#$%^&*]', password):
        return False, "Debe contener al menos un carácter especial (!@#$%^&*)."
    for dato in user_data:
        if dato and dato.lower() in password.lower():
            return False, "La contraseña no debe contener datos personales como nombre, cédula o correo."
    return True, "Contraseña válida."

def is_password_reused(new_hash, previous_hashes):
    """
    Compara el nuevo hash con los anteriores usando bcrypt.
    """
    for old_hash in previous_hashes:
        if check_password(new_hash, old_hash):
            return True
    return False
