# -*- coding: utf-8 -*-
"""Renderer que dibuja los datos de la tarjeta de seguro sobre la plantilla.

Para cada celda se mide primero la tinta del texto de ejemplo que ya viene en
la plantilla (posicion de inicio y fin en X). Ese barrido hace que el texto
generado imite exactamente la posicion del ejemplo, incluso cuando el estado
usa textos de ejemplo de longitud distinta. Si la plantilla no tiene tinta
medible en esa celda, se usa la ubicacion por defecto (x0 + 1)."""

import io
import os
import re
import secrets
import string
from datetime import datetime

import pymupdf

FUENTE_REGULAR = "Calibri"
FUENTE_NEGRITA = "CalibriBold"
# Ruta empaquetada (funciona en Windows y Linux/Railway) con fallback a C:/Windows/Fonts
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_RUTA_EMPAQUETADA = os.path.join(_BASE_DIR, "fonts", "calibri.ttf")
_RUTA_EMPAQUETADA_BOLD = os.path.join(_BASE_DIR, "fonts", "calibrib.ttf")
RUTA_CALIBRI = _RUTA_EMPAQUETADA if os.path.exists(_RUTA_EMPAQUETADA) else "C:/Windows/Fonts/calibri.ttf"
RUTA_CALIBRI_BOLD = _RUTA_EMPAQUETADA_BOLD if os.path.exists(_RUTA_EMPAQUETADA_BOLD) else "C:/Windows/Fonts/calibrib.ttf"

try:
    _MEDIDOR_REGULAR = pymupdf.Font(fontfile=RUTA_CALIBRI)
except Exception:
    _MEDIDOR_REGULAR = pymupdf.Font("helv")

try:
    _MEDIDOR_NEGRITA = pymupdf.Font(fontfile=RUTA_CALIBRI_BOLD)
except Exception:
    _MEDIDOR_NEGRITA = pymupdf.Font("helv")

RUTA_CALIBRI_REGULAR = RUTA_CALIBRI
RUTA_CALIBRI_BOLD_TTF = RUTA_CALIBRI_BOLD

HORA_EJEMPLO = "16:50 PM CT"

TAMANOS = {
    "numero_poliza": 9.0,
    "fecha_inicio": 9.0,
    "fecha_expiracion": 9.0,
    "nombre": 8.5,
    "direccion": 8.5,
    "codigo_postal": 8.5,
    "anio_marca_modelo": 9.0,
    "vin": 9.0,
    "conductor": 8.5,
}

# Celdas de escritura: tarjeta izquierda y tarjeta derecha.
RECTS = {
    "numero_poliza": [(34.6, 267.65, 92, 281.65), (300.3, 266.05, 358, 280.05)],
    "fecha_inicio": [(95.6, 266.58, 192.0, 280.58), (367.6, 266.08, 462.0, 280.08)],
    "fecha_expiracion": [(199.4, 266.58, 297.0, 280.58), (471.1, 266.08, 569.0, 280.08)],
    "nombre": [(35.1, 223.84, 191, 235.84), (301.1, 225.64, 455, 236.64)],
    "direccion": [(35.1, 232.8, 191, 243.8), (301.1, 234.6, 455, 245.6)],
    "codigo_postal": [(35.1, 241.3, 191, 252.3), (301.1, 243.1, 455, 254.1)],
    "anio_marca_modelo": [(70.6, 298.7, 194, 310.7), (323.9, 296.6, 464, 308.6)],
    "vin": [(196.0, 298.6, 288, 310.6), (465.0, 297.3, 553, 309.3)],
    "conductor": [(33.6, 415.9, 290, 428.9), (299.5, 416.5, 557, 429.5)],
}

