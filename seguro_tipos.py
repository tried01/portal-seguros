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
    ("auto", "Falcon TX", "plantilla_auto.pdf", "16:50 PM CT", "TX"),
    ("auto_az", "Falcon AZ", "SG_FIC_ARIZONA_CORTO.pdf", "12:00 PM CT", "AZ"),
    ("auto_co", "Falcon CO", "SG_FIC_COLORADO_CORTO.pdf", "05:00 PM CT", "CO"),
    ("auto_ga", "Falcon GA", "SG_FIC_GEORGIA_CORTO.pdf", "06:00 PM CT", "GA"),
    ("auto_il", "Falcon IL", "SG_FIC_ILINOIS_CORTO.pdf", "01:00 PM CT", "IL"),
    ("auto_ne", "Falcon NE", "SG_FIC_NEBRASKA.pdf", "05:00 PM CT", "NE"),
    ("auto_nm", "Falcon NM", "SG_FIC_NEW.MEXICO.pdf", "04:00 PM CT", "NM"),
    ("auto_ut", "Falcon UT", "SG_FIC_UTAH_CORTO.pdf", "08:00 AM CT", "UT"),
    ("auto_wa", "Falcon WA", "SG_FIC_WASHINGTON_CORTO.pdf", "06:00 PM CT", "WA"),
]

SEGUROS = {
    seguro_id: {
        "nombre": nombre,
        "descripcion": f"Politica de vehiculo {nombre}.",
        "plantilla": plantilla,
        "tipo_plantilla": "tarjeta",
        "codigo_estado": codigo,
        "campos": _campos(hora),
        "mapping": dict(MAPPING),
    }
    for seguro_id, nombre, plantilla, hora, codigo in ESTADOS
}


def obtener_seguro(seguro_id):
    return SEGUROS.get(seguro_id)