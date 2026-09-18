from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

AZUL = colors.HexColor("#1F4E78")
CELESTE = colors.HexColor("#DCE9F5")
GRIS = colors.HexColor("#555555")


def generar_pdf_generico(titulo, subtitulo, pares):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=25 * mm,
        bottomMargin=20 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
    )

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "Titulo",
        parent=estilos["Title"],
        textColor=AZUL,
        fontSize=18,
        spaceAfter=2,
    )
    estilo_sub = ParagraphStyle(
        "Subtitulo",
        parent=estilos["Normal"],
        textColor=GRIS,
        fontSize=9,
        spaceAfter=6,
    )
    estilo_label = ParagraphStyle(
        "Etiqueta",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=AZUL,
    )
    estilo_valor = ParagraphStyle(
        "Valor",
        parent=estilos["Normal"],
        fontSize=9,
        textColor=colors.black,
    )

    elementos = [
        Paragraph(titulo, estilo_titulo),
        Paragraph(subtitulo, estilo_sub),
        HRFlowable(width="100%", thickness=1.2, color=AZUL, spaceAfter=12),
    ]

    filas = [[Paragraph(etiqueta, estilo_label), Paragraph(valor, estilo_valor)] for etiqueta, valor in pares]
    tabla = Table(filas, colWidths=[60 * mm, 110 * mm])
    tabla.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, CELESTE]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B0C4DE")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    elementos.append(tabla)
    elementos.append(Spacer(1, 10 * mm))
    elementos.append(
        Paragraph("Documento generado automaticamente por el Portal de Seguros.", estilo_sub)
    )

    doc.build(elementos)
    buffer.seek(0)
    return buffer