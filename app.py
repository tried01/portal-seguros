import json
import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from config import SECRET_KEY, TEMPLATES_PDF_DIR
from contador import nombre_archivo_pdf
from database import (
    cantidad_usuarios,
    crear_usuario,
    init_db,
    verificar_usuario,
)
from pdf_generator import generar_pdf_relleno, plantilla_existe
from pdf_generico import generar_pdf_generico
from pdf_tarjeta import abrir_pdf_para_imprimir, generar_tarjeta
from plantilla_generador import generar_plantilla_auto
from seguro_tipos import SEGUROS, obtener_seguro

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.context_processor
def inyectar_seguros():
    return {"seguros": SEGUROS}

init_db()

if cantidad_usuarios() == 0:
    crear_usuario("admin", "admin123", nombre="Administrador", rol="admin")

ruta_plantilla_auto = os.path.join(TEMPLATES_PDF_DIR, "plantilla_auto.pdf")
if not plantilla_existe(ruta_plantilla_auto):
    generar_plantilla_auto(ruta_plantilla_auto)


def cargar_mapping_tipo(seguro_id, mapping):
    ruta = os.path.join(TEMPLATES_PDF_DIR, f"mapping_{seguro_id}.json")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            try:
                override = json.load(f)
            except Exception:
                override = {}
        mapping = {**mapping, **override}
    return mapping


def requiere_login(funcion):
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        if "usuario" not in session:
            flash("Inicia sesion para continuar.", "error")
            return redirect(url_for("login"))
        return funcion(*args, **kwargs)

    return envoltura


@app.route("/login", methods=["GET", "POST"])
def login():
    if "usuario" in session:
        return redirect(url_for("inicio"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        usuario = verificar_usuario(username, password)
        if usuario:
            session["usuario"] = usuario["username"]
            session["nombre"] = usuario["nombre"]
            session["rol"] = usuario["rol"]
            return redirect(url_for("inicio"))
        flash("Usuario o contrasena incorrectos.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@requiere_login
def inicio():
    return render_template("tramites.html")


@app.route("/form/<seguro_id>")
@requiere_login
def formulario(seguro_id):
    seguro = obtener_seguro(seguro_id)
    if not seguro:
        flash("El seguro seleccionado no existe.", "error")
        return redirect(url_for("inicio"))
    return render_template(
        "formulario.html",
        seguro=seguro,
        seguro_id=seguro_id,
        fecha_hoy=datetime.now().strftime("%Y-%m-%d"),
    )


@app.route("/generar/<seguro_id>", methods=["POST"])
@requiere_login
def generar(seguro_id):
    seguro = obtener_seguro(seguro_id)
    if not seguro:
        flash("El seguro seleccionado no existe.", "error")
        return redirect(url_for("inicio"))

    datos = {campo["name"]: request.form.get(campo["name"], "").strip() for campo in seguro["campos"]}

    obligatorios_faltantes = [
        campo["label"]
        for campo in seguro["campos"]
        if campo.get("obligatorio") and not datos.get(campo["name"])
    ]
    if obligatorios_faltantes:
        for label in obligatorios_faltantes:
            flash(f"El campo {label} es obligatorio.", "error")
        return redirect(url_for("formulario", seguro_id=seguro_id))

    ruta_plantilla = os.path.join(TEMPLATES_PDF_DIR, seguro.get("plantilla", ""))
    tipo_plantilla = seguro.get("tipo_plantilla")
    mapping = cargar_mapping_tipo(seguro_id, seguro.get("mapping") or {})

    if tipo_plantilla == "tarjeta" and plantilla_existe(ruta_plantilla):
        buffer = generar_tarjeta(ruta_plantilla, datos)
        modo = "tarjeta"
    elif plantilla_existe(ruta_plantilla) and mapping:
        buffer = generar_pdf_relleno(ruta_plantilla, datos, mapping)
        modo = "plantilla"
    else:
        titulo = f"COTIZACION - {seguro['nombre']}".upper()
        subtitulo = f"Generada por {session.get('nombre') or session['usuario']} el {datetime.now().strftime('%m/%d/%Y %H:%M')}"
        pares = [(campo["label"], datos[campo["name"]] or "-") for campo in seguro["campos"]]
        buffer = generar_pdf_generico(titulo, subtitulo, pares)
        modo = "generico"

    nombre_archivo = nombre_archivo_pdf(seguro.get("codigo_estado", "TX"))
    base = os.path.splitext(nombre_archivo)[0]
    buffer = abrir_pdf_para_imprimir(buffer, base)

    response = send_file(
        buffer,
        as_attachment=False,
        download_name=nombre_archivo,
        mimetype="application/pdf",
    )
    # Asegura que al guardar desde el visor del celular use SG_FIC_TX_XXXX.pdf y no "auto.pdf" (URL)
    response.headers["Content-Disposition"] = f'inline; filename="{nombre_archivo}"; filename*=UTF-8\'\'{nombre_archivo}'
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)