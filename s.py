# s.py - Script para cargar datos de prueba RANDOM con Faker
import sys
sys.path.append('.')
from datetime import datetime, timedelta
from bson import ObjectId
from Conexion import bd
import random
from faker import Faker

# Importar CRUDs
from Crud.CrudUsuario import registrar_usuario
from Crud.CrudComercio import registrar_comercio
from Crud.CrudPublicacion import crear_publicacion_db
from Crud.CrudComentario import crear_comentario_db, incrementar_reportes
from Crud.CrudReporte import crear_reporte_db
from Crud.CrudNotificacion import crear_notificacion_db, crear_notificacion_admin

# Importar estructuras
from Colecciones.Comercio import crear_direccion

# Inicializar Faker en español
fake = Faker('es_ES')

print("\n" + "="*70)
print("🚀 CARGANDO DATOS ALEATORIOS CON FAKER")
print("="*70)

# ==========================================
# CONFIGURACIÓN
# ==========================================
CANT_USUARIOS = 30
CANT_COMERCIOS = 15
CANT_PUBLICACIONES_POR_COMERCIO = (3, 8)  # Entre 3 y 8
CANT_EVENTOS = 5
CANT_COMENTARIOS_POR_PUBLICACION = (2, 10)  # Entre 2 y 10
PROBABILIDAD_COMENTARIO_MALO = 0.15  # 15% de comentarios problemáticos

# ==========================================
# PASO 2: CREAR USUARIOS
# ==========================================
print(f"\n👥 Creando {CANT_USUARIOS} usuarios...")

usuarios_ids = []
admins_ids = []
propietarios_ids = []
usuarios_normales_ids = []

# 1. Crear al menos 2 admins
for i in range(2):
    usuario_id = registrar_usuario(
        nombre=fake.first_name(),
        apellido=fake.last_name(),
        correo=f"admin{i+1}@dondeqeda.com",
        contraseña=fake.password(),
        roles=["Usuario", "Admin"]
    )
    if usuario_id:
        usuarios_ids.append(usuario_id)
        admins_ids.append(usuario_id)

# 2. Crear propietarios (30% de los usuarios restantes)
cant_propietarios = int((CANT_USUARIOS - 2) * 0.3)
for i in range(cant_propietarios):
    usuario_id = registrar_usuario(
        nombre=fake.first_name(),
        apellido=fake.last_name(),
        correo=fake.unique.email(),
        contraseña=fake.password(),
        roles=["Usuario", "Propietario"]
    )
    if usuario_id:
        usuarios_ids.append(usuario_id)
        propietarios_ids.append(usuario_id)

# 3. Crear usuarios normales
usuarios_restantes = CANT_USUARIOS - len(usuarios_ids)
for i in range(usuarios_restantes):
    usuario_id = registrar_usuario(
        nombre=fake.first_name(),
        apellido=fake.last_name(),
        correo=fake.unique.email(),
        contraseña=fake.password(),
        roles=["Usuario"]
    )
    if usuario_id:
        usuarios_ids.append(usuario_id)
        usuarios_normales_ids.append(usuario_id)

# 4. Dar strikes a algunos usuarios random (para testing)
usuarios_con_strikes = random.sample(usuarios_normales_ids, min(3, len(usuarios_normales_ids)))
for usuario_id in usuarios_con_strikes:
    strikes = random.randint(1, 2)
    bd.usuarios.update_one(
        {"_id": ObjectId(usuario_id)},
        {"$set": {"strikes": strikes}}
    )

print(f"   ✅ {len(usuarios_ids)} usuarios creados")
print(f"      - Admins: {len(admins_ids)}")
print(f"      - Propietarios: {len(propietarios_ids)}")
print(f"      - Usuarios normales: {len(usuarios_normales_ids)}")
print(f"      - Usuarios con strikes: {len(usuarios_con_strikes)}")

# ==========================================
# PASO 3: CREAR COMERCIOS
# ==========================================
print(f"\n🏪 Creando {CANT_COMERCIOS} comercios...")

comercios_ids = []
categorias = [
    "Gastronomía", "Salud y Bienestar", "Educación", "Tecnología",
    "Moda", "Hogar y Decoración", "Entretenimiento", "Servicios Profesionales",
    "Turismo", "Automotor"
]

