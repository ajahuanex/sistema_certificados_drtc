# 🔄 Limpiar Caché del Navegador

## El CSS no se ve porque el navegador tiene caché

---

## ✅ Solución Rápida

### Opción 1: Recarga Forzada (MÁS RÁPIDO)

**En la página del admin, presiona:**

```
Windows/Linux: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

O también:

```
Windows/Linux: Ctrl + F5
Mac: Cmd + Shift + Delete
```

---

### Opción 2: Limpiar Caché Completo

#### Chrome/Edge:
1. Presiona `Ctrl + Shift + Delete`
2. Selecciona "Imágenes y archivos en caché"
3. Rango de tiempo: "Desde siempre"
4. Click en "Borrar datos"

#### Firefox:
1. Presiona `Ctrl + Shift + Delete`
2. Selecciona "Caché"
3. Rango de tiempo: "Todo"
4. Click en "Limpiar ahora"

---

### Opción 3: Modo Incógnito (PARA PROBAR)

1. Abre ventana de incógnito:
   - Chrome/Edge: `Ctrl + Shift + N`
   - Firefox: `Ctrl + Shift + P`

2. Ve a: `http://localhost:8000/admin/`

3. Si se ve bien aquí, el problema es el caché

---

## 🔍 Verificar que el CSS se está cargando

1. Abre el admin: `http://localhost:8000/admin/`

2. Presiona `F12` (Herramientas de desarrollador)

3. Ve a la pestaña "Network" o "Red"

4. Recarga la página (`Ctrl + R`)

5. Busca: `custom_admin.css`

6. Debe aparecer con estado `200 OK`

---

## ✅ Después de Limpiar Caché

Deberías ver:

- ✅ Tablas con fondo blanco
- ✅ Headers con fondo gris claro (#f5f5f5)
- ✅ Texto negro en todas las celdas
- ✅ Enlaces azul oscuro
- ✅ Hover con fondo gris claro

---

## 🚨 Si Aún No Funciona

Ejecuta estos comandos:

```bash
# 1. Detener servidor
# Presiona Ctrl + C en la ventana del servidor

# 2. Limpiar archivos estáticos
python manage.py collectstatic --noinput --clear

# 3. Reiniciar servidor
python manage.py runserver

# 4. En el navegador:
# Ctrl + Shift + R (recarga forzada)
```

---

**¡El CSS está aplicado, solo necesitas limpiar el caché!**
