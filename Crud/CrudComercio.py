import sys
sys.path.append('..')
from datetime import datetime
from bson import ObjectId
from Conexion import bd
from Colecciones.Comercio import crear_comercio

# ==========================================
# CRUD BÁSICO
# ==========================================

def registrar_comercio(propietario_id, nombre, descripcion, categoria, telefono, correo, direccion, horario=None):
    """Registra un nuevo comercio en la base de datos."""
    comercio = crear_comercio(propietario_id, nombre, descripcion, categoria, telefono, correo, direccion, horario)
    resultado = bd.comercios.insert_one(comercio)
    return resultado.inserted_id


def obtener_comercio_por_id(comercio_id):
    """Busca un comercio por su ID."""
    return bd.comercios.find_one({"_id": ObjectId(comercio_id)})


def obtener_comercios_por_propietario(propietario_id):
    """Busca todos los comercios de un propietario."""
    return list(bd.comercios.find({"propietarioId": ObjectId(propietario_id)}))


def actualizar_comercio(comercio_id, datos):
    """Actualiza los datos de un comercio."""
    datos["updatedAt"] = datetime.now()
    resultado = bd.comercios.update_one(
        {"_id": ObjectId(comercio_id)},
        {"$set": datos}
    )
    return resultado.modified_count > 0


def eliminar_comercio(comercio_id):
    """Elimina un comercio de la base de datos."""
    resultado = bd.comercios.delete_one({"_id": ObjectId(comercio_id)})
    return resultado.deleted_count > 0


# ==========================================
# HORARIOS
# ==========================================

def actualizar_horario(comercio_id, dia, turnos):
    """Actualiza el horario de un día específico."""
    resultado = bd.comercios.update_one(
        {"_id": ObjectId(comercio_id)},
        {"$set": {f"horario.{dia}": turnos, "updatedAt": datetime.now()}}
    )
    return resultado.modified_count > 0