
import sys

# Añadir la carpeta Menu al path
sys.path.append('.')
sys.path.append('./Menu')

# Importar el menú principal
from MenuPrincipal import menu_principal

if __name__ == "__main__":
    try:
        print("\n" + "="*70)
        print("🏪 BIENVENIDO AL SISTEMA DONDEQUEDA")
        print("="*70)
        print("\n💡 Sistema de gestión de comercios con MongoDB")
        print("📊 Versión 1.0 - Coloquio Base de Datos II\n")
        
        # Ejecutar menú principal
        menu_principal()
        
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido por el usuario")
        print("¡Hasta luego!")
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()