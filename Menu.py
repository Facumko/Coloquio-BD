import sys
sys.path.append('.')
from bson import ObjectId
from datetime import datetime

# Importar conexión
from Conexion import bd

# Importar CRUDs
from Crud.CrudUsuario import (
    registrar_usuario, buscar_usuario_id, buscar_usuario_correo,
    actualizar_usuario, eliminar_usuario, dar_strike, 
    banear_usuario, desbanear_usuario
)
from Crud.CrudComercio import (
    registrar_comercio, buscar_comercio_id, actualizar_comercio,
    eliminar_comercio
)
from Crud.CrudPublicacion import (
    crear_publicacion_db, obtener_publicacion_por_id,
    obtener_publicaciones_por_comercio, actualizar_publicacion,
    eliminar_publicacion
)
from Crud.CrudComentario import (
    crear_comentario_db, obtener_comentario_por_id,
    obtener_comentarios_por_contenido, actualizar_comentario,
    eliminar_comentario
)

# Importar funciones de transacción
from Transaccion.Reporte import (
    obtener_reportes_pendientes, obtener_detalles_reporte,
    mostrar_reporte_detallado, aceptar_reporte_y_sancionar,
    rechazar_reporte
)

# Importar estructuras
from Colecciones.Comercio import crear_direccion

# ==========================================
# UTILIDADES
# ==========================================

