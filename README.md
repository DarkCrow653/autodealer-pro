# 🚗 AutoDealer Pro

Aplicación web de portafolio para una tienda de autos, construida con **Python Flask** y **SQLite**.

🔗 **Demo en vivo:** [autodealer-pro.onrender.com](https://autodealer-pro.onrender.com)

---

## ✨ Características

- **Catálogo de autos** con filtros por combustible, transmisión y precio
- **Sección de destacados** en home y catálogo
- **Panel de administración** con dashboard de estadísticas y gráficas
- **CRUD completo** — agregar, editar, destacar y eliminar autos
- **Subida de imágenes** para cada vehículo
- Diseño dark luxury, 100% responsive

## 🛠️ Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python · Flask |
| Base de datos | SQLite |
| Frontend | HTML · CSS (custom) · JavaScript |
| Gráficas (admin) | Chart.js |
| Producción | Gunicorn · Render |

## 🚀 Correr localmente

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/autodealer-pro.git
cd autodealer-pro

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Inicializar la base de datos (solo la primera vez)
python init_db.py

# 4. Correr la app
python app.py
```

Abre `http://localhost:5000` en tu navegador.

**Credenciales admin:** `admin` / `1234`

## 📁 Estructura

```
autodealer-pro/
├── app.py              # Rutas y lógica principal
├── init_db.py          # Script para crear/poblar la DB
├── requirements.txt    # Dependencias Python
├── Procfile            # Configuración para Render/Heroku
├── render.yaml         # Deploy automático en Render
├── templates/          # HTML (Jinja2)
│   ├── base.html
│   ├── admin_base.html
│   ├── index.html
│   ├── catalogo.html
│   ├── detalle_auto.html
│   ├── admin.html
│   ├── agregar_auto.html
│   ├── editar_auto.html
│   └── login.html
└── static/
    ├── css/style.css
    ├── js/script.js
    └── img/
```

## ⚠️ Nota sobre imágenes en producción

Render (plan gratuito) usa un **filesystem efímero**: las imágenes que subas se borran al reiniciar el servidor. Para producción real, integra **Cloudinary** o **AWS S3**.

## 📄 Licencia

MIT — libre para uso personal y de portafolio.
