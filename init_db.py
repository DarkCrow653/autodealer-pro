import sqlite3
import os

# Ruta absoluta para que funcione en cualquier entorno
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "database.db")

conexion = sqlite3.connect(DB_PATH)
cursor = conexion.cursor()

# Drop existing tables to recreate with updated schema
cursor.execute("DROP TABLE IF EXISTS autos")
cursor.execute("DROP TABLE IF EXISTS usuarios")

cursor.execute("""
CREATE TABLE autos (
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
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")

cursor.execute("""
INSERT INTO usuarios (username, password)
VALUES ('admin', '1234')
""")

# Sample inventory data
autos_sample = [
    ("Toyota", "Camry XSE", 28500, 2023, 12000, "Gasolina", "Automática",
     "Sedán mediano con motor V6, techo solar, sistema de infoentretenimiento de 9 pulgadas y asistente de manejo.", "default.jpg", 1),
    ("BMW", "Serie 3 320i", 42000, 2022, 25000, "Gasolina", "Automática",
     "El icónico sedán deportivo de BMW con motor turbo 2.0L, interior premium y tecnología ConnectedDrive.", "default.jpg", 1),
    ("Ford", "Mustang GT", 39800, 2023, 8000, "Gasolina", "Manual",
     "El legendario muscle car americano con motor V8 5.0L, 460 HP, frenos Brembo y diferencial electrónico.", "default.jpg", 1),
    ("Honda", "Civic Sport", 24900, 2023, 15000, "Gasolina", "Automática",
     "Compacto deportivo con diseño renovado, motor turbo 1.5L y amplia conectividad.", "default.jpg", 0),
    ("Tesla", "Model 3", 46990, 2023, 5000, "Eléctrico", "Automática",
     "Sedán eléctrico con autonomía de 576 km, Autopilot incluido y pantalla táctil de 15.4 pulgadas.", "default.jpg", 1),
    ("Chevrolet", "Equinox RS", 31500, 2022, 32000, "Gasolina", "Automática",
     "SUV compacta con tracción AWD, motor turbo y amplio espacio de carga.", "default.jpg", 0),
    ("Audi", "A4 40 TFSI", 47500, 2022, 18000, "Gasolina", "Automática",
     "Sedán ejecutivo con diseño Singleframe, Virtual Cockpit 12.3\" y sistema MMI Touch.", "default.jpg", 1),
    ("Nissan", "Sentra SR", 22400, 2023, 20000, "Gasolina", "Automática",
     "Sedán compacto con diseño moderno, pantalla de 8 pulgadas y sistema ProPilot.", "default.jpg", 0),
    ("Mercedes-Benz", "Clase C 200", 54000, 2023, 9000, "Gasolina", "Automática",
     "El nuevo Clase C con pantalla MBUX de 11.9 pulgadas, motor 1.5L turbo de 204 HP.", "default.jpg", 1),
    ("Volkswagen", "Jetta TSI", 26900, 2023, 11000, "Gasolina", "Automática",
     "Sedán alemán con motor TSI 1.4L, Digital Cockpit Pro y asistentes de manejo.", "default.jpg", 0),
]

cursor.executemany("""
INSERT INTO autos (marca, modelo, precio, anio, kilometraje, combustible,
                   transmision, descripcion, imagen, destacado)
VALUES (?,?,?,?,?,?,?,?,?,?)
""", autos_sample)

conexion.commit()
conexion.close()

print("✅ Base de datos creada con datos de ejemplo.")
print(f"   → {len(autos_sample)} autos de muestra insertados")
print("   → Usuario admin: admin / 1234")
