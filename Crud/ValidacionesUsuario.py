import sys
sys.path.append('..')
from Conexion import bd

def aplicar_validacion_usuarios():

    try:
        bd.command({
            "collMod": "usuarios",
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["nombre", "apellido", "correo", "contraseña", "roles"],
                    "properties": {
                        "nombre": {
                            "bsonType": "string",
                            "minLength": 2,
                            "maxLength": 50,
                            "description": "Nombre del usuario (2-50 caracteres)"
                        },
                        "apellido": {
                            "bsonType": "string",
                            "minLength": 2,
                            "maxLength": 50,
                            "description": "Apellido del usuario (2-50 caracteres)"
                        },
                        "correo": {
                            "bsonType": "string",
                            "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                            "description": "Email válido"
                        },
                        "contraseña": {
                            "bsonType": "string",
                            "minLength": 6,
                            "description": "Contraseña (mínimo 6 caracteres)"
                        },
                        "roles": {
                            "bsonType": "array",
                            "minItems": 1,
                            "items": {
                                "enum": ["Usuario", "Admin", "Propietario"]
                            },
                            "description": "Lista de roles del usuario"
                        },
                        "strikes": {
                            "bsonType": "int",
                            "minimum": 0,
                            "maximum": 3,
                            "description": "Número de strikes (0-3)"
                        },
                        "estadoCuenta": {
                            "enum": ["activo", "baneado"],
                            "description": "Estado de la cuenta"
                        },
                        "fechaBaneo": {
                            "bsonType": ["date", "null"],
                            "description": "Fecha de baneo (si aplica)"
                        },
                        "createdAt": {
                            "bsonType": "date",
                            "description": "Fecha de creación"
                        },
                        "updatedAt": {
                            "bsonType": "date",
                            "description": "Fecha de última actualización"
                        }
                    }
                }
            },
            "validationLevel": "moderate",
            "validationAction": "error"
        })
        
        print("Validacion aplicada correctamente a la coleccion 'usuarios'")
        return True
        
    except Exception as e:
        print(f"Error al aplicar validacion: {e}")
        return False


def verificar_validacion():
    try:
        coleccion_info = bd.command({"listCollections": 1, "filter": {"name": "usuarios"}})
        if coleccion_info["cursor"]["firstBatch"]:
            info = coleccion_info["cursor"]["firstBatch"][0]
            if "options" in info and "validator" in info["options"]:
                print("La coleccion 'usuarios' tiene validacion activa")
                return True
            else:
                print("La coleccion 'usuarios' NO tiene validacion activa")
                return False
    except Exception as e:
        print(f"Error al verificar validacion: {e}")
        return False


if __name__ == "__main__":
    print("="*70)
    print("APLICANDO VALIDACIONES JSON SCHEMA A USUARIOS")
    print("="*70)
    print()
    
    aplicar_validacion_usuarios()
    print()
    verificar_validacion()
    
    print()
    print("="*70)