nombres_comercios = {
    "Gastronomía": ["Restaurante", "Parrilla", "Pizzería", "Café", "Bar", "Heladería"],
    "Salud y Bienestar": ["Gimnasio", "Spa", "Nutrición", "Yoga", "Pilates"],
    "Educación": ["Instituto", "Academia", "Escuela"],
    "Tecnología": ["Tech", "Informática", "Reparaciones"],
    "Moda": ["Boutique", "Tienda", "Moda"],
    "Hogar y Decoración": ["Bazar", "Deco", "Muebles"],
    "Entretenimiento": ["Cine", "Boliche", "Juegos"],
    "Servicios Profesionales": ["Estudio", "Consultora"],
    "Turismo": ["Agencia", "Turismo"],
    "Automotor": ["Taller", "Repuestos"]
}

for i in range(CANT_COMERCIOS):
    # Elegir propietario random
    propietario_id = random.choice(propietarios_ids)
    
    # Elegir categoría random
    categoria = random.choice(categorias)
    
    # Generar nombre según categoría
    tipo_comercio = random.choice(nombres_comercios[categoria])
    nombre = f"{tipo_comercio} {fake.last_name()}"
    
    # Crear dirección
    direccion = crear_direccion(
        calle=fake.street_name(),
        numero=str(random.randint(100, 9999)),
        ciudad="Resistencia",
        provincia="Chaco",
        codigo_postal="3500",
        lat=round(-27.4514 + random.uniform(-0.05, 0.05), 6),
        long=round(-58.9867 + random.uniform(-0.05, 0.05), 6)
    )
    
    # Crear horarios realistas
    horario = {}
    dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    
    for dia in dias[:5]:  # Lunes a viernes
        horario[dia] = [
            {"apertura": "09:00", "cierre": "13:00"},
            {"apertura": "17:00", "cierre": "21:00"}
        ]
    
    # Sábado
    horario["sabado"] = [{"apertura": "09:00", "cierre": "14:00"}]
    
    # Domingo (algunos cierran)
    if random.random() > 0.3:  # 70% abre los domingos
        horario["domingo"] = [{"apertura": "10:00", "cierre": "13:00"}]
    else:
        horario["domingo"] = []
    
    # Registrar comercio
    comercio_id = registrar_comercio(
        propietario_id=propietario_id,
        nombre=nombre,
        descripcion=fake.text(max_nb_chars=200),
        categoria=categoria,
        telefono=fake.phone_number(),
        correo=fake.email(),
        direccion=direccion,
        horario=horario
    )
    
    if comercio_id:
        comercios_ids.append(comercio_id)

print(f"   ✅ {len(comercios_ids)} comercios creados")

# ==========================================
# PASO 4: CREAR PUBLICACIONES
# ==========================================
print(f"\n📝 Creando publicaciones...")

publicaciones_ids = []
publicaciones_por_comercio = {}  # Para tracking

titulos_ejemplo = [
    "¡Nueva promoción especial!",
    "Oferta del mes",
    "No te lo pierdas",
    "Últimos días de descuento",
    "Llegó nueva mercadería",
    "Atención clientes",
    "Novedad del día",
    "Producto destacado",
    "Combo especial"
]

for comercio_id in comercios_ids:
    # Cantidad random de publicaciones por comercio
    cant_pubs = random.randint(*CANT_PUBLICACIONES_POR_COMERCIO)
    publicaciones_por_comercio[comercio_id] = []
    
    for _ in range(cant_pubs):
        titulo = random.choice(titulos_ejemplo)
        descripcion = fake.text(max_nb_chars=300)
        
        # 50% de probabilidad de tener imágenes
        imagenes = []
        if random.random() > 0.5:
            cant_imagenes = random.randint(1, 3)
            imagenes = [f"https://picsum.photos/800/600?random={random.randint(1, 1000)}" 
                       for _ in range(cant_imagenes)]
        
        pub_id = crear_publicacion_db(
            comercio_id=comercio_id,
            titulo=titulo,
            descripcion=descripcion,
            imagenes=imagenes
        )
        
        if pub_id:
            publicaciones_ids.append(pub_id)
            publicaciones_por_comercio[comercio_id].append(pub_id)

