# 🔄 LIMPIAR CACHE DEL DASHBOARD

## El dashboard está funcionando correctamente en el servidor

Los archivos CSS y JS están correctos y se están sirviendo bien:
- ✅ CSS: 15.7KB (completo)
- ✅ JS: 8KB (completo)
- ✅ Plantilla actualizada con parámetros de versión

## El problema es CACHE del navegador

Tu navegador tiene guardada la versión antigua del dashboard y no está descargando la nueva.

## SOLUCIÓN: Limpiar Cache Completamente

### Opción 1: Forzar Recarga (MÁS RÁPIDO)
1. Ve a: https://certificados.transportespuno.gob.pe/admin/dashboard/
2. Presiona **Ctrl + Shift + R** (Windows/Linux)
3. O **Cmd + Shift + R** (Mac)
4. Espera 5 segundos
5. Recarga de nuevo con **Ctrl + Shift + R**

### Opción 2: Limpiar Cache Completo (RECOMENDADO)
1. Presiona **Ctrl + Shift + Delete**
2. Selecciona:
   - ✅ Cookies y otros datos de sitios
   - ✅ Imágenes y archivos en caché
3. Rango de tiempo: **Todo el tiempo**
4. Haz clic en **Borrar datos**
5. Cierra el navegador completamente
6. Abre el navegador de nuevo
7. Ve a: https://certificados.transportespuno.gob.pe/admin/dashboard/

### Opción 3: Modo Incógnito (PARA PROBAR)
1. Abre una ventana de incógnito:
   - **Ctrl + Shift + N** (Chrome/Edge)
   - **Ctrl + Shift + P** (Firefox)
2. Ve a: https://certificados.transportespuno.gob.pe/admin/dashboard/
3. Inicia sesión
4. Verifica si se ve bien

### Opción 4: Otro Navegador (DEFINITIVO)
1. Abre un navegador diferente (Chrome, Firefox, Edge, etc.)
2. Ve a: https://certificados.transportespuno.gob.pe/admin/dashboard/
3. Inicia sesión
4. Verifica si se ve bien

## Cómo Verificar que Funcionó

### El dashboard DEBE verse así:

#### Header
- ✅ Fondo azul con gradiente
- ✅ Texto blanco
- ✅ Logo "Administración DRTC" en blanco

#### Tarjetas de Estadísticas
- ✅ Tarjetas blancas con sombra
- ✅ Iconos grandes de colores
- ✅ Números grandes y claros
- ✅ Borde de color a la izquierda

#### Botones
- ✅ Botón "Actualizar" blanco con sombra
- ✅ Botones de "Acciones Rápidas" con colores

#### Gráficos
- ✅ Secciones para gráficos (aunque estén vacíos si no hay datos)

## Si TODAVÍA se ve mal después de limpiar cache

### Verificar en Herramientas de Desarrollador

1. Presiona **F12** para abrir las herramientas de desarrollador
2. Ve a la pestaña **Network** o **Red**
3. Recarga la página (**Ctrl + R**)
4. Busca estos archivos:
   - `dashboard.css?v=20251118`
   - `dashboard.js?v=20251118`
5. Haz clic en cada uno y verifica:
   - **Status**: Debe ser 200 (OK)
   - **Size**: CSS debe ser ~15KB, JS debe ser ~8KB

### Si los archivos NO se cargan (Status 404 o error)

Ejecuta esto en el servidor:

```bash
ssh administrador@161.132.47.92
cd dockers/sistema_certificados_drtc
docker compose -f docker-compose.prod.7070.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.7070.yml restart web
```

### Si los archivos se cargan pero NO se aplican

1. Ve a la pestaña **Console** en las herramientas de desarrollador
2. Busca errores en rojo
3. Copia el error y envíamelo

## Verificación Técnica

### Desde el servidor (para confirmar que está bien)

```bash
# Verificar que los archivos existen
ssh administrador@161.132.47.92
cd dockers/sistema_certificados_drtc

# Verificar CSS
curl -I https://certificados.transportespuno.gob.pe/static/admin/css/dashboard.css
# Debe retornar: HTTP/1.1 200 OK, Content-Length: 15781

# Verificar JS
curl -I https://certificados.transportespuno.gob.pe/static/admin/js/dashboard.js
# Debe retornar: HTTP/1.1 200 OK

# Ver primeras líneas del CSS
curl -s https://certificados.transportespuno.gob.pe/static/admin/css/dashboard.css | head -5
# Debe mostrar: /* Dashboard de Estadísticas - Estilos */
```

## Resumen

✅ **Los archivos están correctos en el servidor**
✅ **La plantilla está actualizada**
✅ **Los archivos se están sirviendo correctamente**

❌ **Tu navegador tiene cache antiguo**

**SOLUCIÓN**: Limpia el cache completamente siguiendo las instrucciones arriba.

---

## Última Actualización
- **Fecha**: 18 de Noviembre de 2025, 21:45 hrs
- **Archivos actualizados**: dashboard.css, dashboard.js, dashboard.html
- **Parámetro de versión**: ?v=20251118
- **Estado del servidor**: ✅ FUNCIONANDO
