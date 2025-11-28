"""
Funciones auxiliares para los menús del sistema
"""
import sys
sys.path.append('..')
import os
from Conexion import bd


def limpiar_pantalla():
    """Limpia la pantalla (multiplataforma)"""
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
    
    Returns:
        dict: Usuario admin o None si no existe
    """
    admin = bd.usuarios.find_one({"roles": "Admin"})
    if not admin:
        print("\n⚠️  No hay usuarios admin en el sistema")
        print("💡 Ejecuta 'python s.py' para generar datos de prueba")
        return None
    return admin


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