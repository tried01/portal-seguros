import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import crear_usuario, init_db, cantidad_usuarios

init_db()


def crear():
    if cantidad_usuarios() == 0:
        print("No hay usuarios. Creando el administrador inicial...")
        crear_usuario("admin", "admin123", nombre="Administrador", rol="admin")
        print("  Usuario: admin | Contrasena: admin123 (cambiala luego)")

    username = input("Usuario: ").strip()
    if not username:
        return
    contrasena = input("Contrasena: ").strip()
    nombre = input("Nombre y apellido (opcional): ").strip()
    rol = input("Rol (admin/vendedor) [vendedor]: ").strip() or "vendedor"

    if crear_usuario(username, contrasena, nombre=nombre, rol=rol):
        print(f"[OK] Usuario {username} creado con rol '{rol}'.")
    else:
        print(f"[ERROR] El usuario '{username}' ya existe.")


if __name__ == "__main__":
    crear()