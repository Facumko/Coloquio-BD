from datetime import datetime

def crear_evento(comercio_creador_id, titulo, descripcion, fecha_inicio, fecha_fin, ubicacion, imagenes=None, comercios_invitados=None):
    if imagenes is None:
        imagenes = []

    if comercios_invitados is None:
        comercios_invitados = []


    evento = {
        "comercioCreadorId": comercio_creador_id,
        "comerciosInvitados": comercios_invitados,
        "titulo": titulo,
        "descripcion": descripcion,
        "imagenes": imagenes,
        "fechaInicio": fecha_inicio,
        "fechaFin": fecha_fin,
        "ubicacion": ubicacion,
        "estado": "activo",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    return evento
