
import sys
sys.path.append('..')

from Utilidades import limpiar_pantalla, pausar, mostrar_encabezado, menu_utilidades
from MenuUsuarios import menu_crud_usuarios
from MenuModeracion import menu_moderacion
from MenuNotificaciones import menu_ver_notificaciones
def menu_principal():
    """Menú principal del sistema"""
    while True:
        limpiar_pantalla()
        mostrar_encabezado("🏪 SISTEMA DONDEQUEDA - MONGODB")
        
        print("\n MÓDULOS DISPONIBLES:\n")
        print("1.  CRUD de Usuarios")
        print("2.  Sistema de Moderación (Transacciones)")
        print("3.  Ver Notificaciones de Usuarios")
        print("4.  Informes y Estadísticas")
        print("5.  Utilidades")
        print("0.  Salir")
        
        opcion = input("\n👉 Selecciona un módulo: ").strip()
        
        if opcion == "1":
            menu_crud_usuarios()
        elif opcion == "2":
            menu_moderacion()
        elif opcion == "3":
            menu_ver_notificaciones()
        elif opcion == "4":
            print("\n  Módulo en desarrollo...")
            pausar()
        elif opcion == "5":
            menu_utilidades()
        elif opcion == "0":
            print("\n ¡Hasta luego!")
            break
        else:
            print("\n Opción inválida")
            pausar()