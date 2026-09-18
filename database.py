import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

from config import DATABASE_PATH


def _conexion():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _conexion()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre TEXT NOT NULL DEFAULT '',
            rol TEXT NOT NULL DEFAULT 'vendedor',
            activo INTEGER NOT NULL DEFAULT 1,
            fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def cantidad_usuarios():
    conn = _conexion()
    total = conn.execute("SELECT COUNT(*) AS total FROM usuarios").fetchone()["total"]
    conn.close()
    return total


def crear_usuario(username, password, nombre="", rol="vendedor"):
    conn = _conexion()
    try:
        conn.execute(
            "INSERT INTO usuarios (username, password_hash, nombre, rol) VALUES (?, ?, ?, ?)",
            (username, generate_password_hash(password), nombre, rol),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def verificar_usuario(username, password):
    conn = _conexion()
    fila = conn.execute(
        "SELECT * FROM usuarios WHERE username = ? AND activo = 1", (username,)
    ).fetchone()
    conn.close()
    if fila and check_password_hash(fila["password_hash"], password):
        return dict(fila)
    return None