# 🌸 Sistema de Reparto de Regalos – Día de la Madre

Sistema web (Python + MySQL) para registrar la entrega de regalos y evitar entregas dobles.
Consulta el DNI automáticamente a RENIEC.

---

## ✅ Requisitos previos

- Python 3.9+
- MySQL 8.0+
- Conexión a internet (para consultar RENIEC)

---

## 🚀 Instalación paso a paso

### 1. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### 2. Crear la base de datos en MySQL

Abre MySQL Workbench o la terminal y ejecuta:

```bash
mysql -u root -p < schema.sql
```

O copia y pega el contenido de `schema.sql` en MySQL Workbench.

### 3. Configurar credenciales

Edita el archivo `.env`:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_contraseña_mysql
DB_NAME=reparto_regalos
APIPERU_TOKEN=TU_TOKEN_AQUI
```

### 4. Obtener token para RENIEC (gratis)

1. Ve a https://apiperu.dev
2. Crea una cuenta gratuita
3. Copia tu token y pégalo en `.env` como `APIPERU_TOKEN`

> Si no pones token, el sistema igual funciona pero deberás ingresar
> el nombre manualmente (el DNI sigue siendo único y sin duplicados).

### 5. Iniciar la aplicación

```bash
python app.py
```

Luego abre en tu navegador: **http://localhost:5000**

---

## 🎯 Cómo usar el sistema

1. **Ingresa el DNI** de 8 dígitos → el nombre aparece automáticamente desde RENIEC
2. **Confirma la entrega** con el botón verde
3. Si esa persona **ya recibió** su regalo, el sistema lo bloquea con alerta roja
4. La pestaña **"Lista completa"** muestra todas las beneficiarias con estado y hora

---

## 📁 Archivos del proyecto

```
reparto_regalos/
├── app.py            ← Servidor Flask (backend)
├── schema.sql        ← Crear tablas en MySQL
├── requirements.txt  ← Librerías Python
├── .env              ← Contraseñas y tokens (NO compartir)
└── templates/
    └── index.html    ← Interfaz web
```

---

## 🔒 Seguridad

- No compartas el archivo `.env`
- Para producción, cambia `debug=True` a `debug=False` en `app.py`
- Considera usar un usuario MySQL con permisos limitados solo a esta base de datos
