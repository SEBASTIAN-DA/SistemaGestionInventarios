
from repositories.user_repository import (
    get_user_by_national_id,
    update_user_password,
    save_password_to_history,
    get_last_password_hashes
)
from utils.password_utils import (
    hash_password,
    is_valid_password,
    is_password_reused
)

def recover_password(national_id, new_password):
    # Buscar usuario por cédula
    user = get_user_by_national_id(national_id)
    if not user:
        return False, "Usuario no encontrado."

    # Validar contraseña nueva
    user_data = [user['full_name'], user['national_id'], user['username'],]
    is_valid, message = is_valid_password(new_password, user_data)
    if not is_valid:
        return False, message

    # Encriptar nueva contraseña
    new_password_hash = hash_password(new_password)

    # Verificar que no se haya usado antes
    previous_hashes = get_last_password_hashes(user['id'], limit=5)
    if is_password_reused(new_password, previous_hashes):
        return False, "La nueva contraseña ya fue usada recientemente. Usa una diferente."

    # Actualizar contraseña y guardar en historial
    update_user_password(user['id'], new_password_hash)
    save_password_to_history(user['id'], new_password_hash)

    return True, "Contraseña actualizada exitosamente."
