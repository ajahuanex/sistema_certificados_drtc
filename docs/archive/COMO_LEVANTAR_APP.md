# 🚀 CÓMO LEVANTAR LA APLICACIÓN

## ✅ El sistema está OK - Solo warnings de seguridad (normales en desarrollo)

## 📝 PASOS SIMPLES:

### 1. Abre una terminal (CMD o PowerShell)

### 2. Navega al directorio del proyecto
```bash
cd D:\2025\KIRO4
```

### 3. Levanta el servidor
```bash
python manage.py runserver
```

### 4. Deberías ver algo como:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
October 31, 2025 - 15:30:00
Django version 4.2.x, using settings 'config.settings.base'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### 5. Abre el navegador
```
http://127.0.0.1:8000/certificates/query/
```

---

## ❌ SI NO ARRANCA:

### Error: "No module named django"
```bash
pip install -r requirements.txt
```

### Error: "Port already in use"
```bash
# Detener proceso
taskkill /F /IM python.exe

# Reintentar
python manage.py runserver
```

### Error: "Database error"
```bash
python manage.py migrate
```

---

## 🔍 ¿QUÉ ERROR ESPECÍFICO TE DA?

Copia y pega el error aquí para ayudarte mejor.
