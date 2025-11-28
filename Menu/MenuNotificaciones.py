import sys
sys.path.append('..')
from bson import ObjectId
from Conexion import bd
from Crud.CrudUsuario import buscar_usuario_id
from Utilidades import limpiar_pantalla, pausar, mostrar_encabezado

def menu_ver_notificaciones():
    while True:
        limpiar_pantalla()
        mostrar_encabezado("VER NOTIFICACIONES DE USUARIOS")
        
        print("\n1. Ver notificaciones de un usuario")
        print("2.  Usuarios con notificaciones pendientes")
        print("0.  Volver")
        
        opcion = input("\n Selecciona: ").strip()
        
        if opcion == "1":
            ver_notificaciones_usuario()
        elif opcion == "2":
            listar_usuarios_con_notificaciones()
        elif opcion == "0":
            break
        else:
            print("Opción inválida")
            pausar()

def ver_notificaciones_usuario():
    mostrar_encabezado("NOTIFICACIONES DE USUARIO")
    usuario_id = input("\n ID del usuario: ").strip()
    
    try:
        usuario = buscar_usuario_id(usuario_id)
        if not usuario:
            print("\n Usuario no encontrado")
            pausar()
            return
        
        print(f"\n Usuario: {usuario['nombre']} {usuario['apellido']}")
        print(f" Correo: {usuario['correo']}")
        
        notificaciones = list(bd.notificaciones.find(
            {"usuarioId": ObjectId(usuario_id)}
        ).sort("createdAt", -1).limit(20))
        
        if not notificaciones:
            print("\n No hay notificaciones")
        else:
            print(f"\n Total: {len(notificaciones)}\n")
            for i, notif in enumerate(notificaciones, 1):
                estado = " LEÍDA" if notif.get("leida") else "NO LEÍDA"
                print(f"\n{'='*70}")
                print(f" NOTIFICACIÓN #{i} - {estado}")
                print(f"{'='*70}")
                print(f" ID: {notif['_id']}")
                print(f" Tipo: {notif.get('tipo', 'N/A')}")
                print(f" Mensaje: {notif.get('mensaje', 'N/A')}")
                print(f" Fecha: {notif.get('createdAt', 'N/A')}")
    except Exception as e:
        print(f"\n Error: {e}")
    pausar()

def listar_usuarios_con_notificaciones():
    mostrar_encabezado("USUARIOS CON NOTIFICACIONES PENDIENTES")
    try:
        pipeline = [
            {"$match": {"leida": False}},
            {"$group": {"_id": "$usuarioId", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
            {"$limit": 20}
        ]
        resultados = list(bd.notificaciones.aggregate(pipeline))
        
        if not resultados:
            print("\n No hay notificaciones pendientes")
        else:
            print(f"\n Usuarios con notificaciones no leídas: {len(resultados)}\n")
            print(f"{'Usuario':<40} {'Pendientes':<15}")
            print("-" * 55)
            for res in resultados:
                usuario = bd.usuarios.find_one({"_id": res["_id"]})
                if usuario:
                    nombre = f"{usuario['nombre']} {usuario['apellido']}"[:39]
                    print(f"{nombre:<40} {res['total']:<15}")
    except Exception as e:
        print(f"\n Error: {e}")
    pausar()