# -*- coding: utf-8 -*-
"""Renderer para SG_FIC_CP_Tx.pdf (Amended Policy Declarations).
Cubre todo lo marcado en la foto: policy, fechas, titular, vehículo, coberturas, driver, totales, counter signed.
Usa misma fuente Calibri que las tarjetas y fechas MM/DD/YYYY.
"""
import io
import os
import re
from datetime import datetime

import pymupdf

FUENTE = "helv"

# RECTS medidos directamente de la plantilla (bbox de los valores + margen)
RECTS_CP = {
    # Top
    "processed_date": [(439.0, 14.0, 520.0, 24.5)],
    # Policy block
    "numero_poliza": [(98.0, 98.5, 160.0, 111.0)],
    "fecha_inicio": [(423.0, 98.5, 514.0, 111.0)],  # Jun 02, 2026 10:10 AM
    "fecha_expiracion": [(425.0, 109.5, 514.0, 122.0)],  # Sep 02, 2026 10:10 AM
    # Policyholder (3 líneas en un solo rect para redactar)
    "nombre": [(76.0, 139.0, 200.0, 153.0)],  # Carlos Fernandez Chember
    "direccion": [(76.0, 152.0, 200.0, 173.5)],  # 4300 Cornhusker..., Lincoln...
    # Insured Vehicle
    "anio_marca_modelo": [(44.0, 204.5, 136.0, 215.5)],  # 2013 HYUNDAI SONATA
    "vin": [(194.0, 203.0, 274.0, 215.5)],  # 5NPEB4AC3DH800462
    "millas": [(310.0, 203.0, 338.0, 215.5)],  # 122565
    "territory": [(395.0, 203.0, 402.0, 215.5)],  # 5
    "symbol": [(431.0, 203.0, 458.0, 215.5)],  # 32 / 26
    # Schedule of Coverages - columna Veh 1 (todos los $)
    "cover_veh1": [(410.0, 268.0, 433.0, 420.0)],  # columna de montos Veh1 (se redacta junto)
    # Totales
    "veh_total": [(419.0, 404.5, 439.0, 417.0)],  # $180
    "total_policy": [(550.0, 429.0, 588.0, 441.0)],  # $180 (parte numerica de Total for Policy)
    "prorated": [(558.0, 440.0, 580.0, 452.0)],  # -$0.00 / 0.00
    "total_fees": [(445.0, 451.0, 480.0, 463.0)],  # $160
    "final_total": [(545.0, 462.0, 578.0, 474.0)],  # $180
    # Driver(s)
    "driver_name": [(40.0, 529.5, 140.0, 542.5)],  # Carlos Fernandez Chember
    "driver_type": [(204.0, 529.5, 236.0, 542.0)],  # Principal
    "driver_edad": [(268.0, 531.0, 280.0, 543.0)],  # 27
    "driver_genero": [(308.0, 529.5, 328.0, 542.0)],  # Male
    "driver_status": [(366.0, 529.0, 392.0, 541.5)],  # single
    "sr22": [(423.0, 529.5, 436.0, 542.0)],  # No
    "points": [(453.0, 529.5, 461.0, 542.0)],  # 0
    # Counter Signed
    "counter_signed": [(320.0, 709.0, 406.0, 722.0)],  # 06/02/2026
}

TAMANOS_CP = {
    "numero_poliza": 9.0,
    "fecha_inicio": 9.0,
    "fecha_expiracion": 9.0,
    "nombre": 9.0,
    "direccion": 8.5,
    "anio_marca_modelo": 8.5,
    "vin": 8.5,
    "millas": 8.5,
    "territory": 8.5,
    "symbol": 8.5,
    "cover_veh1": 8.0,
    "veh_total": 9.0,
    "total_policy": 9.0,
    "prorated": 9.0,
    "total_fees": 9.0,
    "final_total": 9.0,
    "driver_name": 8.5,
    "driver_type": 8.5,
    "driver_edad": 8.5,
    "driver_genero": 8.5,
    "driver_status": 8.5,
    "sr22": 8.5,
    "points": 8.5,
    "counter_signed": 9.0,
    "processed_date": 8.5,
}

def _formatear_fecha(valor):
    valor = (valor or "").strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%m-%d-%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(valor, fmt).strftime("%m/%d/%Y")
        except ValueError:
            continue
    return valor

