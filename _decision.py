# -*- coding: utf-8 -*-
"""Decision final: mantener solo estados alineados con su ejemplo (<=0.7pt)."""
import io, os, re, sys

BASE = r"C:\Users\raulu\Documents\Default Project\portal_seguros"
sys.path.insert(0, BASE)
import pdf_tarjeta as P
import seguro_tipos as ST

import pymupdf

CAMPOS = ("fecha_inicio", "fecha_expiracion")


def _valores_de_ejemplo_plantilla(ruta_template):
    """Extrae fecha_inicio/fecha_expiracion y la hora del texto de ejemplo
    que ya vive en la plantilla, para generar con los MISMO valores."""
    doc = pymupdf.open(ruta_template)
    texto = doc[0].get_text()
    doc.close()
    fechas = re.findall(r"(\d{2}/\d{2}/\d{4})\s+(\d{1,2}:\d{2}\s*[AP]M)", texto)
    inicio = None
    expira = None
    hora = None
    if len(fechas) >= 2:
        f1, h1 = fechas[0]
        f2, h2 = fechas[1]
        inicio, expira = f1, f2
        hora = h1
        # En el ejemplo, la expiracion no lleva zona horaria; la eliminamos
        hora = re.sub(r"\s*[A-Za-z]{1,5}$", "", hora).strip()
    return {"fecha_inicio": inicio, "fecha_expiracion": expira, "hora": hora}


def _generar_y_medir(plantilla, valores):
    buf = P.generar_tarjeta(plantilla, valores)
    doc = pymupdf.open(stream=buf, filetype="pdf")
    medidas = P._medidas_tinta(doc[0], CAMPOS)
    doc.close()
    return medidas


def medir(plan):
    doc = pymupdf.open(plan)
    med = P._medidas_tinta(doc[0], CAMPOS)
    doc.close()
    return med


resultados = {}
for codigo, info in ST.SEGUROS.items():
    plantilla = info["plantilla"]
    ruta = os.path.join(BASE, "templates_pdf", plantilla)
    if not os.path.exists(ruta):
        resultados[codigo] = ("SIN PLANTILLA", 99.0)
        continue
    ejemplo = medir(ruta)
    valores = _valores_de_ejemplo_plantilla(ruta)
    if not valores["fecha_inicio"]:
        resultados[codigo] = ("SIN EJEMPLO", 99.0)
        continue
    try:
        generado = _generar_y_medir(ruta, valores)
    except Exception as e:
        resultados[codigo] = ("ERROR " + repr(e)[:40], 99.0)
        continue
    peor = 0.0
    for c in CAMPOS:
        for i in range(2):
            e = ejemplo.get(c, [None, None])[i]
            g = generado.get(c, [None, None])[i]
            if e and g:
                peor = max(peor, abs((e[0] or 0) - (g[0] or 0)))
                peor = max(peor, abs((e[1] or 0) - (g[1] or 0)))
    estado = "OK" if peor <= 0.7 else "FALLA"
    resultados[codigo] = (estado, round(peor, 2))

ok = [c for c, (e, _) in resultados.items() if e == "OK"]
fail = [c for c, (e, _) in resultados.items() if e != "OK"]
for c, (e, p) in resultados.items():
    print("%-14s %-12s %.2f" % (c, e, p))
print("KEEP:", ok)
print("REMOVE:", fail)
