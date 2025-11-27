from datetime import datetime, timedelta

def crear_notificacion(usuario_id, tipo, mensaje, reporte_id=None):
    notificacion = {
        "usuarioId": usuario_id,
        "tipo": tipo,
        "mensaje": mensaje,
        "leida": False,
        "reporteId": reporte_id,
        "createdAt": datetime.now(),
        "expiraEn": datetime.now() + timedelta(days=30)
    }
    return notificacion
