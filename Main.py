import sys
sys.path.append('.')
sys.path.append('./Menu')

from MenuPrincipal import menu_principal

if __name__ == "__main__":
    try:
        print("BIENVENIDO AL SISTEMA DONDEQUEDA")
        menu_principal()
        
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario")
        print("¡Hasta luego!")
        
    except Exception as e:
        print(f"\n Error inesperado: {e}")
        import traceback
        traceback.print_exc()