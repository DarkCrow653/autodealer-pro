from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ── Configuración ──────────────────────────────────────────────────────────────
# En Render: ajusta la variable de entorno SECRET_KEY en el dashboard.
# En local: funciona con el valor por defecto.
app.secret_key = os.environ.get("SECRET_KEY", "autodealer_dev_key_change_in_production")

# Rutas absolutas → funcionan sin importar desde dónde Render ejecute la app
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DB_PATH      = os.path.join(BASE_DIR, "database.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "img", "autos")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Auto-inicialización de la base de datos ────────────────────────────────────
# En Render la DB no existe en el primer deploy; esta función la crea
# automáticamente con datos de ejemplo si no encuentra el archivo.
def init_db_if_needed():
    if os.path.exists(DB_PATH):
        return  # Ya existe, no hacer nada

    print("⚙️  Base de datos no encontrada. Creando con datos de ejemplo...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS autos (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        marca        TEXT NOT NULL,
        modelo       TEXT NOT NULL,
        precio       INTEGER NOT NULL,
        anio         INTEGER,
        kilometraje  INTEGER,
        combustible  TEXT DEFAULT 'Gasolina',
        transmision  TEXT DEFAULT 'Manual',
        descripcion  TEXT,
        imagen       TEXT DEFAULT 'default.jpg',
        destacado    INTEGER DEFAULT 0
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )""")

    cursor.execute("INSERT INTO usuarios (username, password) VALUES ('admin', '1234')")

    autos_sample = [
        ("Toyota", "Camry XSE", 28500, 2023, 12000, "Gasolina", "Automática",
         "Sedán mediano con motor V6, techo solar y asistente de manejo.", "default.jpg", 1),
        ("BMW", "Serie 3 320i", 42000, 2022, 25000, "Gasolina", "Automática",
         "Sedán deportivo con motor turbo 2.0L e interior premium.", "default.jpg", 1),
        ("Ford", "Mustang GT", 39800, 2023, 8000, "Gasolina", "Manual",
         "Muscle car con motor V8 5.0L, 460 HP y frenos Brembo.", "default.jpg", 1),
        ("Honda", "Civic Sport", 24900, 2023, 15000, "Gasolina", "Automática",
         "Compacto deportivo con motor turbo 1.5L.", "default.jpg", 0),
        ("Tesla", "Model 3", 46990, 2023, 5000, "Eléctrico", "Automática",
         "Sedán eléctrico con autonomía de 576 km y Autopilot.", "default.jpg", 1),
        ("Chevrolet", "Equinox RS", 31500, 2022, 32000, "Gasolina", "Automática",
         "SUV compacta con tracción AWD.", "default.jpg", 0),
        ("Audi", "A4 40 TFSI", 47500, 2022, 18000, "Gasolina", "Automática",
         "Sedán ejecutivo con Virtual Cockpit 12.3\".", "default.jpg", 1),
        ("Nissan", "Sentra SR", 22400, 2023, 20000, "Gasolina", "Automática",
         "Sedán compacto con pantalla de 8 pulgadas.", "default.jpg", 0),
        ("Mercedes-Benz", "Clase C 200", 54000, 2023, 9000, "Gasolina", "Automática",
         "Clase C con pantalla MBUX de 11.9 pulgadas.", "default.jpg", 1),
        ("Volkswagen", "Jetta TSI", 26900, 2023, 11000, "Gasolina", "Automática",
         "Sedán alemán con motor TSI 1.4L.", "default.jpg", 0),
    ]

    cursor.executemany("""
    INSERT INTO autos (marca, modelo, precio, anio, kilometraje, combustible,
                       transmision, descripcion, imagen, destacado)
    VALUES (?,?,?,?,?,?,?,?,?,?)
    """, autos_sample)

    conn.commit()
    conn.close()
    print(f"✅ DB creada: {len(autos_sample)} autos de ejemplo, usuario admin/1234")


# Ejecutar al importar el módulo (Gunicorn lo hace al arrancar)
init_db_if_needed()


def format_price(value):
    """Format number as currency string"""
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


app.jinja_env.filters['format_price'] = format_price


# ================= PUBLIC =================

@app.route("/")
def index():
    conn = db()
    destacados = conn.execute(
        "SELECT * FROM autos WHERE destacado=1 ORDER BY id DESC LIMIT 6"
    ).fetchall()
    recientes = conn.execute(
        "SELECT * FROM autos ORDER BY id DESC LIMIT 3"
    ).fetchall()
    total_autos = conn.execute("SELECT COUNT(*) FROM autos").fetchone()[0]
    total_marcas = conn.execute("SELECT COUNT(DISTINCT marca) FROM autos").fetchone()[0]
    conn.close()
    return render_template(
        "index.html",
        destacados=destacados,
        recientes=recientes,
        total_autos=total_autos,
        total_marcas=total_marcas
    )


@app.route("/catalogo")
def catalogo():
    buscar = request.args.get("buscar", "")
    combustible_filter = request.args.get("combustible", "")
    transmision_filter = request.args.get("transmision", "")
    orden = request.args.get("orden", "reciente")

    conn = db()

    query = "SELECT * FROM autos WHERE 1=1"
    params = []

    if buscar:
        query += " AND (marca LIKE ? OR modelo LIKE ? OR descripcion LIKE ?)"
        params.extend(['%' + buscar + '%', '%' + buscar + '%', '%' + buscar + '%'])

    if combustible_filter:
        query += " AND combustible = ?"
        params.append(combustible_filter)

    if transmision_filter:
        query += " AND transmision = ?"
        params.append(transmision_filter)

    if orden == "precio_asc":
        query += " ORDER BY CAST(precio AS INTEGER) ASC"
    elif orden == "precio_desc":
        query += " ORDER BY CAST(precio AS INTEGER) DESC"
    elif orden == "anio_desc":
        query += " ORDER BY anio DESC NULLS LAST"
    else:
        query += " ORDER BY id DESC"

    autos = conn.execute(query, params).fetchall()
    destacados = conn.execute(
        "SELECT * FROM autos WHERE destacado=1 ORDER BY id DESC LIMIT 4"
    ).fetchall()
    conn.close()

    return render_template(
        "catalogo.html",
        autos=autos,
        destacados=destacados,
        buscar=buscar,
        combustible_filter=combustible_filter,
        transmision_filter=transmision_filter,
        orden=orden,
        total_resultados=len(autos)
    )


@app.route("/auto/<int:id>")
def auto(id):
    conn = db()
    auto = conn.execute("SELECT * FROM autos WHERE id=?", (id,)).fetchone()
    if not auto:
        conn.close()
        return redirect("/catalogo")
    relacionados = conn.execute(
        "SELECT * FROM autos WHERE marca=? AND id!=? LIMIT 3",
        (auto['marca'], id)
    ).fetchall()
    conn.close()
    return render_template("detalle_auto.html", auto=auto, relacionados=relacionados)


# ================= LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = db()
        user = conn.execute(
            "SELECT * FROM usuarios WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["admin"] = True
            session["username"] = username
            return redirect("/admin")
        else:
            error = "Usuario o contraseña incorrectos"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ================= ADMIN =================

@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/login")

    conn = db()

    autos = conn.execute("SELECT * FROM autos ORDER BY id DESC").fetchall()
    total_autos = conn.execute("SELECT COUNT(*) FROM autos").fetchone()[0]
    total_destacados = conn.execute(
        "SELECT COUNT(*) FROM autos WHERE destacado=1"
    ).fetchone()[0]

    avg_row = conn.execute("SELECT AVG(CAST(precio AS REAL)) FROM autos").fetchone()[0]
    avg_precio = round(avg_row) if avg_row else 0

    total_marcas = conn.execute(
        "SELECT COUNT(DISTINCT marca) FROM autos WHERE marca IS NOT NULL AND marca != ''"
    ).fetchone()[0]

    precio_max = conn.execute(
        "SELECT MAX(CAST(precio AS INTEGER)) FROM autos"
    ).fetchone()[0] or 0

    precio_min = conn.execute(
        "SELECT MIN(CAST(precio AS INTEGER)) FROM autos WHERE precio > 0"
    ).fetchone()[0] or 0

    # Data for charts
    marcas_data = conn.execute(
        "SELECT marca, COUNT(*) as count FROM autos WHERE marca IS NOT NULL AND marca != '' "
        "GROUP BY marca ORDER BY count DESC LIMIT 8"
    ).fetchall()

    combustible_data = conn.execute(
        "SELECT combustible, COUNT(*) as count FROM autos "
        "WHERE combustible IS NOT NULL AND combustible != '' GROUP BY combustible"
    ).fetchall()

    transmision_data = conn.execute(
        "SELECT transmision, COUNT(*) as count FROM autos "
        "WHERE transmision IS NOT NULL AND transmision != '' GROUP BY transmision"
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        autos=autos,
        total_autos=total_autos,
        total_destacados=total_destacados,
        avg_precio=avg_precio,
        total_marcas=total_marcas,
        precio_max=precio_max,
        precio_min=precio_min,
        marcas_data=marcas_data,
        combustible_data=combustible_data,
        transmision_data=transmision_data
    )


@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if "admin" not in session:
        return redirect("/login")

    if request.method == "POST":
        marca = request.form.get("marca", "").strip()
        modelo = request.form.get("modelo", "").strip()
        precio = request.form.get("precio", 0)
        anio = request.form.get("anio") or None
        kilometraje = request.form.get("kilometraje") or None
        combustible = request.form.get("combustible", "Gasolina")
        transmision = request.form.get("transmision", "Manual")
        descripcion = request.form.get("descripcion", "").strip()
        destacado = 1 if request.form.get("destacado") else 0

        imagen = request.files.get("imagen")
        filename = "default.jpg"

        if imagen and imagen.filename != "" and allowed_file(imagen.filename):
            filename = secure_filename(imagen.filename)
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            ruta = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            imagen.save(ruta)

        conn = db()
        conn.execute(
            """INSERT INTO autos 
               (marca, modelo, precio, anio, kilometraje, combustible, 
                transmision, descripcion, imagen, destacado)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (marca, modelo, precio, anio, kilometraje, combustible,
             transmision, descripcion, filename, destacado)
        )
        conn.commit()
        conn.close()

        return redirect("/admin")

    return render_template("agregar_auto.html")


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if "admin" not in session:
        return redirect("/login")

    conn = db()

    if request.method == "POST":
        marca = request.form.get("marca", "").strip()
        modelo = request.form.get("modelo", "").strip()
        precio = request.form.get("precio", 0)
        anio = request.form.get("anio") or None
        kilometraje = request.form.get("kilometraje") or None
        combustible = request.form.get("combustible", "Gasolina")
        transmision = request.form.get("transmision", "Manual")
        descripcion = request.form.get("descripcion", "").strip()
        destacado = 1 if request.form.get("destacado") else 0

        imagen = request.files.get("imagen")
        if imagen and imagen.filename != "" and allowed_file(imagen.filename):
            filename = secure_filename(imagen.filename)
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            ruta = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            imagen.save(ruta)
            conn.execute(
                """UPDATE autos SET marca=?, modelo=?, precio=?, anio=?, kilometraje=?,
                   combustible=?, transmision=?, descripcion=?, imagen=?, destacado=?
                   WHERE id=?""",
                (marca, modelo, precio, anio, kilometraje, combustible,
                 transmision, descripcion, filename, destacado, id)
            )
        else:
            conn.execute(
                """UPDATE autos SET marca=?, modelo=?, precio=?, anio=?, kilometraje=?,
                   combustible=?, transmision=?, descripcion=?, destacado=?
                   WHERE id=?""",
                (marca, modelo, precio, anio, kilometraje, combustible,
                 transmision, descripcion, destacado, id)
            )

        conn.commit()
        conn.close()
        return redirect("/admin")

    auto = conn.execute("SELECT * FROM autos WHERE id=?", (id,)).fetchone()
    conn.close()

    if not auto:
        return redirect("/admin")

    return render_template("editar_auto.html", auto=auto)


@app.route("/destacar/<int:id>")
def destacar(id):
    if "admin" not in session:
        return redirect("/login")

    conn = db()
    auto = conn.execute("SELECT destacado FROM autos WHERE id=?", (id,)).fetchone()
    if auto:
        nuevo = 0 if auto['destacado'] else 1
        conn.execute("UPDATE autos SET destacado=? WHERE id=?", (nuevo, id))
        conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/borrar/<int:id>")
def borrar(id):
    if "admin" not in session:
        return redirect("/login")

    conn = db()
    conn.execute("DELETE FROM autos WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=False)