print(f"   ✅ {len(publicaciones_ids)} publicaciones creadas")

# ==========================================
# PASO 5: CREAR EVENTOS
# ==========================================
print(f"\n🎉 Creando {CANT_EVENTOS} eventos...")

eventos_ids = []

titulos_eventos = [
    "Gran inauguración",
    "Fiesta de aniversario",
    "Evento especial",
    "Noche temática",
    "Festival",
    "Jornada de puertas abiertas",
    "Día del cliente"
]

for i in range(CANT_EVENTOS):
    comercio_creador = random.choice(comercios_ids)
    comercio_data = bd.comercios.find_one({"_id": ObjectId(comercio_creador)})
    
    fecha_inicio = fake.date_time_between(start_date='+1d', end_date='+60d')
    duracion_horas = random.randint(2, 8)
    fecha_fin = fecha_inicio + timedelta(hours=duracion_horas)
    
    # Crear evento usando la estructura de colección
    from Colecciones.Eventos import crear_evento
    
    evento = crear_evento(
        comercio_creador_id=comercio_creador,
        titulo=random.choice(titulos_eventos),
        descripcion=fake.text(max_nb_chars=250),
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        ubicacion=comercio_data["direccion"],
        imagenes=[f"https://picsum.photos/1200/800?random={random.randint(1, 1000)}"],
        comercios_invitados=[]
    )
    
    resultado = bd.eventos.insert_one(evento)
    eventos_ids.append(resultado.inserted_id)

print(f"   ✅ {len(eventos_ids)} eventos creados")

# ==========================================
# PASO 6: CREAR COMENTARIOS
# ==========================================
print(f"\n💬 Creando comentarios...")

comentarios_ids = []
comentarios_malos_ids = []

comentarios_positivos = [
    "¡Excelente servicio! Muy recomendable.",
    "Me encantó, volveré sin dudas.",
    "Buena atención y precios accesibles.",
    "Lo mejor de la zona, sin dudas.",
    "Muy buena calidad, superó mis expectativas.",
    "Atención de primera, muy profesionales.",
    "Ambiente agradable y cómodo.",
    "Vale la pena visitarlos!"
]

comentarios_negativos = [
    "Pésimo servicio, nunca más vuelvo.",
    "Una estafa total, no lo recomiendo para nada.",
    "Muy mala atención, el dueño es un desastre.",
    "Horrible experiencia, pérdida de tiempo y dinero.",
    "No funciona nada, todo sucio y descuidado.",
    "Empleados maleducados y producto de mala calidad."
]

for pub_id in publicaciones_ids:
    # Cantidad random de comentarios
    cant_comentarios = random.randint(*CANT_COMENTARIOS_POR_PUBLICACION)
    
    for _ in range(cant_comentarios):
        autor_id = random.choice(usuarios_ids)
        
        # Decidir si es comentario bueno o malo
        es_malo = random.random() < PROBABILIDAD_COMENTARIO_MALO
        
        if es_malo:
            texto = random.choice(comentarios_negativos)
        else:
            texto = random.choice(comentarios_positivos)
        
        comentario_id = crear_comentario_db(
            autor_id=autor_id,
            contenido_id=pub_id,
            tipo_contenido="publicacion",
            texto=texto
        )
        
        if comentario_id:
            comentarios_ids.append(comentario_id)
            if es_malo:
                comentarios_malos_ids.append(comentario_id)

# Algunos comentarios en eventos
for evento_id in eventos_ids:
    cant_comentarios = random.randint(1, 5)
    
    for _ in range(cant_comentarios):
        autor_id = random.choice(usuarios_ids)
        texto = random.choice(comentarios_positivos)
        
        comentario_id = crear_comentario_db(
            autor_id=autor_id,
            contenido_id=evento_id,
            tipo_contenido="evento",
            texto=texto
        )
        
        if comentario_id:
            comentarios_ids.append(comentario_id)

print(f"   ✅ {len(comentarios_ids)} comentarios creados")
print(f"      - Comentarios problemáticos: {len(comentarios_malos_ids)}")

