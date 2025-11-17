# 🎯 EMPIEZA AQUÍ - Pruebas Locales

## 👋 ¡Hola!

Tienes el servidor corriendo en **http://localhost:7070** y estás listo para probar el sistema.

---

## ⚡ Inicio Rápido (30 segundos)

### Opción 1: Script Automático (RECOMENDADO)

Simplemente ejecuta este archivo:

```cmd
EJECUTAR_AHORA_PRUEBAS.bat
```

**¿Qué hace?**
- ✅ Verifica que el servidor esté corriendo
- ✅ Te da opciones de pruebas automatizadas o manuales
- ✅ Abre el navegador con las URLs principales
- ✅ Te muestra las credenciales necesarias

---

### Opción 2: Abrir Navegador Manualmente

Simplemente abre estas URLs en tu navegador:

1. **Admin:** http://localhost:7070/admin/
   - Usuario: `admin`
   - Contraseña: `admin123`

2. **Dashboard:** http://localhost:7070/admin/dashboard/

3. **Consulta:** http://localhost:7070/consulta/
   - Prueba con DNI: `99238323`

---

## 📋 Checklist Rápido

Marca lo que ya probaste:

```
[ ] 1. Servidor corriendo en http://localhost:7070
[ ] 2. Login en admin funciona
[ ] 3. Dashboard muestra estadísticas
[ ] 4. Consulta de certificado funciona
[ ] 5. Descarga de PDF funciona
[ ] 6. Verificación de certificado funciona
```

---

## 🔧 Si Algo No Funciona

### El servidor no responde
```cmd
# Inicia el servidor
python manage.py runserver 7070
```

### No puedo hacer login
```cmd
# Recrea el superusuario
python manage.py create_superuser_if_not_exists --update --noinput
```

### Archivos estáticos no cargan
```cmd
# Recolecta archivos estáticos
python manage.py collectstatic --noinput
```

---

## 📚 Documentación Disponible

Si necesitas más detalles:

- **RESUMEN_PRUEBAS_LOCALES.md** - Resumen de todo lo preparado
- **GUIA_PRUEBAS_LOCALES.md** - Guía completa y detallada
- **PRUEBAS_LOCALES_RAPIDO.md** - Guía rápida de 5 minutos
- **CREDENCIALES_PRUEBA.md** - Todas las credenciales y DNIs

---

## 🎯 Tu Próximo Paso

### Ahora Mismo:
```cmd
EJECUTAR_AHORA_PRUEBAS.bat
```

### Después de las Pruebas Locales:
```cmd
test-produccion-local.bat
```

---

## 💡 Tip

Usa **modo incógnito** (Ctrl + Shift + N) en el navegador para evitar problemas de caché.

---

## ❓ ¿Necesitas Ayuda?

1. Revisa **RESUMEN_PRUEBAS_LOCALES.md**
2. Revisa **GUIA_PRUEBAS_LOCALES.md**
3. Busca el error en **logs/django.log**

---

# 🚀 ¡Adelante!

**Ejecuta ahora:**
```cmd
EJECUTAR_AHORA_PRUEBAS.bat
```

---

**Todo está listo. Solo tienes que ejecutar el script y seguir las instrucciones.** ✨
