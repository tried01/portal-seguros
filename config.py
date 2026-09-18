import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
TEMPLATES_PDF_DIR = os.path.join(BASE_DIR, "templates_pdf")

DATABASE_PATH = os.path.join(DATA_DIR, "portal.db")

SECRET_KEY = "cambia-esta-clave-en-produccion"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEMPLATES_PDF_DIR, exist_ok=True)