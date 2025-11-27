from datetime import datetime

def crear_usuario(nombre, apellido, correo, contraseña, roles=None):
    if roles is None:
        roles = ["Usuario"]

    usuario = {
        "nombre": nombre,
        "apellido": apellido,
        "correo": correo,
        "contraseña": contraseña, 
        "roles": roles,
        "strikes": 0,
        "estadoCuenta": "activo",
        "fechaBaneo": None,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }

    return usuario