from datetime import datetime
def crear_direccion (calle, numero, ciudad, provincia, codigo_postal, lat = None, long = None):
    return {
        "calle": calle,
        "numero": numero,
        "ciudad": ciudad,
        "provincia": provincia,
        "codigo_postal": codigo_postal,
        "coordenadas": {
        "lat":lat,
        "long": long
    }
}

def crear_horario_vacio():
    return {
        "lunes": [],
        "martes": [],
        "miercoles": [],
        "jueves": [],
        "viernes": [],
        "sabado": [],
        "domingo": []
    }

def crear_comercio (propietario_id, nombre, descripcion, categoria, telefono, correo, direccion, horario=None):
    if horario is None:
        horario = crear_horario_vacio()
    
    comercio = {
        "propietario_id": propietario_id,
        "nombre": nombre,
        "descripcion": descripcion,
        "categoria": categoria,
        "telefono": telefono,
        "correo": correo,
        "direccion": direccion,
        "horario": horario,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    return comercio

