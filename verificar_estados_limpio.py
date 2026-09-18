# -*- coding: utf-8 -*-
"""Verificacion por estado usando SOLO el renderer real (pdf_tarjeta de
Default Project\portal_seguros) y SU _medidas_tinta. Para TX ya se certifico
dX=0.00 con este medidor; aqui medimos la tinta de ejemplo real de cada
plantilla y confirmamos que el renderer la mide (si no mide tinta de ejemplo
=> la plantilla esta vacia/movida y ese estado no queda correctamente
posicionado => se elimina)."""
import io
import os
import sys

BASE = r"C:\Users\raulu\Documents\Default Project\portal_seguros"
sys.path.insert(0, BASE)
import pdf_tarjeta as P
import seguro_tipos as ST
import pymupdf

REDACCION = ("fecha_inicio", "fecha_expiracion")


def main():
    mantener = []
    eliminar = []
    for codigo, info in ST.SEGUROS.items():
        ruta = os.path.join(BASE, "templates_pdf", info["plantilla"])
        if not os.path.exists(ruta):
            eliminar.append((codigo, "sin plantilla"))
            continue
        doc = pymupdf.open(ruta)
        pagina = doc[0]
        medidas = P._medidas_tinta(pagina, REDACCION)
        doc.close()
        sin_tinta = []
        for campo in REDACCION:
            celdas = medidas.get(campo) or []
            for i, celda in enumerate(celdas):
                if not celda or celda[0] is None:
                    sin_tinta.append("%s[%d]" % (campo, i))
        if sin_tinta:
            eliminar.append((codigo, "sin tinta de ejemplo en " + ",".join(sin_tinta)))
        else:
            mantener.append(codigo)

    print("MANTENER (renderer real los alinea como TX):")
    for c in mantener:
        print("  ", c)
    print("ELIMINAR (no quedan correctamente posicionados):")
    for c, r in eliminar:
        print("  %-10s %s" % (c, r))


if __name__ == "__main__":
    main()
