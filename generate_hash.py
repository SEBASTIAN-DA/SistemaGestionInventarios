import bcrypt

password = "SecurePass123!"  # Esta será la contraseña del usuario
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print("Contraseña encriptada:", hashed)
