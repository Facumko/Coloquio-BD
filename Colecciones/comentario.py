from datetime import datetime

def crear_comentario(autor_id, contenido_id, tipo_contenido, texto):

    comentario = {
        "autorId":autor_id,
        "contenidoId": contenido_id,
        "tipoContenido": tipo_contenido,
        "texto": texto,
        "estado": "activo",
        "cantidadReportes": 0,
        "createdAt": datetime.now(),
        "updateAt": datetime.now()
        }
    return comentario
