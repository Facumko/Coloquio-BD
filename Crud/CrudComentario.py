import sys
sys.path.append('..')
from datetime import datetime
from bson import ObjectId
from Conexion import bd
from Colecciones.comentario import crear_comentario

# ==========================================
# CRUD BÁSICO
# ==========================================

def crear_comentario_db(autor_id, contenido_id, tipo_contenido, texto):
    """
    Crea un nuevo comentario en la base de datos.
    tipo_contenido: "publicacion" o "evento"
    """
    comentario = crear_comentario(autor_id, contenido_id, tipo_contenido, texto)
    resultado = bd.comentarios.insert_one(comentario)
    return resultado.inserted_id


def obtener_comentario_por_id(comentario_id):
    """Busca un comentario por su ID."""
    return bd.comentarios.find_one({"_id": ObjectId(comentario_id)})


def obtener_comentarios_por_contenido(contenido_id, tipo_contenido, limite=50, pagina=1):
    """
    Obtiene los comentarios de una publicación o evento específico.
    Solo trae comentarios activos.
    """
    skip = (pagina - 1) * limite
    comentarios = bd.comentarios.find({
        "contenidoId": ObjectId(contenido_id),
        "tipoContenido": tipo_contenido,
        "estado": "activo"
    }).sort("createdAt", -1).skip(skip).limit(limite)
    
    return list(comentarios)


def obtener_comentarios_por_autor(autor_id, limite=50, pagina=1):
    """Obtiene todos los comentarios de un usuario."""
    skip = (pagina - 1) * limite
    comentarios = bd.comentarios.find({
        "autorId": ObjectId(autor_id)
    }).sort("createdAt", -1).skip(skip).limit(limite)
    
    return list(comentarios)


def actualizar_comentario(comentario_id, texto):
    """Actualiza el texto de un comentario."""
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
    """Elimina un comentario de la base de datos."""
    resultado = bd.comentarios.delete_one({"_id": ObjectId(comentario_id)})
    return resultado.deleted_count > 0


# ==========================================
# MODERACIÓN Y REPORTES
# ==========================================

def incrementar_reportes(comentario_id):
    """
    Incrementa el contador de reportes del comentario.
    Si llega a 3 o más, marca el comentario como "pendiente".
    Retorna el nuevo número de reportes.
    """
    comentario = obtener_comentario_por_id(comentario_id)
    if not comentario:
        return None
    
    nuevo_contador = comentario["cantidadReportes"] + 1
    
    # Si llega a 3 reportes, cambiar estado a pendiente de revisión
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
    """Marca un comentario como pendiente de revisión administrativa."""
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
    """
    Obtiene todos los comentarios pendientes de revisión.
    Útil para el panel de administración.
    """
    comentarios = bd.comentarios.find({
        "estado": "pendiente"
    }).sort("cantidadReportes", -1).limit(limite)
    
    return list(comentarios)


def obtener_comentarios_reportados(limite=50):
    """
    Obtiene comentarios con al menos 1 reporte, ordenados por cantidad.
    """
    comentarios = bd.comentarios.find({
        "cantidadReportes": {"$gte": 1},
        "estado": {"$ne": "eliminado"}
    }).sort("cantidadReportes", -1).limit(limite)
    
    return list(comentarios)


# ==========================================
# ESTADÍSTICAS Y CONSULTAS
# ==========================================

def contar_comentarios_por_contenido(contenido_id, tipo_contenido):
    """Cuenta cuántos comentarios activos tiene una publicación o evento."""
    return bd.comentarios.count_documents({
        "contenidoId": ObjectId(contenido_id),
        "tipoContenido": tipo_contenido,
        "estado": "activo"
    })


def contar_comentarios_por_autor(autor_id):
    """Cuenta cuántos comentarios ha hecho un usuario."""
    return bd.comentarios.count_documents({
        "autorId": ObjectId(autor_id)
    })


def eliminar_comentarios_por_autor(autor_id):
    """
    Elimina todos los comentarios de un usuario.
    Útil cuando se banea a un usuario.
    """
    resultado = bd.comentarios.delete_many({"autorId": ObjectId(autor_id)})
    return resultado.deleted_count