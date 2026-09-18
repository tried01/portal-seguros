import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_generator import listar_campos_pdf

if len(sys.argv) < 2:
    print("Uso: python ver_campos_pdf.py <ruta_del_pdf>")
    sys.exit(1)

ruta = sys.argv[1]
campos = listar_campos_pdf(ruta)

if not campos:
    print("No se encontraron campos de formulario en el PDF.")
    print("Recuerda: el PDF debe tener casillas editables (AcroForm).")
    sys.exit(0)

print(f"Campos encontrados en {ruta}:\n")
for nombre, tipo in sorted(campos.items()):
    print(f"  {nombre:30s} ({tipo})")

print("\nCopia estos nombres exactos en el 'mapping' de 'seguro_tipos.py'.")