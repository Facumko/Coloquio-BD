import sys
sys.path.append('..')
from Conexion import bd
from Transaccion.Reporte import (
    obtener_reportes_pendientes, obtener_detalles_reporte,
    mostrar_reporte_detallado, aceptar_reporte_y_sancionar, rechazar_reporte
)
from Utilidades import limpiar_pantalla, pausar, mostrar_encabezado, obtener_admin

def menu_moderacion():
    admin = obtener_admin()
    if not admin:
        pausar()
        return
    
    admin_id = str(admin["_id"])
    
    while True:
        limpiar_pantalla()
        mostrar_encabezado("SISTEMA DE MODERACIÓN DE REPORTES")
        print(f" Admin: {admin['nombre']} {admin['apellido']}")
        
        print("\n1.  Ver reportes pendientes")
        print("2.  Revisar reporte específico")
        print("3. Procesar reporte (Aceptar)")
        print("4.  Rechazar reporte")
        print("5. Estadísticas de moderación")
        print("0. Volver")
        
        opcion = input("Selecciona: ").strip()
        
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
            print("Opción inválida")
            pausar()

def listar_reportes_pendientes():
    mostrar_encabezado("REPORTES PENDIENTES")
    try:
        reportes = obtener_reportes_pendientes()
        if not reportes:
            print("No hay reportes pendientes")
        else:
            print(f"Total: {len(reportes)}\n")
            for i, reporte in enumerate(reportes, 1):
                print(f"\n{'='*70}\n REPORTE #{i}\n{'='*70}")
                print(f" ID: {reporte['_id']}")
                print(f"Motivo: {reporte['motivo']}")
                print(f"Fecha: {reporte.get('createAt', 'N/A')}")
                comentario = bd.comentarios.find_one({"_id": reporte["comentarioId"]})
                if comentario:
                    print(f"Comentario: \"{comentario['texto'][:60]}...\"")
                    print(f"Reportes: {comentario.get('cantidadReportes', 0)}")
    except Exception as e:
        print(f"\n Error: {e}")
    pausar()

def revisar_reporte_especifico():
    mostrar_encabezado("REVISAR REPORTE")
    reporte_id = input("\nID del reporte: ").strip()
    try:
        mostrar_reporte_detallado(reporte_id)
    except Exception as e:
        print(f"\n Error: {e}")
    pausar()

def procesar_reporte_aceptar(admin_id):
    mostrar_encabezado("ACEPTAR Y PROCESAR REPORTE")
    reporte_id = input("\nID del reporte: ").strip()
    try:
        detalles = obtener_detalles_reporte(reporte_id)
        if not detalles:
            print("\nReporte no encontrado")
            pausar()
            return
        
        print(f"\n{'='*70}")
        print(f"Comentario: \"{detalles['comentario']['texto']}\"")
        print(f"Usuario: {detalles['usuario_reportado']['nombre']} {detalles['usuario_reportado']['apellido']}")
        print(f"Strikes actuales: {detalles['usuario_reportado'].get('strikes', 0)}/3")
        print(f"{'='*70}")
        
        eliminar = input("\n¿Eliminar comentario? (S/N): ").strip().upper() == "S"
        dar_strike = input("¿Dar strike? (S/N): ").strip().upper() == "S"
        confirmacion = input("\n ¿Confirmar?s (S/N): ").strip().upper()
        
        if confirmacion == "S":
            resultado = aceptar_reporte_y_sancionar(reporte_id, admin_id, dar_strike, eliminar)
            if resultado["exito"]:
                print(f"\n{'='*70}\n REPORTE PROCESADO\n{'='*70}")
                print(f"Comentario eliminado: {'SÍ' if resultado['comentario_eliminado'] else 'NO'}")
                print(f"Strike aplicado: {'SÍ' if resultado['strike_aplicado'] else 'NO'}")
                if resultado.get('usuario_baneado'):
                    print(f"Usuario BANEADO")
                print(f"{'='*70}")
            else:
                print(f"\nError: {resultado.get('error')}")
        else:
            print("\n Cancelado")
    except Exception as e:
        print(f"\n Error: {e}")
    pausar()

def procesar_reporte_rechazar(admin_id):
    mostrar_encabezado("RECHAZAR REPORTE")
    reporte_id = input("\n ID del reporte: ").strip()
    try:
        detalles = obtener_detalles_reporte(reporte_id)
        if not detalles:
            print("\n Reporte no encontrado")
            pausar()
            return
        
        print(f"\n{'='*70}")
        print(f"Comentario: \"{detalles['comentario']['texto']}\"")
        print(f"Motivo: {detalles['reporte']['motivo']}")
        print(f"{'='*70}")
        
        motivo_rechazo = input("\n Motivo del rechazo: ").strip()
        if not motivo_rechazo:
            motivo_rechazo = "Reporte no válido"
        
        confirmacion = input("\n ¿Confirmar? (S/N): ").strip().upper()
        if confirmacion == "S":
            resultado = rechazar_reporte(reporte_id, admin_id, motivo_rechazo)
            if resultado["exito"]:
                print("\n  Reporte rechazado")
            else:
                print(f"\n Error: {resultado.get('error')}")
        else:
            print("\n Cancelado")
    except Exception as e:
        print(f"\n Error: {e}")
    pausar()

def mostrar_estadisticas_moderacion():
    mostrar_encabezado("ESTADÍSTICAS DE MODERACIÓN")
    try:
        print("\nESTADÍSTICAS:")
        print(f"\n Reportes totales: {bd.reportes.count_documents({})}")
        print(f" Pendientes: {bd.reportes.count_documents({'estado': 'pendiente'})}")
        print(f" Resueltos: {bd.reportes.count_documents({'estado': 'resuelto'})}")
        print(f" Rechazados: {bd.reportes.count_documents({'estado': 'rechazado'})}")
        print(f"\n Usuarios baneados: {bd.usuarios.count_documents({'estadoCuenta': 'baneado'})}")
        print(f" Comentarios reportados: {bd.comentarios.count_documents({'cantidadReportes': {'$gte': 1}})}")
    except Exception as e:
        print(f"\n Error: {e}")
    pausar()