TEXTO = "text"
NUMERO = "number"
FECHA = "date"
EMAIL = "email"
TELEFONO = "tel"
SELECCION = "select"


def _campos(hora_por_defecto):
    return [
        {"name": "numero_poliza", "label": "Nro de Poliza", "tipo": TEXTO, "obligatorio": True},
        {"name": "nombre", "label": "Nombre del Titular", "tipo": TEXTO, "obligatorio": True},
        {"name": "direccion", "label": "Direccion", "tipo": TEXTO, "obligatorio": True},
        {"name": "codigo_postal", "label": "Codigo Postal", "tipo": TEXTO, "obligatorio": True},
        {"name": "fecha_inicio", "label": "Fecha de Inicio", "tipo": FECHA, "obligatorio": True},
        {"name": "fecha_expiracion", "label": "Fecha de Expiracion", "tipo": FECHA, "obligatorio": True},
        {"name": "hora", "label": "Hora", "tipo": TEXTO, "obligatorio": True, "valor": hora_por_defecto},
        {"name": "marca", "label": "Marca del Vehiculo", "tipo": TEXTO, "obligatorio": True},
        {"name": "modelo", "label": "Modelo", "tipo": TEXTO, "obligatorio": True},
        {"name": "anio", "label": "Año", "tipo": NUMERO, "obligatorio": True},
        {"name": "vin", "label": "VIN del Vehiculo", "tipo": TEXTO, "obligatorio": True},
    ]


def _campos_completo(hora_por_defecto):
    # Campos para SG_FIC_CP_Tx.pdf (Amended Policy Declarations) — todo lo marcado en la foto
    base = _campos(hora_por_defecto)
    # Campos adicionales específicos del completo
    extra = [
        {"name": "processed_date", "label": "Processed Date", "tipo": FECHA, "obligatorio": True},
        {"name": "agent_number", "label": "Agent Number", "tipo": TEXTO, "obligatorio": False},
        {"name": "millas", "label": "Millas", "tipo": TEXTO, "obligatorio": False},
        {"name": "territory", "label": "Territory", "tipo": TEXTO, "obligatorio": False},
        {"name": "symbol", "label": "Symbol", "tipo": TEXTO, "obligatorio": False},
        {"name": "veh_total", "label": "Vehicle Total", "tipo": TEXTO, "obligatorio": False},
        {"name": "total_policy", "label": "Total for Policy Coverages", "tipo": TEXTO, "obligatorio": False},
        {"name": "total_fees", "label": "TOTAL FEES", "tipo": TEXTO, "obligatorio": False},
        {"name": "final_total", "label": "FINAL TOTAL", "tipo": TEXTO, "obligatorio": False},
        {"name": "driver_name", "label": "Driver Name", "tipo": TEXTO, "obligatorio": True},
        {"name": "driver_type", "label": "Driver Type", "tipo": TEXTO, "obligatorio": False, "valor": "Principal"},
        {"name": "driver_edad", "label": "Driver Age", "tipo": NUMERO, "obligatorio": False},
        {"name": "driver_genero", "label": "Driver Gender", "tipo": SELECCION, "obligatorio": False, "opciones": ["Male", "Female", "Other"]},
        {"name": "driver_status", "label": "Driver Status", "tipo": TEXTO, "obligatorio": False},
        {"name": "sr22", "label": "SR22", "tipo": SELECCION, "obligatorio": False, "opciones": ["No", "Yes"]},
        {"name": "points", "label": "Points", "tipo": NUMERO, "obligatorio": False},
        {"name": "counter_signed", "label": "Counter Signed Date", "tipo": FECHA, "obligatorio": False},
    ]
    return base + extra


MAPPING = {
    "numero_poliza": "numero_poliza",
    "nombre": "nombre",
    "direccion": "direccion",
    "codigo_postal": "codigo_postal",
    "fecha_inicio": "fecha_inicio",
    "fecha_expiracion": "fecha_expiracion",
    "marca": "marca",
    "modelo": "modelo",
    "anio": "anio",
    "vin": "vin",
}

ESTADOS = [
    ("auto", "Falcon TX", "plantilla_auto.pdf", "16:50 PM CT", "TX", "basico"),
    ("auto_az", "Falcon AZ", "SG_FIC_ARIZONA_CORTO.pdf", "12:00 PM CT", "AZ", "basico"),
    ("auto_co", "Falcon CO", "SG_FIC_COLORADO_CORTO.pdf", "05:00 PM CT", "CO", "basico"),
    ("auto_ga", "Falcon GA", "SG_FIC_GEORGIA_CORTO.pdf", "06:00 PM CT", "GA", "basico"),
    ("auto_il", "Falcon IL", "SG_FIC_ILINOIS_CORTO.pdf", "01:00 PM CT", "IL", "basico"),
    ("auto_ne", "Falcon NE", "SG_FIC_NEBRASKA.pdf", "05:00 PM CT", "NE", "basico"),
    ("auto_nm", "Falcon NM", "SG_FIC_NEW.MEXICO.pdf", "04:00 PM CT", "NM", "basico"),
    ("auto_ut", "Falcon UT", "SG_FIC_UTAH_CORTO.pdf", "08:00 AM CT", "UT", "basico"),
    ("auto_wa", "Falcon WA", "SG_FIC_WASHINGTON_CORTO.pdf", "06:00 PM CT", "WA", "basico"),
    # Modelos completos — agrega aquí los nuevos PDFs completos
    ("auto_completo_cp", "Falcon CP TX", "SG_FIC_CP_Tx.pdf", "16:50 PM CT", "TX", "completo"),
]

SEGUROS = {
    seguro_id: {
        "nombre": nombre,
        "descripcion": f"Politica de vehiculo {nombre}.",
        "plantilla": plantilla,
        "tipo_plantilla": "tarjeta" if categoria == "basico" else "completo",
        "codigo_estado": codigo,
        "categoria": categoria,
        "campos": _campos_completo(hora) if categoria == "completo" else _campos(hora),
        "mapping": dict(MAPPING),
    }
    for seguro_id, nombre, plantilla, hora, codigo, categoria in ESTADOS
}


def obtener_seguro(seguro_id):
    return SEGUROS.get(seguro_id)