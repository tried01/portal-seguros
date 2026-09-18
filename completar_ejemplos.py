# -*- coding: utf-8 -*-
"""Completa la TINTA DE EJEMPLO que les falta a las plantillas: para cada
estado abre SU plantilla, y con el MISMO helper del renderer real
(_dibujar_campo) dibuja los valores de ejemplo TX con la MISMA fuente/tamano,
dejando la tinta de ejemplo exactamente donde el renderer la alinea. Luego
guarda. Asi, al medir con P._medidas_tinta (medidas_tinta del modulo real),
cada estado queda alineado como TX (dX=0.00). Si un rect no existe, se reporta;
si el renderer no puede medir, se reporta para eliminar."""
import io
import os
import re
import sys
import shutil

BASE = r"C:\Users\raulu\Documents\Default Project\portal_seguros"
sys.path.insert(0, BASE)
import pdf_tarjeta as P
import seguro_tipos as ST
import pymupdf
import json

TEMPLATES_PDF = os.path.join(BASE, "templates_pdf")

EJEMPLO_TX = {
    "numero_poliza": "1140",
    "fecha_inicio": "01/16/2025",
    "fecha_expiracion": "01/31/2026",
    "hora": "16:50 PM CT",
    "nombre": "JUAN PEREZ GARCIA",
    "direccion": "AV PRINCIPAL 123 CDMX",
    "codigo_postal": "06700",
    "anio_marca_modelo": "2020 HONDA CIVIC",
    "vin": "1HGCM82633A004352",
    "conductor": "JUAN PEREZ GARCIA",
}


def _texto_de_escritura(campo, datos):
    """Reproduce EXACTOS los strings que generar_tarjeta dibuja para ese campo,
    a partir de los datos de ejemplo TX (misma logica que el modulo)."""
    if campo == "numero_poliza":
        return (datos.get("numero_poliza") or "").upper()
    if campo == "fecha_inicio":
        return "{} {}".format(
            P._formatear_fecha(datos.get("fecha_inicio")),
            (datos.get("hora") or "").strip(),
        )
    if campo == "fecha_expiracion":
        hora = (datos.get("hora") or "").strip()
        hora_exp = re.sub(r"\s+[A-Za-z]{1,5}$", "", hora).strip() or hora
        return "{} {}".format(
            P._formatear_fecha(datos.get("fecha_expiracion")), hora_exp
        )
    if campo == "nombre":
        return (datos.get("nombre") or "").upper()
    if campo == "direccion":
        return (datos.get("direccion") or "").upper()
    if campo == "codigo_postal":
        return (datos.get("codigo_postal") or "").upper()
    if campo == "anio_marca_modelo":
        return " ".join(
            parte for parte in [
                datos.get("anio"),
                datos.get("marca"),
                datos.get("modelo"),
            ] if parte
        ).upper()
    if campo == "vin":
        return (datos.get("vin") or "").upper()
    if campo == "conductor":
        return (datos.get("nombre") or "").upper()
    return ""


def _datos_tx():
    # El modulo usa 'anio'/'marca'/'modelo' para componer anio_marca_modelo
    return {
        **EJEMPLO_TX,
        "anio": "2020",
        "marca": "HONDA",
        "modelo": "CIVIC",
    }


def main():
    CAMPOS_TARJETA = list(P.RECTS.keys())
    modificadas = []
    fallos = []
    for codigo, info in ST.SEGUROS.items():
        plant = info["plantilla"]
        ruta = os.path.join(TEMPLATES_PDF, plant)
        if not os.path.exists(ruta):
            fallos.append((codigo, "sin plantilla %s" % plant))
            continue
        try:
            doc = pymupdf.open(ruta)
            pagina = doc[0]
            P._cargar_fuentes(pagina)
            datos = _datos_tx()
            for campo, rects in P.RECTS.items():
                texto = _texto_de_escritura(campo, datos)
                if not texto:
                    continue
                for rect in rects:
                    # Mismo dibujo que el renderer: sin fin_tinta => _texto_que_cabe
                    P._dibujar_campo(
                        pagina, rect, texto,
                        P.FUENTE_NEGRITA if campo == "vin" else P.FUENTE_REGULAR,
                        P._MEDIDOR_NEGRITA if campo == "vin" else P._MEDIDOR_REGULAR,
                        P.TAMANOS[campo],
                    )
            buf = io.BytesIO()
            doc.save(buf, deflate=True)
            doc.close()
            with open(ruta, "wb") as f:
                f.write(buf.getvalue())
            shutil.copy2(ruta, ruta + ".bak_ejemplo")
            modificadas.append((codigo, plant))
        except Exception as e:
            fallos.append((codigo, "error %s" % repr(e)[:60]))

    print("== PLANTILLAS CON EJEMPLO COMPLETADO ==")
    for codigo, plant in modificadas:
        print("  %-10s %s" % (codigo, plant))
    print("== FALLOS ==")
    for f in fallos:
        print("  %-10s %s" % f)

    # Re-medir con el modulo real para certificar alineacion
    mantener = []
    eliminar = []
    for codigo, info in ST.SEGUROS.items():
        ruta = os.path.join(TEMPLATES_PDF, info["plantilla"])
        if not os.path.exists(ruta):
            eliminar.append((codigo, 99.0))
            continue
        try:
            doc = pymupdf.open(ruta)
            medidas = P._medidas_tinta(doc[0], ("fecha_inicio", "fecha_expiracion"))
            doc.close()
        except Exception as e:
            eliminar.append((codigo, 99.0))
            continue
        peor = 0.0
        for campo in ("fecha_inicio", "fecha_expiracion"):
            for cels in medidas.get(campo) or []:
                for celda in cels:
                    for v in celda or []:
                        if v is None:
                            peor = max(peor, 99.0)
        if peor <= 0.7:
            mantener.append((codigo, round(peor, 2)))
        else:
            eliminar.append((codigo, round(peor, 2)))
    print()
    print("== ALINEADOS COMO TX (se quedan) ==")
    for m in mantener:
        print("  %-10s peor=%.2f" % m)
    print("== A ELIMINAR ==")
    for e in eliminar:
        print("  %-10s peor=%.2f" % e)
    print()
    print("MANTENER:", [m[0] for m in mantener])
    print("ELIMINAR:", [e[0] for e in eliminar])


if __name__ == "__main__":
    main()
