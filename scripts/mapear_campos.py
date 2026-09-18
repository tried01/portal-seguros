import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TEMPLATES_PDF_DIR
from pdf_generator import listar_campos_pdf
from seguro_tipos import SEGUROS

SINONIMOS = {
    "numero_poliza": ["poliza"],
    "nombre": ["nombre", "titular"],
    "direccion": ["direccion"],
    "codigo_postal": ["codigopostal", "postal", "zip"],
    "fecha_inicio": ["fechainicio", "inicio", "desde"],
    "fecha_expiracion": ["expiracion", "expira", "vencimiento", "venci", "hasta"],
    "marca": ["marca"],
    "modelo": ["modelo"],
    "anio": ["anio", "ano", "year"],
    "vin": ["vin"],
}


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", texto.lower())


def buscar_mejor(campo_portal, campos_pdf):
    objetivo = normalizar(campo_portal)
    for nombre in campos_pdf:
        if normalizar(nombre) == objetivo:
            return nombre, "exacto"

    sinonimos = [normalizar(s) for s in SINONIMOS.get(campo_portal, [objetivo])]
    candidatos = []
    for nombre in campos_pdf:
        candidato = normalizar(nombre)
        for s in sinonimos:
            if s in candidato or candidato in s:
                candidatos.append(nombre)
                break
    if candidatos:
        mejor = sorted(candidatos, key=len)[0]
        return mejor, "parcial"
    return None, None


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(TEMPLATES_PDF_DIR, "plantilla_auto.pdf")
    if not os.path.exists(ruta):
        print(f"No existe el archivo: {ruta}")
        sys.exit(1)

    campos_pdf = listar_campos_pdf(ruta)
    if not campos_pdf:
        print("El PDF no tiene campos de formulario (AcroForm).")
        sys.exit(1)

    print(f"Campos encontrados en tu PDF ({len(campos_pdf)}):")
    for nombre in sorted(campos_pdf):
        print(f"    - {nombre}")

    portal = [c["name"] for c in SEGUROS["auto"]["campos"]]

    print("\nEmparejando con el formulario del portal:\n")
    mapping = {}
    faltan = []
    for campo_portal in portal:
        encontrado, tipo = buscar_mejor(campo_portal, list(campos_pdf.keys()))
        if encontrado:
            mapping[campo_portal] = encontrado
            print(f"    OK   {campo_portal:20s} -> {encontrado}")
        else:
            faltan.append(campo_portal)
            print(f"    FALTA {campo_portal:20s} -> (sin coincidencia)")

    salida = os.path.join(TEMPLATES_PDF_DIR, "mapping_auto.json")
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"\nMapping guardado en: {salida}")
    if faltan:
        print("\nCampos sin emparejar: " + ", ".join(faltan))
        print("Abre el archivo mapping_auto.json y escribe a mano el nombre exacto de la casilla.")
    else:
        print("Todos los campos emparejados. Ya puedes tramitar el seguro.")


if __name__ == "__main__":
    main()