def _texto_que_cabe(texto, font, ancho, tope):
    size = tope
    try:
        while size > 5.5 and font.text_length(texto, fontsize=size) > ancho:
            size -= 0.4
    except Exception:
        pass
    return size

def generar_completo(template_path, datos):
    # Fuente base helv (Calibri empaquetada se usa si existe, pero helv es seguro en Linux)
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        cal = os.path.join(base, "fonts", "calibri.ttf")
        if os.path.exists(cal):
            font = pymupdf.Font(fontfile=cal)
        else:
            font = pymupdf.Font("helv")
    except Exception:
        font = pymupdf.Font("helv")

    doc = pymupdf.open(template_path)
    page = doc[0]  # todo lo marcado está en página 0

    # Valores formateados MM/DD/YYYY
    valores = {}
    valores["numero_poliza"] = (datos.get("numero_poliza") or "").strip()
    # Fechas con hora si viene
    hora = (datos.get("hora") or "10:10 AM").strip()
    valores["fecha_inicio"] = f"{_formatear_fecha(datos.get('fecha_inicio'))}  {hora}".strip()
    valores["fecha_expiracion"] = f"{_formatear_fecha(datos.get('fecha_expiracion'))}  {hora}".strip()
    valores["processed_date"] = _formatear_fecha(datos.get("processed_date") or datos.get("fecha_inicio"))
    valores["nombre"] = (datos.get("nombre") or "").upper()
    # Direccion: puede venir con saltos, tomamos solo primera parte
    valores["direccion"] = (datos.get("direccion") or "").upper()
    valores["anio_marca_modelo"] = " ".join(p for p in [datos.get("anio"), datos.get("marca"), datos.get("modelo")] if p).upper()
    valores["vin"] = (datos.get("vin") or "").upper()
    valores["millas"] = (datos.get("millas") or "122565").upper()
    valores["territory"] = (datos.get("territory") or "5")
    valores["symbol"] = (datos.get("symbol") or "32 / 26")
    valores["cover_veh1"] = ""  # no se rellena por ahora (montos fijos)
    valores["veh_total"] = (datos.get("veh_total") or "$180")
    valores["total_policy"] = (datos.get("total_policy") or "$180")
    valores["prorated"] = (datos.get("prorated") or "-$0.00")
    valores["total_fees"] = (datos.get("total_fees") or "$160")
    valores["final_total"] = (datos.get("final_total") or "$180")
    valores["driver_name"] = (datos.get("driver_name") or datos.get("nombre") or "").upper()
    valores["driver_type"] = (datos.get("driver_type") or "Principal")
    valores["driver_edad"] = str(datos.get("driver_edad") or "27")
    valores["driver_genero"] = (datos.get("driver_genero") or "Male")
    valores["driver_status"] = (datos.get("driver_status") or "single")
    valores["sr22"] = (datos.get("sr22") or "No")
    valores["points"] = str(datos.get("points") or "0")
    valores["counter_signed"] = _formatear_fecha(datos.get("counter_signed") or datos.get("fecha_inicio"))

    # Redacción: borra todo lo existente en cada rect
    for campo, rects in RECTS_CP.items():
        for r in rects:
            page.add_redact_annot(pymupdf.Rect(*r))
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)

    # Cargar fuente para escritura
    try:
        cal = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "calibri.ttf")
        if os.path.exists(cal):
            page.insert_font(fontname="Calibri", fontfile=cal)
            fontname = "Calibri"
        else:
            fontname = "helv"
    except Exception:
        fontname = "helv"

    for campo, rects in RECTS_CP.items():
        texto = valores.get(campo, "")
        if not texto:
            continue
        for rect in rects:
            x0, y0, x1, y1 = rect
            ancho = x1 - x0 - 2
            tope = TAMANOS_CP.get(campo, 9.0)
            tam = _texto_que_cabe(texto, font, ancho, tope)
            # Centrado horizontal
            try:
                tw = font.text_length(texto, fontsize=tam)
                x = x0 + (x1 - x0 - tw) / 2
            except Exception:
                x = x0 + 1
            y = (y0 + y1) / 2 + tam * 0.3
            page.insert_text((x, y), texto, fontsize=tam, fontname=fontname, color=(0,0,0))

    buf = io.BytesIO()
    doc.save(buf, garbage=3)
    doc.close()
    buf.seek(0)
    return buf
