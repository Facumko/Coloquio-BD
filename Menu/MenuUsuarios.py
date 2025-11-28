
import sys
sys.path.append('..')
from Conexion import bd
from Crud.CrudUsuario import (
    registrar_usuario, buscar_usuario_id, buscar_usuario_correo,
    actualizar_usuario, eliminar_usuario
)
from Utilidades import limpiar_pantalla, pausar, mostrar_encabezado


def menu_crud_usuarios():
    """Submenú para operaciones CRUD de usuarios"""
    while True:
        limpiar_pantalla()
        mostrar_encabezado("CRUD DE USUARIOS")
        
        print("\n1.  Crear nuevo usuario")
        print("2.  Buscar usuario por ID")
        print("3. Buscar usuario por correo")
        print("4.   Actualizar usuario")
        print("5.   Eliminar usuario")
        print("6.  Listar todos los usuarios")
        print("0.   Volver al menú principal")
        
        opcion = input("\n Selecciona una opción: ").strip()
        
        if opcion == "1":
            crear_usuario_interactivo()
        elif opcion == "2":
            buscar_usuario_por_id_interactivo()
        elif opcion == "3":
            buscar_usuario_por_correo_interactivo()
        elif opcion == "4":
            actualizar_usuario_interactivo()
        elif opcion == "5":
            eliminar_usuario_interactivo()
        elif opcion == "6":
            listar_usuarios()
        elif opcion == "0":
            break
        else:
            print(" Opción inválida")
            pausar()


def crear_usuario_interactivo():
    mostrar_encabezado("CREAR NUEVO USUARIO")
    
    nombre = input("\n Nombre: ").strip()
    apellido = input(" Apellido: ").strip()
    correo = input(" Correo: ").strip()
    contraseña = input(" Contraseña: ").strip()
    
    print("\n Roles disponibles:")
    print("1. Usuario (predeterminado)")
    print("2. Usuario + Propietario")
    print("3. Usuario + Admin")
    
    rol_opcion = input("\n Selecciona roles (1-3): ").strip()
    
    roles = ["Usuario"]
    if rol_opcion == "2":
        roles.append("Propietario")
    elif rol_opcion == "3":
        roles.append("Admin")
    
    try:
        usuario_id = registrar_usuario(nombre, apellido, correo, contraseña, roles)
        
        if usuario_id:
            print(f"\n Usuario creado exitosamente!")
            print(f" ID: {usuario_id}")
            print(f" Nombre: {nombre} {apellido}")
            print(f" Correo: {correo}")
            print(f" Roles: {', '.join(roles)}")
        else:
            print("\n Error: El correo ya está registrado")
    
    except Exception as e:
        print(f"\n Error al crear usuario: {e}")
    
    pausar()


def buscar_usuario_por_id_interactivo():
    mostrar_encabezado("BUSCAR USUARIO POR ID")

    usuario_id = input("\n🆔 Ingresa el ID del usuario: ").strip()
    
    try:
        usuario = buscar_usuario_id(usuario_id)
        
        if usuario:
            print("\n Usuario encontrado:")
            print(f"\n ID: {usuario['_id']}")
            print(f" Nombre: {usuario['nombre']} {usuario['apellido']}")
            print(f" Correo: {usuario['correo']}")
            print(f" Roles: {', '.join(usuario.get('roles', []))}")
            print(f"  Strikes: {usuario.get('strikes', 0)}/3")
            print(f" Estado: {usuario.get('estadoCuenta', 'activo')}")
            print(f" Creado: {usuario.get('createdAt', 'N/A')}")
        else:
            print("\n Usuario no encontrado")
    
    except Exception as e:
        print(f"\n Error: {e}")
    
    pausar()


