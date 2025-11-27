import sys
sys.path.append('.')
from faker import Faker
from datetime import datetime, timedelta
import random
from bson import ObjectId

# Importar conexión
from Conexion import bd

# Importar CRUDs
from Crud.CrudUsuario import registrar_usuario
from Crud.CrudComercio import registrar_comercio
from Crud.CrudPublicacion import crear_publicacion_db
from Crud.CrudComentario import crear_comentario_db
from Crud.CrudReporte import crear_reporte_db
from Crud.CrudNotificacion import crear_notificacion_db

# Importar funciones de creación de estructuras
from Colecciones.Comercio import crear_direccion

# Configurar Faker en español
fake = Faker('es_AR')  # Configuración para Argentina

# ==========================================
# LIMPIAR BASE DE DATOS
# ==========================================

def limpiar_base_datos():
    """Elimina todas las colecciones para empezar desde cero."""
    print("🗑️  Limpiando base de datos...")
    bd.usuarios.delete_many({})
    bd.comercios.delete_many({})
    bd.publicaciones.delete_many({})
    bd.comentarios.delete_many({})
    bd.reportes.delete_many({})
    bd.notificaciones.delete_many({})
    print("✅ Base de datos limpiada")


# ==========================================
# GENERAR USUARIOS
# ==========================================

def generar_usuarios(cantidad=20):
    """Genera usuarios aleatorios incluyendo admins."""
    print(f"👥 Generando {cantidad} usuarios...")
    usuarios_ids = []
    admins_ids = []
    
    # Crear 3 usuarios admin
    for i in range(3):
        usuario_id = registrar_usuario(
            nombre=fake.first_name(),
            apellido=fake.last_name(),
            correo=f"admin{i+1}@test.com",
            contraseña=fake.password(),
            roles=["Admin"]
        )
        usuarios_ids.append(usuario_id)
        admins_ids.append(usuario_id)
        print(f"   ✅ Admin creado: admin{i+1}@test.com")
    
    # Crear usuarios normales
    for i in range(cantidad - 3):
        roles = ["Usuario"]
        # Algunos usuarios serán dueños de comercios
        if random.random() < 0.3:  # 30% de probabilidad
            roles.append("Propietario")
        
        usuario_id = registrar_usuario(
            nombre=fake.first_name(),
            apellido=fake.last_name(),
            correo=fake.email(),
            contraseña=fake.password(),
            roles=roles
        )
        usuarios_ids.append(usuario_id)
    
    print(f"✅ {cantidad} usuarios generados ({len(admins_ids)} admins)")
    return usuarios_ids, admins_ids


# ==========================================
# GENERAR COMERCIOS
# ==========================================

def generar_comercios(propietarios_ids, cantidad=10):
    """Genera comercios aleatorios."""
    print(f"🏪 Generando {cantidad} comercios...")
    comercios_ids = []
    
    categorias = [
        "Gastronomía", "Salud y Bienestar", "Educación", 
        "Tecnología", "Moda", "Hogar y Decoración",
        "Entretenimiento", "Servicios Profesionales"
    ]
    
    for i in range(cantidad):
        direccion = crear_direccion(
            calle=fake.street_name(),
            numero=fake.building_number(),
            ciudad=fake.city(),
            provincia="Chaco",
            codigo_postal=fake.postcode(),
            lat=float(fake.latitude()),
            long=float(fake.longitude())
        )
        
        propietario = random.choice(propietarios_ids)
        
        comercio_id = registrar_comercio(
            propietario_id=propietario,
            nombre=fake.company(),
            descripcion=fake.text(max_nb_chars=200),
            categoria=random.choice(categorias),
            telefono=fake.phone_number(),
            correo=fake.company_email(),
            direccion=direccion
        )
        comercios_ids.append(comercio_id)
    
    print(f"✅ {cantidad} comercios generados")
    return comercios_ids


# ==========================================
# GENERAR PUBLICACIONES
# ==========================================

def generar_publicaciones(comercios_ids, cantidad=30):
    """Genera publicaciones aleatorias."""
    print(f"📝 Generando {cantidad} publicaciones...")
    publicaciones_ids = []
    
    for i in range(cantidad):
        comercio = random.choice(comercios_ids)
        
        # Algunas publicaciones tienen imágenes
        imagenes = []
        if random.random() < 0.7:  # 70% tienen imágenes
            num_imagenes = random.randint(1, 3)
            imagenes = [fake.image_url() for _ in range(num_imagenes)]
        
        publicacion_id = crear_publicacion_db(
            comercio_id=comercio,
            titulo=fake.sentence(nb_words=6),
            descripcion=fake.text(max_nb_chars=300),
            imagenes=imagenes
        )
        publicaciones_ids.append(publicacion_id)
    
    print(f"✅ {cantidad} publicaciones generadas")
    return publicaciones_ids


# ==========================================
# GENERAR COMENTARIOS
# ==========================================

