from Conexion import bd
from Colecciones.Usuario import crear_usuario

# Crear un usuario de prueba
usuario = crear_usuario(
    nombre="Pedro",
    apellido="Lock",
    correo="PL@test.com",
    contraseña="123456"
)

# Insertarlo en MongoDB
resultado = bd.usuarios.insert_one(usuario)
print("Usuario creado con ID:", resultado.inserted_id)

# Buscarlo
usuario_encontrado = bd.usuarios.find_one({"correo": "PL@test.com"})
print("Usuario encontrado:", usuario_encontrado)