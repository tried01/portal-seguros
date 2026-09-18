from io import BytesIO

from pypdf import PdfReader, PdfWriter


def listar_campos_pdf(path):
    try:
        reader = PdfReader(path)
    except Exception:
        return {}
    campos = reader.get_fields()
    if not campos:
        return {}
    return {nombre: (campo.get("/FT") or "desconocido") for nombre, campo in campos.items()}


def generar_pdf_relleno(template_path, datos, mapping):
    reader = PdfReader(template_path)
    writer = PdfWriter()
    if hasattr(writer, "clone_reader_document_root"):
        writer.clone_reader_document_root(reader)
    else:
        writer.append(reader)

    campos_plantilla = set(reader.get_fields().keys()) if reader.get_fields() else set()
    valores = {}
    rellenados = []
    omitidos = []

    for clave_form, nombre_campo in mapping.items():
        if not nombre_campo:
            continue
        if nombre_campo not in campos_plantilla:
            omitidos.append(nombre_campo)
            continue
        valor = datos.get(clave_form)
        if valor is None:
            continue
        valor = str(valor).strip()
        if valor:
            valores[nombre_campo] = valor
            rellenados.append(nombre_campo)

    if valores:
        for pagina in writer.pages:
            writer.update_page_form_field_values(pagina, valores)
        writer.set_need_appearances_writer(True)

    buffer = BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return buffer


def plantilla_existe(ruta):
    from os.path import getsize

    try:
        return getsize(ruta) > 0
    except OSError:
        return False