import sys
sys.path.append('..')
from datetime import datetime
from bson import ObjectId
from Conexion import bd
from Colecciones.Usuario import crear_usuario


def registrar_usuario(nombre, apellido, correo, contraseña, roles=None):
    """Registra un nuevo usuario en la base de datos."""
    # Verificar si el correo ya existe
    if bd.usuarios.find_one({"correo": correo}):
        return None  # Correo ya registrado
    
    usuario = crear_usuario(nombre, apellido, correo, contraseña, roles)
    resultado = bd.usuarios.insert_one(usuario)
    return resultado.inserted_id


def buscar_usuario_id(usuario_id):
    """Busca un usuario por su ID."""
    return bd.usuarios.find_one({"_id": ObjectId(usuario_id)})


def buscar_usuario_correo(correo):
    """Busca un usuario por su correo."""
    return bd.usuarios.find_one({"correo": correo})


def actualizar_usuario(usuario_id, datos):
    """
    Actualiza los datos de un usuario.
    datos: diccionario con los campos a actualizar
    """
    datos["updatedAt"] = datetime.now()
    resultado = bd.usuarios.update_one(
        {"_id": ObjectId(usuario_id)},
        {"$set": datos}
    )
    return resultado.modified_count > 0


def eliminar_usuario(usuario_id):
    """Elimina un usuario de la base de datos."""
    resultado = bd.usuarios.delete_one({"_id": ObjectId(usuario_id)})
    return resultado.deleted_count > 0


# ==========================================
# MODERACIÓN
# ==========================================

def dar_strike(usuario_id):
    """
    Suma 1 strike al usuario.
    Si llega a 3, lo banea automáticamente.
    Retorna el nuevo número de strikes.
    """
    usuario = buscar_usuario_id(usuario_id)  # ✅ CORREGIDO
    if not usuario:
        return None
    
    nuevos_strikes = usuario["strikes"] + 1
    
    if nuevos_strikes >= 3:
        banear_usuario(usuario_id)
        return 3
    
    bd.usuarios.update_one(
        {"_id": ObjectId(usuario_id)},
        {
            "$set": {
                "strikes": nuevos_strikes,
                "updatedAt": datetime.now()
            }
        }
    )
    return nuevos_strikes


def banear_usuario(usuario_id):
    """Banea un usuario cambiando su estado a 'baneado'."""
    resultado = bd.usuarios.update_one(
        {"_id": ObjectId(usuario_id)},
        {
            "$set": {
                "estadoCuenta": "baneado",
                "fechaBaneo": datetime.now(),
                "updatedAt": datetime.now()
            }
        }
    )
    return resultado.modified_count > 0


def desbanear_usuario(usuario_id):
    """Desbanea un usuario, volviendo su estado a 'activo'."""
    resultado = bd.usuarios.update_one(
        {"_id": ObjectId(usuario_id)},
        {
            "$set": {
                "estadoCuenta": "activo",
                "strikes": 0,
                "fechaBaneo": None,
                "updatedAt": datetime.now()
            }
        }
    )
    return resultado.modified_count > 0


def agregar_rol(usuario_id, rol):
    """Agrega un rol al usuario si no lo tiene."""
    resultado = bd.usuarios.update_one(
        {"_id": ObjectId(usuario_id)},
        {
            "$addToSet": {"roles": rol},
            "$set": {"updatedAt": datetime.now()}
        }
    )
    return resultado.modified_count > 0


def quitar_rol(usuario_id, rol):
    """Quita un rol al usuario."""
    resultado = bd.usuarios.update_one(
        {"_id": ObjectId(usuario_id)},
        {
            "$pull": {"roles": rol},
            "$set": {"updatedAt": datetime.now()}
        }
    )
    return resultado.modified_count > 0