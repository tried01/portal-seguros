from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

ANCHO, ALTO = A4

AZUL = HexColor("#1F4E78")
GRIS = HexColor("#555555")
CELESTE = HexColor("#DCE9F5")

CAMPOS_AUTO = [
    ("nombre", "Nombre del Titular"),
    ("direccion", "Direccion"),
    ("codigo_postal", "Codigo Postal"),
    ("fecha_inicio", "Fecha de Inicio"),
    ("fecha_expiracion", "Fecha de Expiracion"),
    ("numero_poliza", "Nro de Poliza"),
    ("marca", "Marca"),
    ("modelo", "Modelo"),
    ("anio", "Anio"),
    ("vin", "VIN del Vehiculo"),
]


def generar_plantilla_auto(output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    c.setTitle("Cotizacion de Seguro de Vehiculo")

    c.setFillColor(AZUL)
    c.rect(0, ALTO - 90, ANCHO, 90, stroke=0, fill=1)

    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 20)
    c.drawString(40, ALTO - 45, "COTIZACION DE SEGURO DE VEHICULO")

    c.setFont("Helvetica", 11)
    c.drawString(40, ALTO - 65, "Aseguradora Ejemplo S.A.  |  RIF: J-00000000-0  |  www.aseguradora.com")

    c.setFillColor(CELESTE)
    c.rect(30, ALTO - 108, ANCHO - 60, 24, stroke=0, fill=1)
    c.setFillColor(AZUL)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(42, ALTO - 92, "DATOS DEL ASEGURADO Y DEL VEHICULO")

    ancho_campo = (ANCHO - 120) / 2
    col1_x = 42
    col2_x = 42 + ancho_campo + 36

    def campo(nombre, etiqueta, x, top, alto=24):
        base = ALTO - top - alto
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 9)
        c.drawString(x, base + alto - 4, etiqueta)
        c.acroForm.textfield(
            name=nombre,
            x=x,
            y=base,
            width=ancho_campo,
            height=alto - 10,
            borderColor=AZUL,
            borderStyle="inset",
            fillColor=HexColor("#FFFFFF"),
            forceBorder=True,
            textColor=HexColor("#000000"),
            fontSize=9,
        )
        return alto + 14

    top = 128
    medio = -(-len(CAMPOS_AUTO) // 2)
    col1 = CAMPOS_AUTO[:medio]
    col2 = CAMPOS_AUTO[medio:]

    top_actual = top
    for item in col1:
        nombre, etiqueta = item[0], item[1]
        alto = item[2] if len(item) > 2 else 24
        top_actual += campo(nombre, etiqueta, col1_x, top_actual, alto)

    top_actual = top
    for item in col2:
        nombre, etiqueta = item[0], item[1]
        alto = item[2] if len(item) > 2 else 24
        top_actual += campo(nombre, etiqueta, col2_x, top_actual, alto)

    c.setFont("Helvetica", 7)
    c.setFillColor(GRIS)
    c.drawString(40, 40, "Documento generado automaticamente por el Portal de Seguros.")

    c.showPage()
    c.save()