def generar_comentarios(usuarios_ids, publicaciones_ids, cantidad=50):
    """Genera comentarios aleatorios, algunos ofensivos."""
    print(f"💬 Generando {cantidad} comentarios...")
    comentarios_ids = []
    
    # Comentarios normales
    comentarios_normales = [
        "¡Excelente producto!", "Me encantó el servicio",
        "Muy recomendable", "Buena atención", "Volveré pronto",
        "Gran calidad", "Precios justos", "Lo mejor de la zona"
    ]
    
    # Comentarios ofensivos (para los reportes)
    comentarios_ofensivos = [
        "Esto es una porquería", "Pésimo servicio, no vuelvo más",
        "Son unos estafadores", "Me trataron muy mal",
        "Desastre total", "No lo recomiendo para nada"
    ]
    
    for i in range(cantidad):
        autor = random.choice(usuarios_ids)
        publicacion = random.choice(publicaciones_ids)
        
        # 20% de probabilidad de comentario ofensivo
        if random.random() < 0.2:
            texto = random.choice(comentarios_ofensivos)
        else:
            texto = random.choice(comentarios_normales)
        
        comentario_id = crear_comentario_db(
            autor_id=autor,
            contenido_id=publicacion,
            tipo_contenido="publicacion",
            texto=texto
        )
        comentarios_ids.append(comentario_id)
    
    print(f"✅ {cantidad} comentarios generados")
    return comentarios_ids


# ==========================================
# GENERAR REPORTES
# ==========================================

def generar_reportes(usuarios_ids, comentarios_ids, cantidad=15):
    """Genera reportes de comentarios."""
    print(f"🚨 Generando {cantidad} reportes...")
    reportes_ids = []
    
    motivos = [
        "Contenido ofensivo",
        "Spam",
        "Lenguaje inapropiado",
        "Acoso",
        "Información falsa"
    ]
    
    # Obtener algunos comentarios aleatorios para reportar
    comentarios_reportados = random.sample(comentarios_ids, min(cantidad, len(comentarios_ids)))
    
    for comentario_id in comentarios_reportados:
        # Obtener el comentario para saber quién es el autor
        comentario = bd.comentarios.find_one({"_id": ObjectId(comentario_id)})
        if not comentario:
            continue
        
        # El que reporta no puede ser el autor
        posibles_reportantes = [u for u in usuarios_ids if u != comentario["autorId"]]
        usuario_reportante = random.choice(posibles_reportantes)
        
        reporte_id = crear_reporte_db(
            comentario_id=comentario_id,
            usuario_que_reporta=usuario_reportante,
            usuario_reportado=comentario["autorId"],
            motivo=random.choice(motivos)
        )
        reportes_ids.append(reporte_id)
        
        # Incrementar contador en el comentario
        bd.comentarios.update_one(
            {"_id": ObjectId(comentario_id)},
            {"$inc": {"cantidadReportes": 1}}
        )
    
    print(f"✅ {cantidad} reportes generados")
    return reportes_ids


# ==========================================
# GENERAR NOTIFICACIONES
# ==========================================

def generar_notificaciones(admins_ids, reportes_ids):
    """Genera notificaciones para admins sobre reportes."""
    print(f"🔔 Generando notificaciones...")
    notificaciones_count = 0
    
    for reporte_id in reportes_ids[:5]:  # Solo las primeras 5
        for admin_id in admins_ids:
            crear_notificacion_db(
                usuario_id=admin_id,
                tipo="reporte_pendiente",
                mensaje="Hay un nuevo comentario reportado que requiere revisión",
                reporte_id=reporte_id
            )
            notificaciones_count += 1
    
    print(f"✅ {notificaciones_count} notificaciones generadas")


# ==========================================
# FUNCIÓN PRINCIPAL
# ==========================================

def inicializar_base_datos():
    """Ejecuta todo el proceso de carga de datos."""
    print("\n" + "="*50)
    print("🚀 INICIANDO CARGA DE DATOS ALEATORIOS")
    print("="*50 + "\n")
    
    # Limpiar BD
    limpiar_base_datos()
    print()
    
    # Generar datos
    usuarios_ids, admins_ids = generar_usuarios(20)
    print()
    
    comercios_ids = generar_comercios(usuarios_ids, 10)
    print()
    
    publicaciones_ids = generar_publicaciones(comercios_ids, 30)
    print()
    
    comentarios_ids = generar_comentarios(usuarios_ids, publicaciones_ids, 50)
    print()
    
    reportes_ids = generar_reportes(usuarios_ids, comentarios_ids, 15)
    print()
    
    generar_notificaciones(admins_ids, reportes_ids)
    print()
    
    print("="*50)
    print("✅ CARGA DE DATOS COMPLETADA")
    print("="*50)
    print(f"\n📊 Resumen:")
    print(f"   - Usuarios: {len(usuarios_ids)} ({len(admins_ids)} admins)")
    print(f"   - Comercios: {len(comercios_ids)}")
    print(f"   - Publicaciones: {len(publicaciones_ids)}")
    print(f"   - Comentarios: {len(comentarios_ids)}")
    print(f"   - Reportes: {len(reportes_ids)}")
    print()


# ==========================================
# EJECUTAR
# ==========================================

if __name__ == "__main__":
    inicializar_base_datos()