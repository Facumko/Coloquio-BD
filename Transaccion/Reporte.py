import sys
sys.path.append('..')
from datetime import datetime
from bson import ObjectId
from pymongo.errors import PyMongoError
from Conexion import bd, client

# ==========================================
# FUNCIONES AUXILIARES - CONSULTA
# ==========================================

def obtener_reportes_pendientes():
    """
    Obtiene todos los reportes pendientes de procesamiento.
    """
    reportes = list(bd.reportes.find(
        {"estado": "pendiente"}
    ).sort("createAt", 1))
    
    return reportes


def obtener_detalles_reporte(reporte_id):
    """
    Obtiene todos los detalles de un reporte para que el admin pueda revisarlo.
    
    Returns:
        dict: Información completa del reporte, comentario y usuarios involucrados
    """
    reporte = bd.reportes.find_one({"_id": ObjectId(reporte_id)})
    
    if not reporte:
        return None
    
    # Obtener el comentario
    comentario = bd.comentarios.find_one({"_id": reporte["comentarioId"]})
    
    # Obtener usuario reportado
    usuario_reportado = bd.usuarios.find_one({"_id": reporte["usuarioReportado"]})
    
    # Obtener usuario que reportó
    usuario_reportante = bd.usuarios.find_one({"_id": reporte["usuarioQueReporta"]})
    
    # Obtener contenido (publicación o evento)
    contenido = None
    if comentario:
        if comentario["tipoContenido"] == "publicacion":
            contenido = bd.publicaciones.find_one({"_id": comentario["contenidoId"]})
        elif comentario["tipoContenido"] == "evento":
            contenido = bd.eventos.find_one({"_id": comentario["contenidoId"]})
    
    return {
        "reporte": reporte,
        "comentario": comentario,
        "usuario_reportado": usuario_reportado,
        "usuario_reportante": usuario_reportante,
        "contenido": contenido
    }


def mostrar_reporte_detallado(reporte_id):
    """
    Muestra todos los detalles de un reporte de forma legible para revisión.
    """
    detalles = obtener_detalles_reporte(reporte_id)
    
    if not detalles:
        print("❌ Reporte no encontrado")
        return None
    
    print("\n" + "="*70)
    print("📋 DETALLES DEL REPORTE")
    print("="*70)
    
    # Información del reporte
    reporte = detalles["reporte"]
    print(f"\n🆔 ID del Reporte: {reporte['_id']}")
    print(f"🚨 Motivo: {reporte['motivo']}")
    print(f"📅 Fecha del reporte: {reporte.get('createAt', 'N/A')}")
    print(f"📊 Estado: {reporte['estado']}")
    
    # Información del comentario
    comentario = detalles["comentario"]
    if comentario:
        print(f"\n💬 COMENTARIO REPORTADO:")
        print(f"   📝 Texto: \"{comentario['texto']}\"")
        print(f"   📊 Total de reportes recibidos: {comentario.get('cantidadReportes', 0)}")
        print(f"   🗓️  Fecha del comentario: {comentario.get('createdAt', 'N/A')}")
        print(f"   📍 Tipo de contenido: {comentario['tipoContenido']}")
    else:
        print("\n⚠️  Comentario no encontrado (posiblemente eliminado)")
    
    # Información del usuario reportado
    usuario_reportado = detalles["usuario_reportado"]
    if usuario_reportado:
        print(f"\n👤 USUARIO REPORTADO:")
        print(f"   Nombre: {usuario_reportado['nombre']} {usuario_reportado['apellido']}")
        print(f"   Email: {usuario_reportado['correo']}")
        print(f"   ⚠️  Strikes actuales: {usuario_reportado.get('strikes', 0)}/3")
        print(f"   📊 Estado de cuenta: {usuario_reportado.get('estadoCuenta', 'activo')}")
    
    # Información del usuario que reportó
    usuario_reportante = detalles["usuario_reportante"]
    if usuario_reportante:
        print(f"\n🚩 REPORTADO POR:")
        print(f"   Nombre: {usuario_reportante['nombre']} {usuario_reportante['apellido']}")
        print(f"   Email: {usuario_reportante['correo']}")
    
    print("\n" + "="*70)
    
    return detalles


