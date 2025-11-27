import sys
sys.path.append('..')
from datetime import datetime
from bson import ObjectId
from Conexion import bd
from Colecciones.Comercio import crear_comercio

#crear comercio
def registrar_comercio(propietario_id, nombre, descripcion, categoria, telefono, correo, direccion, horario=None):
    comercio = crear_comercio(propietario_id, nombre, descripcion, categoria, telefono, correo, direccion, horario)
    resultado = bd.comercios.insert_one(comercio)
    return resultado.inserted_id

#buscar x id
def buscar_comercio_id(comercio_id):
    return bd.comercios.find_one({"_id": ObjectId(comercio_id)})

#buscar x dueño
def Buscar_comercio_dueño(propietario_id):
    return list(bd.comercios.find({"propietarioId": ObjectId(propietario_id)}))

# actualizar 
def actualizar_comercio(comercio_id, datos):
    datos["updatedAt"] = datetime.now()
    resultado = bd.comercios.update_one(
        {"_id": ObjectId(comercio_id)},
        {"$set": datos}
    )
    return resultado.modified_count > 0

#eliminar
def eliminar_comercio(comercio_id):
    resultado = bd.comercios.delete_one({"_id": ObjectId(comercio_id)})
    return resultado.deleted_count > 0

#actualizar horario
def actualizar_horario(comercio_id, dia, turnos):
    resultado = bd.comercios.update_one(
        {"_id": ObjectId(comercio_id)},
        {"$set": {f"horario.{dia}": turnos, "updatedAt": datetime.now()}}
    )
    return resultado.modified_count > 0