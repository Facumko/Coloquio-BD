import sys
sys.path.append('..')
from datetime import datetime
from bson import ObjectId
from Conexion import bd
from Colecciones.comentario import crear_comentario

def crear_comentario_db(autor_id, contenido_id, tipo_contenido, texto):
    comentario = crear_comentario(autor_id, contenido_id, tipo_contenido, texto)
    resultado = bd.comentarios.insert_one(comentario)
    return resultado.inserted_id


def obtener_comentario_por_id(comentario_id):
    return bd.comentarios.find_one({"_id": ObjectId(comentario_id)})


def obtener_comentarios_por_contenido(contenido_id, tipo_contenido, limite=50, pagina=1):

    skip = (pagina - 1) * limite
    comentarios = bd.comentarios.find({
        "contenidoId": ObjectId(contenido_id),
        "tipoContenido": tipo_contenido,
        "estado": "activo"
    }).sort("createdAt", -1).skip(skip).limit(limite)
    
    return list(comentarios)


def obtener_comentarios_por_autor(autor_id, limite=50, pagina=1):
    skip = (pagina - 1) * limite
    comentarios = bd.comentarios.find({
        "autorId": ObjectId(autor_id)
    }).sort("createdAt", -1).skip(skip).limit(limite)
    
    return list(comentarios)


def actualizar_comentario(comentario_id, texto):
    resultado = bd.comentarios.update_one(
        {"_id": ObjectId(comentario_id)},
        {
            "$set": {
                "texto": texto,
                "updateAt": datetime.now()
            }
        }
    )
    return resultado.modified_count > 0


def eliminar_comentario(comentario_id):
    resultado = bd.comentarios.delete_one({"_id": ObjectId(comentario_id)})
    return resultado.deleted_count > 0


def incrementar_reportes(comentario_id):

    comentario = obtener_comentario_por_id(comentario_id)
    if not comentario:
        return None
    
    nuevo_contador = comentario["cantidadReportes"] + 1
    
    if nuevo_contador >= 3:
        bd.comentarios.update_one(
            {"_id": ObjectId(comentario_id)},
            {
                "$set": {
                    "cantidadReportes": nuevo_contador,
                    "estado": "pendiente",
                    "updateAt": datetime.now()
                }
            }
        )
    else:
        bd.comentarios.update_one(
            {"_id": ObjectId(comentario_id)},
            {
                "$set": {
                    "cantidadReportes": nuevo_contador,
                    "updateAt": datetime.now()
                }
            }
        )
    
    return nuevo_contador


def marcar_como_pendiente(comentario_id):
    resultado = bd.comentarios.update_one(
        {"_id": ObjectId(comentario_id)},
        {
            "$set": {
                "estado": "pendiente",
                "updateAt": datetime.now()
            }
        }
    )
    return resultado.modified_count > 0


def obtener_comentarios_pendientes(limite=50):

    comentarios = bd.comentarios.find({
        "estado": "pendiente"
    }).sort("cantidadReportes", -1).limit(limite)
    
    return list(comentarios)


def obtener_comentarios_reportados(limite=50):

    comentarios = bd.comentarios.find({
        "cantidadReportes": {"$gte": 1},
        "estado": {"$ne": "eliminado"}
    }).sort("cantidadReportes", -1).limit(limite)
    
    return list(comentarios)


def contar_comentarios_por_contenido(contenido_id, tipo_contenido):
    return bd.comentarios.count_documents({
        "contenidoId": ObjectId(contenido_id),
        "tipoContenido": tipo_contenido,
        "estado": "activo"
    })


def contar_comentarios_por_autor(autor_id):
    return bd.comentarios.count_documents({
        "autorId": ObjectId(autor_id)
    })


def eliminar_comentarios_por_autor(autor_id):

    resultado = bd.comentarios.delete_many({"autorId": ObjectId(autor_id)})
    return resultado.deleted_count