# Celdas de redaccion (texto de ejemplo) por campo, tarjeta izq/der.
REDACT_RECTS = {
    "numero_poliza": [(33.4, 266.9, 90.7, 280.5), (299.1, 266.9, 356.3, 279.4)],
    "fecha_inicio": [(86.4, 266.9, 190.0, 280.3), (366.4, 266.9, 462.0, 279.4)],
    "fecha_expiracion": [(198.2, 266.9, 297.0, 280.3), (469.9, 266.9, 569.0, 279.4)],
    "nombre": [(33.9, 222.8, 123.6, 235.7), (299.9, 224.1, 389.6, 237.0)],
    "direccion": [(33.9, 231.3, 115.7, 244.2), (299.9, 233.1, 381.7, 246.0)],
    "codigo_postal": [(33.9, 239.8, 108.0, 252.7), (299.9, 241.6, 374.0, 254.5)],
    "anio_marca_modelo": [(69.6, 298.6, 176.3, 310.8), (322.7, 297.9, 419.8, 308.7)],
    "vin": [(196.0, 298.6, 281.3, 311.9), (465.0, 298.6, 551.1, 311.6)],
    "conductor": [(32.4, 414.4, 122.2, 427.3), (298.3, 416.4, 388.1, 429.8)],
}


def _formatear_fecha(valor):
    """Convierte el valor a formato MM/DD/YYYY (igual que el ejemplo)."""
    valor = (valor or "").strip()
    for formato in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(valor, formato).strftime("%m/%d/%Y")
        except ValueError:
            continue
    return valor


def _texto_que_cabe(texto, medidor, ancho, tope):
    tamano = tope
    while tamano > 5.5 and medidor.text_length(texto, fontsize=tamano) > ancho:
        tamano -= 0.4
    return tamano


