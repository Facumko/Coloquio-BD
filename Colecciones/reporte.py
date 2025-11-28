from datetime import datetime

def crear_reporte(comentario_id, usuario_que_reporta, usuario_reportado, motivo):
    reporte = {
        "comentarioId": comentario_id,
        "usuarioQueReporta": usuario_que_reporta,
        "usuarioReportado": usuario_reportado,
        "motivo": motivo,
        "estado": "pendiente",
        "comentarioEliminado": False,
        "strikeAplicado": False,
        "usuarioBaneado": False,
        "adminId": None,
        "createAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    return reporte