def buscar_usuario_por_correo_interactivo():
    mostrar_encabezado("BUSCAR USUARIO POR CORREO")
    
    correo = input("\n Ingresa el correo: ").strip()
    
    try:
        usuario = buscar_usuario_correo(correo)
        
        if usuario:
            print("\n Usuario encontrado:")
            print(f"\n ID: {usuario['_id']}")
            print(f" Nombre: {usuario['nombre']} {usuario['apellido']}")
            print(f" Correo: {usuario['correo']}")
            print(f" Roles: {', '.join(usuario.get('roles', []))}")
            print(f"  Strikes: {usuario.get('strikes', 0)}/3")
            print(f" Estado: {usuario.get('estadoCuenta', 'activo')}")
        else:
            print("\n Usuario no encontrado")
    
    except Exception as e:
        print(f"\n Error: {e}")
    
    pausar()


def actualizar_usuario_interactivo():
    mostrar_encabezado("ACTUALIZAR USUARIO")
    
    usuario_id = input("\n ID del usuario a actualizar: ").strip()
    
    try:
        usuario = buscar_usuario_id(usuario_id)
        
        if not usuario:
            print("\nUsuario no encontrado")
            pausar()
            return
        
        print(f"\n👤 Usuario actual: {usuario['nombre']} {usuario['apellido']}")
        print("\n💡 Deja en blanco para mantener el valor actual")
        
        nombre = input(f"\n Nuevo nombre [{usuario['nombre']}]: ").strip()
        apellido = input(f" Nuevo apellido [{usuario['apellido']}]: ").strip()
        
        datos = {}
        if nombre:
            datos["nombre"] = nombre
        if apellido:
            datos["apellido"] = apellido
        
        if datos:
            actualizado = actualizar_usuario(usuario_id, datos)
            
            if actualizado:
                print("\n Usuario actualizado correctamente")
            else:
                print("\n No se pudo actualizar el usuario")
        else:
            print("\n  No se realizaron cambios")
    
    except Exception as e:
        print(f"\n Error: {e}")
    
    pausar()


def eliminar_usuario_interactivo():
    """Elimina un usuario"""
    mostrar_encabezado("ELIMINAR USUARIO")
    
    usuario_id = input("\n ID del usuario a eliminar: ").strip()
    
    try:
        usuario = buscar_usuario_id(usuario_id)
        
        if not usuario:
            print("\n Usuario no encontrado")
            pausar()
            return
        
        print(f"\n Vas a eliminar al usuario:")
        print(f"{usuario['nombre']} {usuario['apellido']}")
        print(f"{usuario['correo']}")
        
        confirmacion = input("\n ¿Estás seguro? (S/N): ").strip().upper()
        
        if confirmacion == "S":
            eliminado = eliminar_usuario(usuario_id)
            
            if eliminado:
                print("\n Usuario eliminado correctamente")
            else:
                print("\n No se pudo eliminar el usuario")
        else:
            print("\n Operación cancelada")
    
    except Exception as e:
        print(f"\n Error: {e}")
    
    pausar()


def listar_usuarios():
    mostrar_encabezado("LISTA DE USUARIOS")
    
    try:
        usuarios = list(bd.usuarios.find({}).limit(50))
        
        if not usuarios:
            print("\n No hay usuarios en el sistema")
        else:
            print(f"\nTotal de usuarios: {len(usuarios)}\n")
            print(f"{'ID':<26} {'Nombre':<25} {'Correo':<30} {'Strikes':<10} {'Estado':<10}")
            print("-" * 101)
            
            for usuario in usuarios:
                id_str = str(usuario['_id'])[:24]
                nombre = f"{usuario['nombre']} {usuario['apellido']}"[:24]
                correo = usuario['correo'][:29]
                strikes = f"{usuario.get('strikes', 0)}/3"
                estado = usuario.get('estadoCuenta', 'activo')
                
                print(f"{id_str:<26} {nombre:<25} {correo:<30} {strikes:<10} {estado:<10}")
    
    except Exception as e:
        print(f"\n Error: {e}")
    
    pausar()