# ==========================================
# TRANSACCIÓN 1: ACEPTAR REPORTE
# ==========================================

def aceptar_reporte_y_sancionar(reporte_id, admin_id, dar_strike=True, eliminar_comentario=True):
    """
    TRANSACCIÓN: Acepta el reporte como válido y aplica sanciones.
    
    Pasos:
    1. Marcar reporte como resuelto
    2. (Opcional) Eliminar comentario si el admin lo decide
    3. (Opcional) Dar strike al usuario si el admin lo decide
    4. Si llega a 3 strikes → banear automáticamente
    5. Notificar al usuario reportado
    6. Notificar al usuario que reportó ✅ NUEVO
    7. Notificar a los admins
    
    Args:
        reporte_id: ID del reporte a procesar
        admin_id: ID del admin que toma la decisión
        dar_strike: Si se debe dar strike al usuario (default: True)
        eliminar_comentario: Si se debe eliminar el comentario (default: True)
    
    Returns:
        dict: Resultado de la operación
    """
    
    with client.start_session() as session:
        try:
            session.start_transaction()
            
            print("\n" + "="*70)
            print("✅ TRANSACCIÓN: ACEPTAR REPORTE Y SANCIONAR")
            print("="*70)
            
            # PASO 1: Validar y obtener datos
            print("\n📋 Validando reporte...")
            
            reporte = bd.reportes.find_one(
                {"_id": ObjectId(reporte_id)},
                session=session
            )
            
            if not reporte:
                raise ValueError("❌ Reporte no encontrado")
            
            if reporte["estado"] != "pendiente":
                raise ValueError("❌ El reporte ya fue procesado")
            
            comentario_id = reporte["comentarioId"]
            usuario_reportado_id = reporte["usuarioReportado"]
            usuario_reportante_id = reporte["usuarioQueReporta"]  # ✅ NUEVO
            motivo = reporte["motivo"]
            
            print(f"   ✅ Reporte válido")
            
            # Obtener comentario
            comentario = bd.comentarios.find_one(
                {"_id": ObjectId(comentario_id)},
                session=session
            )
            
            if not comentario and eliminar_comentario:
                raise ValueError("❌ Comentario no encontrado")
            
            # Obtener usuario
            usuario = bd.usuarios.find_one(
                {"_id": ObjectId(usuario_reportado_id)},
                session=session
            )
            
            if not usuario:
                raise ValueError("❌ Usuario reportado no encontrado")
            
            strikes_actuales = usuario.get("strikes", 0)
            
            # PASO 2: Marcar reporte como resuelto y aceptado
            print("\n📌 Marcando reporte como resuelto (ACEPTADO)...")
            
            bd.reportes.update_one(
                {"_id": ObjectId(reporte_id)},
                {
                    "$set": {
                        "estado": "resuelto",
                        "adminId": ObjectId(admin_id),
                        "comentarioEliminado": eliminar_comentario,
                        "strikeAplicado": dar_strike,
                        "updateAt": datetime.now()
                    }
                },
                session=session
            )
            
            print(f"   ✅ Reporte aceptado")
            
            # PASO 3: Eliminar comentario (si se decidió)
            comentario_eliminado = False
            if eliminar_comentario and comentario:
                print("\n🗑️  Eliminando comentario...")
                
                resultado = bd.comentarios.delete_one(
                    {"_id": ObjectId(comentario_id)},
                    session=session
                )
                
                if resultado.deleted_count > 0:
                    comentario_eliminado = True
                    print(f"   ✅ Comentario eliminado")
                else:
                    print(f"   ⚠️  No se pudo eliminar el comentario")
            else:
                print("\n📝 Comentario NO eliminado (decisión del admin)")
            
            # PASO 4: Dar strike (si se decidió)
            nuevos_strikes = strikes_actuales
            usuario_baneado = False
            
            if dar_strike:
                print("\n⚠️  Aplicando strike...")
                
                nuevos_strikes = strikes_actuales + 1
                
                if nuevos_strikes >= 3:
                    print(f"   🚫 Usuario alcanzó {nuevos_strikes} strikes - BANEANDO")
                    
                    bd.usuarios.update_one(
                        {"_id": ObjectId(usuario_reportado_id)},
                        {
                            "$set": {
                                "strikes": nuevos_strikes,
                                "estadoCuenta": "baneado",
                                "fechaBaneo": datetime.now(),
                                "updatedAt": datetime.now()
                            }
                        },
                        session=session
                    )
                    
                    bd.reportes.update_one(
                        {"_id": ObjectId(reporte_id)},
                        {"$set": {"usuarioBaneado": True}},
                        session=session
                    )
                    
                    usuario_baneado = True
                    print(f"   ✅ Usuario BANEADO")
                    
                else:
                    bd.usuarios.update_one(
                        {"_id": ObjectId(usuario_reportado_id)},
                        {
                            "$set": {
                                "strikes": nuevos_strikes,
                                "updatedAt": datetime.now()
                            }
                        },
                        session=session
                    )
                    print(f"   ✅ Strike aplicado ({nuevos_strikes}/3)")
            else:
                print("\n📝 NO se aplicó strike (decisión del admin)")
            
            # PASO 5: Notificar al usuario reportado
            print("\n🔔 Notificando al usuario reportado...")
            
            if usuario_baneado:
                mensaje_reportado = f"Tu cuenta ha sido BANEADA por acumular 3 strikes. Motivo: {motivo}"
                tipo_notif = "baneo"
            elif dar_strike:
                mensaje_reportado = f"Has recibido un STRIKE ({nuevos_strikes}/3). Motivo: {motivo}"
                if comentario_eliminado:
                    mensaje_reportado += " Tu comentario fue eliminado."
                tipo_notif = "strike_recibido"
            else:
                mensaje_reportado = f"Tu comentario fue revisado por moderación. Motivo del reporte: {motivo}"
                if comentario_eliminado:
                    mensaje_reportado += " El comentario fue eliminado."
                tipo_notif = "advertencia"
            
            bd.notificaciones.insert_one(
                {
                    "usuarioId": ObjectId(usuario_reportado_id),
                    "tipo": tipo_notif,
                    "mensaje": mensaje_reportado,
                    "leida": False,
                    "reporteId": ObjectId(reporte_id),
                    "createdAt": datetime.now(),
                    "expiraEn": datetime.now()
                },
                session=session
            )
            
            print(f"   ✅ Usuario reportado notificado")
            
            # ✅ PASO 5.5: NOTIFICAR AL USUARIO QUE REPORTÓ
            print("\n🔔 Notificando al usuario que reportó...")
            
            if usuario_baneado:
                mensaje_reportante = f"Tu reporte fue aceptado. El usuario fue BANEADO por acumular 3 strikes."
            elif dar_strike:
                mensaje_reportante = f"Tu reporte fue aceptado. Se aplicó un strike al usuario ({nuevos_strikes}/3)."
                if comentario_eliminado:
                    mensaje_reportante += " El comentario fue eliminado."
            else:
                mensaje_reportante = f"Tu reporte fue aceptado."
                if comentario_eliminado:
                    mensaje_reportante += " El comentario fue eliminado."
                else:
                    mensaje_reportante += " Se tomaron medidas."
            
            bd.notificaciones.insert_one(
                {
                    "usuarioId": ObjectId(usuario_reportante_id),
                    "tipo": "reporte_aceptado",
                    "mensaje": mensaje_reportante,
                    "leida": False,
                    "reporteId": ObjectId(reporte_id),
                    "createdAt": datetime.now(),
                    "expiraEn": datetime.now()
                },
                session=session
            )
            
            print(f"   ✅ Usuario reportante notificado")
            
            # PASO 6: Notificar a admins
            print("\n📢 Notificando a administradores...")
            
            admins = list(bd.usuarios.find({"roles": "Admin"}, session=session))
            
            admin_procesador = bd.usuarios.find_one({"_id": ObjectId(admin_id)}, session=session)
            nombre_admin = f"{admin_procesador['nombre']} {admin_procesador['apellido']}" if admin_procesador else "Admin"
            
            mensaje_admin = (
                f"{nombre_admin} ACEPTÓ un reporte. "
                f"Usuario: {usuario['nombre']} {usuario['apellido']}. "
            )
            
            if usuario_baneado:
                mensaje_admin += "USUARIO BANEADO."
            elif dar_strike:
                mensaje_admin += f"Strike aplicado ({nuevos_strikes}/3)."
            
            if comentario_eliminado:
                mensaje_admin += " Comentario eliminado."
            
            notificaciones = []
            for admin in admins:
                if str(admin["_id"]) != str(admin_id):
                    notificaciones.append({
                        "usuarioId": admin["_id"],
                        "tipo": "reporte_resuelto",
                        "mensaje": mensaje_admin,
                        "leida": False,
                        "reporteId": ObjectId(reporte_id),
                        "createdAt": datetime.now(),
                        "expiraEn": datetime.now()
                    })
            
            if notificaciones:
                bd.notificaciones.insert_many(notificaciones, session=session)
            
            print(f"   ✅ {len(notificaciones)} admins notificados")
            
            # COMMIT
            print("\n💾 Guardando cambios...")
            session.commit_transaction()
            
            print("\n" + "="*70)
            print("✅ TRANSACCIÓN COMPLETADA - REPORTE ACEPTADO")
            print("="*70)
            
            return {
                "exito": True,
                "accion": "aceptado",
                "comentario_eliminado": comentario_eliminado,
                "strike_aplicado": dar_strike,
                "strikes_totales": nuevos_strikes,
                "usuario_baneado": usuario_baneado,
                "mensaje": "Reporte aceptado y procesado correctamente"
            }
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            print("🔄 Haciendo ROLLBACK...")
            session.abort_transaction()
            
            return {
                "exito": False,
                "error": str(e),
                "mensaje": "La transacción falló, no se aplicaron cambios"
            }


