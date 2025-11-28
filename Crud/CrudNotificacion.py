import sys
sys.path.append('..')
from datetime import datetime
from bson import ObjectId
from Conexion import bd
from Colecciones.notificacion import crear_notificacion


def crear_notificacion_db(usuario_id, tipo, mensaje, reporte_id=None):

    notificacion = crear_notificacion(usuario_id, tipo, mensaje, reporte_id)
    resultado = bd.notificaciones.insert_one(notificacion)
    return resultado.inserted_id


def obtener_notificacion_por_id(notificacion_id):
    return bd.notificaciones.find_one({"_id": ObjectId(notificacion_id)})


def obtener_notificaciones_por_usuario(usuario_id, limite=50, pagina=1):
    skip = (pagina - 1) * limite
    notificaciones = bd.notificaciones.find({
        "usuarioId": ObjectId(usuario_id)
    }).sort("createdAt", -1).skip(skip).limit(limite)
    
    return list(notificaciones)


def obtener_notificaciones_no_leidas(usuario_id):
    notificaciones = bd.notificaciones.find({
        "usuarioId": ObjectId(usuario_id),
        "leida": False
    }).sort("createdAt", -1)
    
    return list(notificaciones)


def marcar_como_leida(notificacion_id):
    resultado = bd.notificaciones.update_one(
        {"_id": ObjectId(notificacion_id)},
        {"$set": {"leida": True}}
    )
    return resultado.modified_count > 0


def marcar_todas_como_leidas(usuario_id):
    resultado = bd.notificaciones.update_many(
        {"usuarioId": ObjectId(usuario_id), "leida": False},
        {"$set": {"leida": True}}
    )
    return resultado.modified_count


def eliminar_notificacion(notificacion_id):
    resultado = bd.notificaciones.delete_one({"_id": ObjectId(notificacion_id)})
    return resultado.deleted_count > 0


def eliminar_notificaciones_por_usuario(usuario_id):
    resultado = bd.notificaciones.delete_many({"usuarioId": ObjectId(usuario_id)})
    return resultado.deleted_count


def contar_notificaciones_no_leidas(usuario_id):
    return bd.notificaciones.count_documents({
        "usuarioId": ObjectId(usuario_id),
        "leida": False
    })


def eliminar_notificaciones_expiradas():

    resultado = bd.notificaciones.delete_many({
        "expiraEn": {"$lt": datetime.now()}
    })
    return resultado.deleted_count


def obtener_notificaciones_por_tipo(usuario_id, tipo, limite=20):
    """Obtiene notificaciones de un tipo específico para un usuario."""
    notificaciones = bd.notificaciones.find({
        "usuarioId": ObjectId(usuario_id),
        "tipo": tipo
    }).sort("createdAt", -1).limit(limite)
    
    return list(notificaciones)


def crear_notificacion_admin(tipo, mensaje, reporte_id=None):
    admins = bd.usuarios.find({"roles": "Admin"})
    
    notificaciones_creadas = 0
    for admin in admins:
        notificacion = crear_notificacion(admin["_id"], tipo, mensaje, reporte_id)
        bd.notificaciones.insert_one(notificacion)
        notificaciones_creadas += 1
    
    return notificaciones_creadas