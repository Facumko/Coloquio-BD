from datetime import datetime

def crear_publicacion (comercio_id, titulo, descripcion, imagenes=None):
    if imagenes is None:
        imagenes = []

    post = {
        "comercioId": comercio_id,
        "titulo": titulo,
        "descripcion": descripcion,
        "imagenes": imagenes,
        "estado": "activo",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }

    return post