# ==========================================
# PASO 7: CREAR REPORTES
# ==========================================
print(f"\n🚨 Creando reportes sobre comentarios malos...")

reportes_ids = []

motivos_reporte = [
    "Lenguaje ofensivo e inapropiado",
    "Comentario falso y difamatorio",
    "Acoso o intimidación",
    "Contenido inapropiado",
    "Spam o publicidad no deseada",
    "Información falsa o engañosa"
]

# Reportar algunos comentarios malos
comentarios_a_reportar = random.sample(
    comentarios_malos_ids, 
    min(len(comentarios_malos_ids), 10)  # Reportar hasta 10
)

for comentario_id in comentarios_a_reportar:
    # Obtener datos del comentario
    comentario = bd.comentarios.find_one({"_id": ObjectId(comentario_id)})
    
    if comentario:
        # Cantidad de reportes (1-3)
        cant_reportes = random.randint(1, 3)
        
        # Usuarios que reportan (diferentes)
        reportantes = random.sample(usuarios_normales_ids, min(cant_reportes, len(usuarios_normales_ids)))
        
        for reportante_id in reportantes:
            reporte_id = crear_reporte_db(
                comentario_id=comentario_id,
                usuario_que_reporta=reportante_id,
                usuario_reportado=comentario["autorId"],
                motivo=random.choice(motivos_reporte)
            )
            
            if reporte_id:
                reportes_ids.append(reporte_id)
        
        # Incrementar contador de reportes del comentario
        for _ in range(cant_reportes):
            incrementar_reportes(comentario_id)

print(f"   ✅ {len(reportes_ids)} reportes creados")

# ==========================================
# PASO 8: CREAR NOTIFICACIONES
# ==========================================
print(f"\n🔔 Creando notificaciones...")

# Notificar a admins sobre reportes pendientes
if reportes_ids:
    cant_notif = crear_notificacion_admin(
        tipo="reporte_pendiente",
        mensaje=f"Hay {len(reportes_ids)} reportes pendientes de revisión",
        reporte_id=None
    )
    print(f"   ✅ {cant_notif} notificaciones enviadas a admins")

# Notificar a usuarios reportados
usuarios_reportados = set()
for reporte_id in reportes_ids:
    reporte = bd.reportes.find_one({"_id": ObjectId(reporte_id)})
    if reporte:
        usuarios_reportados.add(reporte["usuarioReportado"])

for usuario_id in usuarios_reportados:
    crear_notificacion_db(
        usuario_id=usuario_id,
        tipo="advertencia",
        mensaje="Tu comentario ha sido reportado. Por favor, respeta las normas de la comunidad.",
        reporte_id=None
    )

print(f"   ✅ {len(usuarios_reportados)} notificaciones enviadas a usuarios reportados")

# ==========================================
# RESUMEN FINAL
# ==========================================
print("\n" + "="*70)
print("✅ CARGA DE DATOS COMPLETADA EXITOSAMENTE")
print("="*70)

print(f"\n📊 RESUMEN DE DATOS GENERADOS:")
print(f"\n   👥 Usuarios: {len(usuarios_ids)}")
print(f"      - Admins: {len(admins_ids)}")
print(f"      - Propietarios: {len(propietarios_ids)}")
print(f"      - Usuarios normales: {len(usuarios_normales_ids)}")
print(f"      - Con strikes: {len(usuarios_con_strikes)}")

print(f"\n   🏪 Comercios: {len(comercios_ids)}")
print(f"   📝 Publicaciones: {len(publicaciones_ids)}")
print(f"   🎉 Eventos: {len(eventos_ids)}")
print(f"   💬 Comentarios: {len(comentarios_ids)}")
print(f"      - Problemáticos: {len(comentarios_malos_ids)}")

print(f"\n   🚨 Reportes: {len(reportes_ids)}")
print(f"   🔔 Notificaciones: {len(usuarios_reportados) + cant_notif}")

print("\n💡 SIGUIENTE PASO:")
print("   ➜ python Menu.py")
print("   ➜ Opción 2: Sistema de Moderación")

print("\n" + "="*70)