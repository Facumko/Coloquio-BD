from datetime import datetime
from bson import ObjectId
from Conexion import bd
from Colecciones.Usuario import crear_usuario

#verifica si el email existe
def registrar_usuario(nombre, apellido, email, password, roles=None):
    if bd.usuarios.find_one({"email": email}):
        return None  
    
    usuario = crear_usuario(nombre, apellido, email, password, roles)
    resultado = bd.usuarios.insert_one(usuario)
    return resultado.inserted_id

#busca usuario x id
def buscar_usuario_id(usuario_id):
    return bd.usuarios.find_one({"_id": ObjectId(usuario_id)})

#busca usuario x email
def buscar_usuario_mail(email):
    return bd.usuarios.find_one({"email": email})


def actualizar_usuario(usuario_id, datos):

    datos["updatedAt"] = datetime.now()
    resultado = bd.usuarios.update_one(
        {"_id": ObjectId(usuario_id)},
        {"$set": datos}
    )
    return resultado.modified_count > 0


def eliminar_usuario(usuario_id):
    resultado = bd.usuarios.delete_one({"_id": ObjectId(usuario_id)})
    return resultado.deleted_count > 0


# strikesp ara banear
def dar_strike(usuario_id):

    usuario = obtener_usuario_por_id(usuario_id)
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

#baneo usuario
def banear_usuario(usuario_id):
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

# desbaneo usuario
def desbanear_usuario(usuario_id):
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
    resultado = bd.usuarios.update_one(
        {"_id": ObjectId(usuario_id)},
        {
            "$addToSet": {"roles": rol},
            "$set": {"updatedAt": datetime.now()}
        }
    )
    return resultado.modified_count > 0


def quitar_rol(usuario_id, rol):
    resultado = bd.usuarios.update_one(
        {"_id": ObjectId(usuario_id)},
        {
            "$pull": {"roles": rol},
            "$set": {"updatedAt": datetime.now()}
        }
    )
    return resultado.modified_count > 0