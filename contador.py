import os
import threading

from config import DATA_DIR

NUMERO_INICIAL = 1140

_bloqueo = threading.Lock()


def _ruta(codigo):
    return os.path.join(DATA_DIR, "numero_secuencial_{}.txt".format(codigo))


def _leer(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return NUMERO_INICIAL - 1


def _guardar(ruta, valor):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(str(valor))


def nombre_archivo_pdf(codigo="TX"):
    ruta = _ruta(codigo)
    with _bloqueo:
        valor = _leer(ruta) + 1
        _guardar(ruta, valor)
    return "SG_FIC_{}_{:04d}.pdf".format(codigo, valor)