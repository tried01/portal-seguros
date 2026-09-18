# -*- coding: utf-8 -*-
"""Minimo y CORRECTO: usa solo el modulo real (pdf_tarjeta) y su propio
_medidas_tinta para certificar cada estado contra SU plantilla. Ese mismo
medidor dio TX dX=0.00. Reporta MANTENER/ELIMINAR por estado segun haya tinta
medible en las celdas de escritura."""
import os, sys, io
BASE = r"C:\Users\raulu\Documents\Default Project\portal_seguros"
sys.path.insert(0, BASE)
import pdf_tarjeta as P
import seguro_tipos as ST
import pymupdf

CAMPOS = ("fecha_inicio", "fecha_expiracion")


def main():
    mantener = []
    eliminar = []
    for codigo, info in ST.SEGUROS.items():
        ruta = os.path.join(BASE, "templates_pdf", info["plantilla"])
        if not os.path.exists(ruta):
            eliminar.append((codigo, "sin plantilla"))
            continue
        try:
            doc = pymupdf.open(ruta)
            medidas = P._medidas_tinta(doc[0], CAMPOS)
            doc.close()
        except Exception as e:
            eliminar.append((codigo, "error " + repr(e)[:40]))
            continue
        sin_tinta = []
        for campo in CAMPOS:
            for i, celda in enumerate(medidas.get(campo) or []):
                if not celda or not celda[0] or not celda[1]:
                    sin_tinta.append("%s[%d]" % (campo, i))
        if sin_tinta:
            eliminar.append((codigo, "sin tinta: " + ",".join(sin_tinta)))
        else:
            mantener.append(codigo)
    print("== MANTENER (se queda, alineado como TX) ==")
    for m in mantener:
        print("  ", m)
    print("== ELIMINAR ==")
    for e in eliminar:
        print("  %-10s %s" % e)
    print()
    print("MANTENER:", mantener)
    print("ELIMINAR:", [e[0] for e in eliminar])


if __name__ == "__main__":
    main()
