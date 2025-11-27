import sys
sys.path.append('..')
from datetime import datetime
from bson import ObjectId
from Conexion import bd
from Colecciones.reporte import crerar_reporte

# ==========================================
# CRUD BÁSICO
# ==========================================

def crear_reporte_db(comentario_id, usuario_que_reporta, usuario_reportado, motivo):
    """Crea un nuevo reporte en la base de datos."""
    reporte = crerar_reporte(comentario_id, usuario_que_reporta, usuario_reportado, motivo)
    resultado = bd.reportes.insert_one(reporte)
    return resultado.inserted_id


def obtener_reporte_por_id(reporte_id):
    """Busca un reporte por su ID."""
    return bd.reportes.find_one({"_id": ObjectId(reporte_id)})


def obtener_reportes_por_comentario(comentario_id):
    """Obtiene todos los reportes de un comentario específico."""
    reportes = bd.reportes.find({
        "comentarioId": ObjectId(comentario_id)
    }).sort("createAt", -1)
    
    return list(reportes)


def obtener_reportes_pendientes(limite=50, pagina=1):
    """
    Obtiene todos los reportes pendientes de revisión.
    Para el panel de administración.
    """
    skip = (pagina - 1) * limite
    reportes = bd.reportes.find({
        "estado": "pendiente"
    }).sort("createAt", 1).skip(skip).limit(limite)  # Más antiguos primero
    
    return list(reportes)


def obtener_reportes_por_usuario_reportado(usuario_id, limite=50):
    """Obtiene todos los reportes donde aparece un usuario como reportado."""
    reportes = bd.reportes.find({
        "usuarioReportado": ObjectId(usuario_id)
    }).sort("createAt", -1).limit(limite)
    
    return list(reportes)


def actualizar_reporte(reporte_id, datos):
    """
    Actualiza los datos de un reporte.
    datos: diccionario con los campos a actualizar
    """
    datos["updateAt"] = datetime.now()
    resultado = bd.reportes.update_one(
        {"_id": ObjectId(reporte_id)},
        {"$set": datos}
    )
    return resultado.modified_count > 0


def eliminar_reporte(reporte_id):
    """Elimina un reporte de la base de datos."""
    resultado = bd.reportes.delete_one({"_id": ObjectId(reporte_id)})
    return resultado.deleted_count > 0


# ==========================================
# GESTIÓN ADMINISTRATIVA
# ==========================================

def marcar_reporte_como_resuelto(reporte_id, admin_id):
    """
    Marca un reporte como resuelto y asigna el admin que lo procesó.
    Esta función se usa DENTRO de la transacción.
    """
    resultado = bd.reportes.update_one(
        {"_id": ObjectId(reporte_id)},
        {
            "$set": {
                "estado": "resuelto",
                "adminId": ObjectId(admin_id),
                "updateAt": datetime.now()
            }
        }
    )
    return resultado.modified_count > 0


def marcar_comentario_eliminado(reporte_id):
    """Marca que el comentario asociado fue eliminado."""
    resultado = bd.reportes.update_one(
        {"_id": ObjectId(reporte_id)},
        {
            "$set": {
                "comentarioEliminado": True,
                "updateAt": datetime.now()
            }
        }
    )
    return resultado.modified_count > 0


def marcar_strike_aplicado(reporte_id):
    """Marca que se aplicó un strike al usuario."""
    resultado = bd.reportes.update_one(
        {"_id": ObjectId(reporte_id)},
        {
            "$set": {
                "strikeAplicado": True,
                "updateAt": datetime.now()
            }
        }
    )
    return resultado.modified_count > 0


def marcar_usuario_baneado(reporte_id):
    """Marca que el usuario fue baneado por este reporte."""
    resultado = bd.reportes.update_one(
        {"_id": ObjectId(reporte_id)},
        {
            "$set": {
                "usuarioBaneado": True,
                "updateAt": datetime.now()
            }
        }
    )
    return resultado.modified_count > 0


# ==========================================
# ESTADÍSTICAS Y CONSULTAS
# ==========================================

def contar_reportes_pendientes():
    """Cuenta cuántos reportes están pendientes de revisión."""
    return bd.reportes.count_documents({"estado": "pendiente"})


def contar_reportes_por_usuario(usuario_id):
    """Cuenta cuántas veces ha sido reportado un usuario."""
    return bd.reportes.count_documents({
        "usuarioReportado": ObjectId(usuario_id)
    })


def obtener_reportes_resueltos(limite=50, pagina=1):
    """Obtiene el historial de reportes resueltos."""
    skip = (pagina - 1) * limite
    reportes = bd.reportes.find({
        "estado": "resuelto"
    }).sort("updateAt", -1).skip(skip).limit(limite)
    
    return list(reportes)