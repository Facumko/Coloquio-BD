import sys
sys.path.append('..')
from datetime import datetime
from bson import ObjectId
from Conexion import bd
from Colecciones.publicacion import crear_publicacion

def crear_publicacion_db(comercio_id, titulo, descripcion, imagenes=None):
    publicacion = crear_publicacion(comercio_id, titulo, descripcion, imagenes)
    resultado = bd.publicaciones.insert_one(publicacion)
    return resultado.inserted_id


def obtener_publicacion_por_id(publicacion_id):
    return bd.publicaciones.find_one({"_id": ObjectId(publicacion_id)})


def obtener_publicaciones_por_comercio(comercio_id, limite=20, pagina=1):

    skip = (pagina - 1) * limite
    publicaciones = bd.publicaciones.find(
        {"comercioId": ObjectId(comercio_id), "estado": "activo"}
    ).sort("createdAt", -1).skip(skip).limit(limite)
    
    return list(publicaciones)


def obtener_todas_publicaciones(limite=50, pagina=1):
    skip = (pagina - 1) * limite
    publicaciones = bd.publicaciones.find(
        {"estado": "activo"}
    ).sort("createdAt", -1).skip(skip).limit(limite)
    
    return list(publicaciones)


def actualizar_publicacion(publicacion_id, datos):

    datos["updatedAt"] = datetime.now()
    resultado = bd.publicaciones.update_one(
        {"_id": ObjectId(publicacion_id)},
        {"$set": datos}
    )
    return resultado.modified_count > 0


def eliminar_publicacion(publicacion_id):
    resultado = bd.publicaciones.delete_one({"_id": ObjectId(publicacion_id)})
    return resultado.deleted_count > 0