# ==========================================
# TRANSACCIÓN 2: RECHAZAR REPORTE
# ==========================================

def rechazar_reporte(reporte_id, admin_id, motivo_rechazo="Reporte no válido"):
    """
    TRANSACCIÓN: Rechaza el reporte como inválido.
    
    Pasos:
    1. Marcar reporte como rechazado
    2. Notificar al usuario que reportó ✅ NUEVO
    3. Notificar a los admins
    4. No se aplican sanciones al usuario reportado
    
    Args:
        reporte_id: ID del reporte a rechazar
        admin_id: ID del admin que toma la decisión
        motivo_rechazo: Razón por la que se rechaza
    
    Returns:
        dict: Resultado de la operación
    """
    
    with client.start_session() as session:
        try:
            session.start_transaction()
            
            print("\n" + "="*70)
            print("❌ TRANSACCIÓN: RECHAZAR REPORTE")
            print("="*70)
            
            # Validar reporte
            print("\n📋 Validando reporte...")
            
            reporte = bd.reportes.find_one(
                {"_id": ObjectId(reporte_id)},
                session=session
            )
            
            if not reporte:
                raise ValueError("❌ Reporte no encontrado")
            
            if reporte["estado"] != "pendiente":
                raise ValueError("❌ El reporte ya fue procesado")
            
            usuario_reportante_id = reporte["usuarioQueReporta"]  # ✅ NUEVO
            
            print(f"   ✅ Reporte válido")
            
            # Marcar como rechazado
            print("\n📌 Marcando reporte como RECHAZADO...")
            
            bd.reportes.update_one(
                {"_id": ObjectId(reporte_id)},
                {
                    "$set": {
                        "estado": "rechazado",
                        "adminId": ObjectId(admin_id),
                        "motivoRechazo": motivo_rechazo,
                        "updateAt": datetime.now()
                    }
                },
                session=session
            )
            
            print(f"   ✅ Reporte rechazado")
            
            # ✅ NOTIFICAR AL USUARIO QUE REPORTÓ
            print("\n🔔 Notificando al usuario que reportó...")
            
            mensaje_reportante = f"Tu reporte fue rechazado. Motivo: {motivo_rechazo}"
            
            bd.notificaciones.insert_one(
                {
                    "usuarioId": ObjectId(usuario_reportante_id),
                    "tipo": "reporte_rechazado",
                    "mensaje": mensaje_reportante,
                    "leida": False,
                    "reporteId": ObjectId(reporte_id),
                    "createdAt": datetime.now(),
                    "expiraEn": datetime.now()
                },
                session=session
            )
            
            print(f"   ✅ Usuario reportante notificado")
            
            # Notificar a admins
            print("\n📢 Notificando a administradores...")
            
            admins = list(bd.usuarios.find({"roles": "Admin"}, session=session))
            admin_procesador = bd.usuarios.find_one({"_id": ObjectId(admin_id)}, session=session)
            nombre_admin = f"{admin_procesador['nombre']} {admin_procesador['apellido']}" if admin_procesador else "Admin"
            
            mensaje_admin = f"{nombre_admin} RECHAZÓ un reporte. Motivo: {motivo_rechazo}"
            
            notificaciones = []
            for admin in admins:
                if str(admin["_id"]) != str(admin_id):
                    notificaciones.append({
                        "usuarioId": admin["_id"],
                        "tipo": "reporte_rechazado",
                        "mensaje": mensaje_admin,
                        "leida": False,
                        "reporteId": ObjectId(reporte_id),
                        "createdAt": datetime.now(),
                        "expiraEn": datetime.now()
                    })
            
            if notificaciones:
                bd.notificaciones.insert_many(notificaciones, session=session)
            
            print(f"   ✅ {len(notificaciones)} admins notificados")
            
            # COMMIT
            print("\n💾 Guardando cambios...")
            session.commit_transaction()
            
            print("\n" + "="*70)
            print("✅ TRANSACCIÓN COMPLETADA - REPORTE RECHAZADO")
            print("="*70)
            
            return {
                "exito": True,
                "accion": "rechazado",
                "motivo": motivo_rechazo,
                "mensaje": "Reporte rechazado correctamente"
            }
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            print("🔄 Haciendo ROLLBACK...")
            session.abort_transaction()
            
            return {
                "exito": False,
                "error": str(e),
                "mensaje": "La transacción falló"
            }


