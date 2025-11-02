# 🔄 REINICIAR SERVIDOR PARA VER CAMBIOS

## ⚠️ IMPORTANTE:
Los cambios están aplicados en el archivo, pero Django necesita reiniciarse.

---

## 🎯 PASOS PARA REINICIAR:

### Opción 1: Reinicio Simple (Recomendado)

1. **Ve a la terminal donde corre el servidor**
2. **Presiona:** `Ctrl + C`
3. **Espera a que se detenga completamente**
4. **Ejecuta:** `python manage.py runserver`
5. **Abre el navegador en modo incógnito:** `Ctrl + Shift + N`
6. **Navega a:** `http://127.0.0.1:8000/certificates/query/`
7. **Busca un DNI:** `12345678`

---

### Opción 2: Reinicio Forzado

```powershell
# 1. Detener todos los procesos Python
taskkill /F /IM python.exe

# 2. Esperar 2 segundos
timeout /t 2

# 3. Reiniciar el servidor
python manage.py runserver
```

---

### Opción 3: Desde PowerShell (Copia y Pega)

```powershell
# Detener servidor
Stop-Process -Name python -Force -ErrorAction SilentlyContinue

# Esperar
Start-Sleep -Seconds 2

# Reiniciar
python manage.py runserver
```

---

## 🌐 LIMPIAR CACHÉ DEL NAVEGADOR:

### Chrome/Edge:
```
1. Presiona: Ctrl + Shift + Delete
2. Selecciona: "Imágenes y archivos en caché"
3. Rango de tiempo: "Desde siempre"
4. Click: "Borrar datos"
```

### O Usa Modo Incógnito:
```
Ctrl + Shift + N (Chrome/Edge)
Ctrl + Shift + P (Firefox)
```

---

## ✅ VERIFICACIÓN:

Después de reiniciar, deberías ver:

### 🎯 Elementos del Nuevo Diseño:

1. **Toolbar con filtros:**
   - Badge azul: "DNI: 12345678"
   - Input de búsqueda: "🔍 Buscar evento..."
   - 2 selectores de filtro
   - Contador: "Mostrando X de Y certificados"

2. **Tabla con header azul oscuro:**
   - Fondo: #0d47a1 (azul oscuro)
   - Texto blanco
   - Columnas: # | Evento | Fecha | Tipo | Estado | Generado | Acciones

3. **Botones compactos:**
   - "PDF" (azul)
   - "QR" (gris)

4. **Footer:**
   - "ℹ️ Usa los filtros"
   - "Total: X certificados"

---

## 🐛 SI AÚN NO VES CAMBIOS:

### 1. Verifica la URL:
```
✅ Correcto: http://127.0.0.1:8000/certificates/results/?dni=12345678
❌ Incorrecto: http://127.0.0.1:8000/admin/
```

### 2. Inspecciona el HTML:
```
1. F12 (Abrir DevTools)
2. Pestaña "Elements"
3. Busca (Ctrl + F): "datatable-card"
4. Si lo encuentras: ✅ Archivo correcto
5. Si NO: ❌ Caché del navegador
```

### 3. Ver Código Fuente:
```
1. Click derecho → "Ver código fuente"
2. Busca: "datatable-card"
3. Si aparece: ✅ Cambios aplicados
```

---

## 📝 COMANDOS RÁPIDOS:

### Reiniciar Todo:
```powershell
# Copiar y pegar en PowerShell
taskkill /F /IM python.exe; timeout /t 2; python manage.py runserver
```

### Verificar Archivo:
```powershell
# Ver si tiene el nuevo diseño
Select-String -Path "templates\certificates\results.html" -Pattern "datatable-card"
```

---

## 🎬 SECUENCIA COMPLETA:

```powershell
# 1. Detener servidor
# En la terminal del servidor: Ctrl + C

# 2. Reiniciar
python manage.py runserver

# 3. Abrir navegador en modo incógnito
# Ctrl + Shift + N

# 4. Ir a la URL
# http://127.0.0.1:8000/certificates/query/

# 5. Buscar DNI
# 12345678

# 6. Ver resultados con nuevo diseño
```

---

## 📸 CAPTURA ESPERADA:

```
┌────────────────────────────────────────────────────┐
│ 📄 Certificados de Juan Perez │ ← Nueva Búsqueda  │
└────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────┐
│ 👤 DNI: 12345678 │ 🔍 Buscar │ ▼ Tipo │ ▼ Estado │
│                              Mostrando 2 de 2      │
├────────────────────────────────────────────────────┤
│ # │ Evento │ Fecha │ Tipo │ Estado │ Acciones    │ ← Header azul oscuro
├───┼────────┼───────┼──────┼────────┼─────────────┤
│ 1 │ ...    │ ...   │ ...  │ ...    │ PDF  QR    │
│ 2 │ ...    │ ...   │ ...  │ ...    │ PDF  QR    │
├────────────────────────────────────────────────────┤
│ ℹ️ Usa los filtros │ Total: 2 certificados        │
└────────────────────────────────────────────────────┘
```

---

**¡El archivo está correcto! Solo necesitas reiniciar el servidor y limpiar caché.** 🔄