def limpiar_pantalla():
    """Limpia la pantalla (multiplataforma)"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def pausar():
    """Pausa la ejecución hasta que el usuario presione Enter"""
    input("\n⏸️  Presiona ENTER para continuar...")


def mostrar_encabezado(titulo):
    """Muestra un encabezado decorado"""
    print("\n" + "="*70)
    print(f"  {titulo}")
    print("="*70)


def obtener_admin():
    """
    Obtiene un usuario admin para las operaciones que lo requieren.
    En un sistema real, esto vendría del login.
    """
    admin = bd.usuarios.find_one({"roles": "Admin"})
    if not admin:
        print("\n⚠️  No hay usuarios admin en el sistema")
        print("💡 Ejecuta s.py para generar datos de prueba")
        return None
    return admin


# ==========================================
# MÓDULO 1: CRUD DE USUARIOS
# ==========================================

def menu_crud_usuarios():
    """Submenú para operaciones CRUD de usuarios"""
    while True:
        limpiar_pantalla()
        mostrar_encabezado("CRUD DE USUARIOS")
        
        print("\n1. 📝 Crear nuevo usuario")
        print("2. 🔍 Buscar usuario por ID")
        print("3. 📧 Buscar usuario por correo")
        print("4. ✏️  Actualizar usuario")
        print("5. 🗑️  Eliminar usuario")
        print("6. 📊 Listar todos los usuarios")
        print("0. ⬅️  Volver al menú principal")
        
        opcion = input("\n👉 Selecciona una opción: ").strip()
        
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
            print("❌ Opción inválida")
            pausar()


def crear_usuario_interactivo():
    """Crea un nuevo usuario de forma interactiva"""
    mostrar_encabezado("CREAR NUEVO USUARIO")
    
    nombre = input("\n📝 Nombre: ").strip()
    apellido = input("📝 Apellido: ").strip()
    correo = input("📧 Correo: ").strip()
    contraseña = input("🔒 Contraseña: ").strip()
    
    print("\n🎭 Roles disponibles:")
    print("1. Usuario (predeterminado)")
    print("2. Usuario + Propietario")
    print("3. Usuario + Admin")
    
    rol_opcion = input("\n👉 Selecciona roles (1-3): ").strip()
    
    roles = ["Usuario"]
    if rol_opcion == "2":
        roles.append("Propietario")
    elif rol_opcion == "3":
        roles.append("Admin")
    
    try:
        usuario_id = registrar_usuario(nombre, apellido, correo, contraseña, roles)
        
        if usuario_id:
            print(f"\n✅ Usuario creado exitosamente!")
            print(f"🆔 ID: {usuario_id}")
            print(f"👤 Nombre: {nombre} {apellido}")
            print(f"📧 Correo: {correo}")
            print(f"🎭 Roles: {', '.join(roles)}")
        else:
            print("\n❌ Error: El correo ya está registrado")
    
    except Exception as e:
        print(f"\n❌ Error al crear usuario: {e}")
    
    pausar()


def buscar_usuario_por_id_interactivo():
    """Busca un usuario por su ID"""
    mostrar_encabezado("BUSCAR USUARIO POR ID")
    
    usuario_id = input("\n🆔 Ingresa el ID del usuario: ").strip()
    
    try:
        usuario = buscar_usuario_id(usuario_id)
        
        if usuario:
            print("\n✅ Usuario encontrado:")
            print(f"\n🆔 ID: {usuario['_id']}")
            print(f"👤 Nombre: {usuario['nombre']} {usuario['apellido']}")
            print(f"📧 Correo: {usuario['correo']}")
            print(f"🎭 Roles: {', '.join(usuario.get('roles', []))}")
            print(f"⚠️  Strikes: {usuario.get('strikes', 0)}/3")
            print(f"📊 Estado: {usuario.get('estadoCuenta', 'activo')}")
            print(f"📅 Creado: {usuario.get('createdAt', 'N/A')}")
        else:
            print("\n❌ Usuario no encontrado")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    pausar()


def buscar_usuario_por_correo_interactivo():
    """Busca un usuario por su correo"""
    mostrar_encabezado("BUSCAR USUARIO POR CORREO")
    
    correo = input("\n📧 Ingresa el correo: ").strip()
    
    try:
        usuario = buscar_usuario_correo(correo)
        
        if usuario:
            print("\n✅ Usuario encontrado:")
            print(f"\n🆔 ID: {usuario['_id']}")
            print(f"👤 Nombre: {usuario['nombre']} {usuario['apellido']}")
            print(f"📧 Correo: {usuario['correo']}")
            print(f"🎭 Roles: {', '.join(usuario.get('roles', []))}")
            print(f"⚠️  Strikes: {usuario.get('strikes', 0)}/3")
            print(f"📊 Estado: {usuario.get('estadoCuenta', 'activo')}")
        else:
            print("\n❌ Usuario no encontrado")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    pausar()


def actualizar_usuario_interactivo():
    """Actualiza un usuario existente"""
    mostrar_encabezado("ACTUALIZAR USUARIO")
    
    usuario_id = input("\n🆔 ID del usuario a actualizar: ").strip()
    
    try:
        usuario = buscar_usuario_id(usuario_id)
        
        if not usuario:
            print("\n❌ Usuario no encontrado")
            pausar()
            return
        
        print(f"\n👤 Usuario actual: {usuario['nombre']} {usuario['apellido']}")
        print("\n💡 Deja en blanco para mantener el valor actual")
        
        nombre = input(f"\n📝 Nuevo nombre [{usuario['nombre']}]: ").strip()
        apellido = input(f"📝 Nuevo apellido [{usuario['apellido']}]: ").strip()
        
        datos = {}
        if nombre:
            datos["nombre"] = nombre
        if apellido:
            datos["apellido"] = apellido
        
        if datos:
            actualizado = actualizar_usuario(usuario_id, datos)
            
            if actualizado:
                print("\n✅ Usuario actualizado correctamente")
            else:
                print("\n❌ No se pudo actualizar el usuario")
        else:
            print("\n⚠️  No se realizaron cambios")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    pausar()


def eliminar_usuario_interactivo():
    """Elimina un usuario"""
    mostrar_encabezado("ELIMINAR USUARIO")
    
    usuario_id = input("\n🆔 ID del usuario a eliminar: ").strip()
    
    try:
        usuario = buscar_usuario_id(usuario_id)
        
        if not usuario:
            print("\n❌ Usuario no encontrado")
            pausar()
            return
        
        print(f"\n⚠️  Vas a eliminar al usuario:")
        print(f"👤 {usuario['nombre']} {usuario['apellido']}")
        print(f"📧 {usuario['correo']}")
        
        confirmacion = input("\n❓ ¿Estás seguro? (S/N): ").strip().upper()
        
        if confirmacion == "S":
            eliminado = eliminar_usuario(usuario_id)
            
            if eliminado:
                print("\n✅ Usuario eliminado correctamente")
            else:
                print("\n❌ No se pudo eliminar el usuario")
        else:
            print("\n🚫 Operación cancelada")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    pausar()


def listar_usuarios():
    """Lista todos los usuarios del sistema"""
    mostrar_encabezado("LISTA DE USUARIOS")
    
    try:
        usuarios = list(bd.usuarios.find({}).limit(50))
        
        if not usuarios:
            print("\n⚠️  No hay usuarios en el sistema")
        else:
            print(f"\n📊 Total de usuarios: {len(usuarios)}\n")
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
        print(f"\n❌ Error: {e}")
    
    pausar()


# ==========================================
# MÓDULO 2: SISTEMA DE MODERACIÓN
# ==========================================

def menu_moderacion():
    """Submenú para el sistema de moderación de reportes"""
    
    admin = obtener_admin()
    if not admin:
        pausar()
        return
    
    admin_id = str(admin["_id"])
    
    while True:
        limpiar_pantalla()
        mostrar_encabezado("SISTEMA DE MODERACIÓN DE REPORTES")
        print(f"👤 Admin: {admin['nombre']} {admin['apellido']}")
        
        print("\n1. 📋 Ver reportes pendientes")
        print("2. 🔍 Revisar reporte específico")
        print("3. ✅ Procesar reporte (Aceptar)")
        print("4. ❌ Rechazar reporte")
        print("5. 📊 Estadísticas de moderación")
        print("0. ⬅️  Volver al menú principal")
        
        opcion = input("\n👉 Selecciona una opción: ").strip()
        
        if opcion == "1":
            listar_reportes_pendientes()
        elif opcion == "2":
            revisar_reporte_especifico()
        elif opcion == "3":
            procesar_reporte_aceptar(admin_id)
        elif opcion == "4":
            procesar_reporte_rechazar(admin_id)
        elif opcion == "5":
            mostrar_estadisticas_moderacion()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida")
            pausar()


def listar_reportes_pendientes():
    """Lista todos los reportes pendientes"""
    mostrar_encabezado("REPORTES PENDIENTES")
    
    try:
        reportes = obtener_reportes_pendientes()
        
        if not reportes:
            print("\n✅ No hay reportes pendientes")
        else:
            print(f"\n📊 Total de reportes pendientes: {len(reportes)}\n")
            
            for i, reporte in enumerate(reportes, 1):
                print(f"\n{'='*70}")
                print(f"📋 REPORTE #{i}")
                print(f"{'='*70}")
                print(f"🆔 ID: {reporte['_id']}")
                print(f"🚨 Motivo: {reporte['motivo']}")
                print(f"📅 Fecha: {reporte.get('createAt', 'N/A')}")
                
                # Obtener comentario
                comentario = bd.comentarios.find_one({"_id": reporte["comentarioId"]})
                if comentario:
                    print(f"💬 Comentario: \"{comentario['texto'][:60]}...\"")
                    print(f"📊 Reportes recibidos: {comentario.get('cantidadReportes', 0)}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    pausar()


def revisar_reporte_especifico():
    """Muestra los detalles completos de un reporte"""
    mostrar_encabezado("REVISAR REPORTE")
    
    reporte_id = input("\n🆔 ID del reporte a revisar: ").strip()
    
    try:
        mostrar_reporte_detallado(reporte_id)
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    pausar()


def procesar_reporte_aceptar(admin_id):
    """Procesa un reporte aceptándolo (con opciones)"""
    mostrar_encabezado("ACEPTAR Y PROCESAR REPORTE")
    
    reporte_id = input("\n🆔 ID del reporte: ").strip()
    
    try:
        # Mostrar detalles primero
        detalles = obtener_detalles_reporte(reporte_id)
        
        if not detalles:
            print("\n❌ Reporte no encontrado")
            pausar()
            return
        
        print("\n" + "="*70)
        print(f"💬 Comentario: \"{detalles['comentario']['texto']}\"")
        print(f"👤 Usuario reportado: {detalles['usuario_reportado']['nombre']} {detalles['usuario_reportado']['apellido']}")
        print(f"⚠️  Strikes actuales: {detalles['usuario_reportado'].get('strikes', 0)}/3")
        print("="*70)
        
        # Preguntar acciones
        print("\n🎯 ¿Qué acciones deseas realizar?")
        
        eliminar = input("\n🗑️  ¿Eliminar el comentario? (S/N): ").strip().upper() == "S"
        dar_strike = input("⚠️  ¿Dar strike al usuario? (S/N): ").strip().upper() == "S"
        
        confirmacion = input("\n✅ ¿Confirmar y procesar? (S/N): ").strip().upper()
        
        if confirmacion == "S":
            resultado = aceptar_reporte_y_sancionar(
                reporte_id=reporte_id,
                admin_id=admin_id,
                dar_strike=dar_strike,
                eliminar_comentario=eliminar
            )
            
            if resultado["exito"]:
                print("\n" + "="*70)
                print("✅ REPORTE PROCESADO EXITOSAMENTE")
                print("="*70)
                print(f"🗑️  Comentario eliminado: {'SÍ' if resultado['comentario_eliminado'] else 'NO'}")
                print(f"⚠️  Strike aplicado: {'SÍ' if resultado['strike_aplicado'] else 'NO'}")
                if resultado.get('usuario_baneado'):
                    print(f"🚫 Usuario BANEADO (llegó a 3 strikes)")
                print("="*70)
            else:
                print(f"\n❌ Error: {resultado.get('error', 'Desconocido')}")
        else:
            print("\n🚫 Operación cancelada")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    pausar()


def procesar_reporte_rechazar(admin_id):
    """Rechaza un reporte como inválido"""
    mostrar_encabezado("RECHAZAR REPORTE")
    
    reporte_id = input("\n🆔 ID del reporte: ").strip()
    
    try:
        # Mostrar detalles
        detalles = obtener_detalles_reporte(reporte_id)
        
        if not detalles:
            print("\n❌ Reporte no encontrado")
            pausar()
            return
        
        print("\n" + "="*70)
        print(f"💬 Comentario: \"{detalles['comentario']['texto']}\"")
        print(f"🚨 Motivo del reporte: {detalles['reporte']['motivo']}")
        print("="*70)
        
        motivo_rechazo = input("\n📝 Motivo del rechazo: ").strip()
        
        if not motivo_rechazo:
            motivo_rechazo = "Reporte no válido"
        
        confirmacion = input("\n❌ ¿Confirmar rechazo? (S/N): ").strip().upper()
        
        if confirmacion == "S":
            resultado = rechazar_reporte(reporte_id, admin_id, motivo_rechazo)
            
            if resultado["exito"]:
                print("\n✅ Reporte rechazado correctamente")
            else:
                print(f"\n❌ Error: {resultado.get('error', 'Desconocido')}")
        else:
            print("\n🚫 Operación cancelada")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    pausar()


def mostrar_estadisticas_moderacion():
    """Muestra estadísticas del sistema de moderación"""
    mostrar_encabezado("ESTADÍSTICAS DE MODERACIÓN")
    
    try:
        total_reportes = bd.reportes.count_documents({})
        reportes_pendientes = bd.reportes.count_documents({"estado": "pendiente"})
        reportes_resueltos = bd.reportes.count_documents({"estado": "resuelto"})
        reportes_rechazados = bd.reportes.count_documents({"estado": "rechazado"})
        
        usuarios_baneados = bd.usuarios.count_documents({"estadoCuenta": "baneado"})
        comentarios_reportados = bd.comentarios.count_documents({"cantidadReportes": {"$gte": 1}})
        
        print("\n📊 ESTADÍSTICAS GENERALES:")
        print(f"\n📋 Reportes totales: {total_reportes}")
        print(f"⏳ Reportes pendientes: {reportes_pendientes}")
        print(f"✅ Reportes resueltos: {reportes_resueltos}")
        print(f"❌ Reportes rechazados: {reportes_rechazados}")
        print(f"\n🚫 Usuarios baneados: {usuarios_baneados}")
        print(f"💬 Comentarios reportados: {comentarios_reportados}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    pausar()


# ==========================================
# MENÚ PRINCIPAL
# ==========================================

def menu_principal():
    """Menú principal del sistema"""
    while True:
        limpiar_pantalla()
        mostrar_encabezado("🏪 SISTEMA DONDEQUE DA - MONGODB")
        
        print("\n📋 MÓDULOS DISPONIBLES:\n")
        print("1. 👥 CRUD de Usuarios")
        print("2. 🛡️  Sistema de Moderación (Transacciones)")
        print("3. 📊 Informes y Estadísticas")
        print("4. 🔧 Utilidades")
        print("0. 🚪 Salir")
        
        opcion = input("\n👉 Selecciona un módulo: ").strip()
        
        if opcion == "1":
            menu_crud_usuarios()
        elif opcion == "2":
            menu_moderacion()
        elif opcion == "3":
            print("\n⚠️  Módulo de informes en desarrollo...")
            pausar()
        elif opcion == "4":
            menu_utilidades()
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n❌ Opción inválida")
            pausar()


def menu_utilidades():
    """Menú de utilidades del sistema"""
    while True:
        limpiar_pantalla()
        mostrar_encabezado("UTILIDADES DEL SISTEMA")
        
        print("\n1. 🔄 Cargar datos de prueba (s.py)")
        print("2. 📊 Ver estadísticas generales")
        print("3. 🗑️  Limpiar base de datos")
        print("0. ⬅️  Volver")
        
        opcion = input("\n👉 Selecciona una opción: ").strip()
        
        if opcion == "1":
            print("\n💡 Para cargar datos ejecuta: python s.py")
            pausar()
        elif opcion == "2":
            mostrar_estadisticas_generales()
        elif opcion == "3":
            limpiar_bd_confirmacion()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida")
            pausar()


def mostrar_estadisticas_generales():
    """Muestra estadísticas generales del sistema"""
    mostrar_encabezado("ESTADÍSTICAS GENERALES")
    
    try:
        print("\n📊 DATOS EN EL SISTEMA:\n")
        print(f"👥 Usuarios: {bd.usuarios.count_documents({})}")
        print(f"   - Admins: {bd.usuarios.count_documents({'roles': 'Admin'})}")
        print(f"   - Propietarios: {bd.usuarios.count_documents({'roles': 'Propietario'})}")
        print(f"   - Baneados: {bd.usuarios.count_documents({'estadoCuenta': 'baneado'})}")
        
        print(f"\n🏪 Comercios: {bd.comercios.count_documents({})}")
        print(f"📝 Publicaciones: {bd.publicaciones.count_documents({})}")
        print(f"🎉 Eventos: {bd.eventos.count_documents({})}")
        print(f"💬 Comentarios: {bd.comentarios.count_documents({})}")
        
        print(f"\n🚨 Reportes: {bd.reportes.count_documents({})}")
        print(f"   - Pendientes: {bd.reportes.count_documents({'estado': 'pendiente'})}")
        print(f"   - Resueltos: {bd.reportes.count_documents({'estado': 'resuelto'})}")
        
        print(f"\n🔔 Notificaciones: {bd.notificaciones.count_documents({})}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    pausar()


def limpiar_bd_confirmacion():
    """Limpia la base de datos con confirmación"""
    mostrar_encabezado("LIMPIAR BASE DE DATOS")
    
    print("\n⚠️  ¡ADVERTENCIA!")
    print("Esta acción eliminará TODOS los datos del sistema.")
    print("Esta operación NO se puede deshacer.")
    
    confirmacion1 = input("\n¿Estás seguro? (SI/NO): ").strip().upper()
    
    if confirmacion1 == "SI":
        confirmacion2 = input("Escribe 'ELIMINAR TODO' para confirmar: ").strip()
        
        if confirmacion2 == "ELIMINAR TODO":
            try:
                bd.usuarios.delete_many({})
                bd.comercios.delete_many({})
                bd.publicaciones.delete_many({})
                bd.eventos.delete_many({})
                bd.comentarios.delete_many({})
                bd.reportes.delete_many({})
                bd.notificaciones.delete_many({})
                
                print("\n✅ Base de datos limpiada correctamente")
            except Exception as e:
                print(f"\n❌ Error: {e}")
        else:
            print("\n🚫 Operación cancelada")
    else:
        print("\n🚫 Operación cancelada")
    
    pausar()


# ==========================================
# PUNTO DE ENTRADA
# ==========================================

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()