# ==========================================
# EJEMPLO DE USO
# ==========================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 PRUEBA DEL SISTEMA DE MODERACIÓN")
    print("="*70)
    
    # Obtener reportes pendientes
    reportes = obtener_reportes_pendientes()
    
    if not reportes:
        print("\n⚠️  No hay reportes pendientes")
        print("💡 Ejecuta s.py para generar datos de prueba")
    else:
        print(f"\n📋 Hay {len(reportes)} reportes pendientes")
        
        # Mostrar el primer reporte
        reporte_id = str(reportes[0]["_id"])
        mostrar_reporte_detallado(reporte_id)
        
        # Obtener un admin
        admin = bd.usuarios.find_one({"roles": "Admin"})
        
        if admin:
            admin_id = str(admin["_id"])
            
            print("\n🎯 Opciones disponibles:")
            print("1. Aceptar reporte (eliminar comentario + dar strike)")
            print("2. Aceptar reporte (solo eliminar comentario)")
            print("3. Aceptar reporte (solo dar strike)")
            print("4. Rechazar reporte")
            
            # Para prueba automática, acepta el reporte
            print("\n🧪 EJECUTANDO PRUEBA: Aceptar y sancionar...")
            resultado = aceptar_reporte_y_sancionar(
                reporte_id=reporte_id,
                admin_id=admin_id,
                dar_strike=True,
                eliminar_comentario=True
            )
            
            if resultado["exito"]:
                print("\n✅ PRUEBA EXITOSA")
            else:
                print(f"\n❌ PRUEBA FALLIDA: {resultado['error']}")
        else:
            print("\n⚠️  No hay admins en la BD")