def _medidas_tinta(pagina, campos):
    """Devuelve {campo: [(inicio, fin), (inicio, fin)]} por tarjeta izq/der,
    midiendo la posicion de la tinta del texto de ejemplo de la plantilla."""
    chars = []
    for block in pagina.get_text("rawdict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                for c in span["chars"]:
                    if not c["c"].isspace():
                        chars.append(c)
    medidas = {campo: [None, None] for campo in campos}
    for campo in campos:
        for i, rect in enumerate(RECTS[campo]):
            x0, y0, x1, y1 = rect
            inicio = None
            fin = None
            for c in chars:
                cx0, cy0, cx1, cy1 = c["bbox"]
                if y0 - 0.5 <= (cy0 + cy1) / 2 <= y1 + 0.5 and x0 <= cx0 <= x1:
                    if inicio is None or cx0 < inicio:
                        inicio = cx0
                    if fin is None or cx1 > fin:
                        fin = cx1
            medidas[campo][i] = (inicio, fin)
    return medidas


def _cargar_fuentes(pagina):
    if os.path.exists(RUTA_CALIBRI):
        pagina.insert_font(fontname=FUENTE_REGULAR, fontfile=RUTA_CALIBRI)
    if os.path.exists(RUTA_CALIBRI_BOLD):
        pagina.insert_font(fontname=FUENTE_NEGRITA, fontfile=RUTA_CALIBRI_BOLD)


def _aplicar_redaccion(pagina, medidas=None):
    for campo, rects in REDACT_RECTS.items():
        for i, r in enumerate(rects):
            x0, y0, x1, y1 = r
            if medidas and medidas.get(campo) and medidas[campo][i]:
                inicio, fin = medidas[campo][i]
                if inicio is not None:
                    x0 = min(x0, inicio - 0.8)
                if fin is not None:
                    x1 = max(x1, fin + 0.6)
            pagina.add_redact_annot(pymupdf.Rect(x0, y0, x1, y1))
    pagina.apply_redactions(
        images=pymupdf.PDF_REDACT_IMAGE_NONE,
        graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
    )


def _dibujar_campo(pagina, rect, texto, fuente, medidor, tope, fin_tinta=None, inicio_tinta=None):
    x0, y0, x1, y1 = rect
    ancho = x1 - (x0 + 1.5)
    if fin_tinta is not None:
        ancho = min(ancho, fin_tinta - (x0 + 1))
    if fin_tinta is None:
        tamano = _texto_que_cabe(texto, medidor, ancho, tope)
    else:
        ancho1 = medidor.text_length(texto, fontsize=1.0)
        tamano = tope if ancho1 <= 0 else max(5.5, min(tope, ancho / ancho1))
    linea_base = (y0 + y1) / 2 + tamano * 0.18
    # Centrado horizontal solo para la fila YEAR/MAKE/MODEL y VIN (y ~298-310)
    x_text = x0 + 1
    try:
        is_fila_centrar = 295 <= y0 <= 312 and (x1 - x0) < 135
        if is_fila_centrar:
            tw = medidor.text_length(texto, fontsize=tamano)
            x_text = x0 + (x1 - x0 - tw) / 2
            if x_text < x0 + 1:
                x_text = x0 + 1
    except Exception:
        x_text = x0 + 1
    fontfile = RUTA_CALIBRI_BOLD if fuente == FUENTE_NEGRITA else RUTA_CALIBRI
    if not os.path.exists(fontfile):
        fontfile = None
    pagina.insert_text(
        (x_text, linea_base),
        texto,
        fontsize=tamano,
        fontname=fuente if fontfile else "helv",
        fontfile=fontfile,
        color=(0, 0, 0),
        overlay=True,
    )


def abrir_pdf_para_imprimir(buffer, titulo):
    """Abre el PDF en el navegador y lo imprime directo (sin guardar archivo),
    bloqueandolo contra edicion (solo se permite imprimir)."""
    doc = pymupdf.open(stream=buffer.getvalue(), filetype="pdf")
    doc.set_metadata({"title": titulo})
    try:
        js = "this.print({bUI:false,bSilent:true,bShrinkToFit:true});"
        xref = doc.get_new_xref()
        doc.update_object(
            xref,
            "<< /S /JavaScript /JS <{}> >>".format(js.encode("utf-8").hex().upper()),
        )
        doc.xref_set_key(doc.pdf_catalog(), "OpenAction", "{} 0 R".format(xref))
    except Exception:
        pass
    salida = io.BytesIO()
    doc.save(
        salida,
        garbage=4,
        deflate=True,
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        owner_pw=secrets.token_hex(16),
        user_pw="",
        permissions=pymupdf.PDF_PERM_PRINT,
    )
    doc.close()
    salida.seek(0)
    return salida


def generar_tarjeta(template_path, datos):
    hora = (datos.get("hora") or HORA_EJEMPLO).strip() or HORA_EJEMPLO
    hora_expiracion = re.sub(r"\s+[A-Za-z]{1,5}$", "", hora).strip() or hora
    valores = {
        "numero_poliza": (datos.get("numero_poliza") or "").upper(),
        "fecha_inicio": "{} {}".format(_formatear_fecha(datos.get("fecha_inicio")), hora),
        "fecha_expiracion": "{} {}".format(_formatear_fecha(datos.get("fecha_expiracion")), hora_expiracion),
        "nombre": (datos.get("nombre") or "").upper(),
        "direccion": (datos.get("direccion") or "").upper(),
        "codigo_postal": (datos.get("codigo_postal") or "").upper(),
        "anio_marca_modelo": " ".join(
            parte for parte in [
                datos.get("anio"),
                datos.get("marca"),
                datos.get("modelo"),
            ] if parte
        ).upper(),
        "vin": (datos.get("vin") or "").upper(),
        "conductor": (datos.get("nombre") or "").upper(),
    }

    doc = pymupdf.open(template_path)
    pagina = doc[0]
    medidas = _medidas_tinta(pagina, ("fecha_inicio", "fecha_expiracion"))
    _aplicar_redaccion(pagina, medidas)
    _cargar_fuentes(pagina)

    for campo, rects in RECTS.items():
        texto = valores.get(campo)
        if not texto:
            continue
        fuente = FUENTE_NEGRITA if campo == "vin" else FUENTE_REGULAR
        medidor = _MEDIDOR_NEGRITA if campo == "vin" else _MEDIDOR_REGULAR
        tope = TAMANOS[campo]
        for i, rect in enumerate(rects):
            par = medidas.get(campo, [None, None])[i] if campo in medidas else None
            fin = par[1] if isinstance(par, (tuple, list)) else par
            ini = par[0] if isinstance(par, (tuple, list)) else None
            _dibujar_campo(pagina, rect, texto, fuente, medidor, tope, fin)

    buffer = io.BytesIO()
    doc.save(buffer, garbage=3)
    doc.close()
    buffer.seek(0)
    return buffer
