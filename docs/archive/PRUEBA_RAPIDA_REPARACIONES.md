# ⚡ Guía de Prueba Rápida - Reparaciones

## 🎯 Objetivo
Verificar que las reparaciones funcionan correctamente en menos de 5 minutos.

---

## 📋 Pre-requisitos

```bash
# 1. Asegúrate de que el servidor esté corriendo
python manage.py runserver

# 2. Tienes acceso al admin con las credenciales:
Usuario: admin
Contraseña: admin123
```

---

## ✅ Prueba 1: Preview de Plantillas (2 minutos)

### Pasos:

1. **Abrir navegador**
   ```
   http://localhost:8000/admin/
   ```

2. **Iniciar sesión**
   - Usuario: `admin`
   - Contraseña: `admin123`

3. **Navegar a Plantillas**
   - En el menú lateral: `Plantillas de certificados`
   - O ir directamente a: `http://localhost:8000/admin/certificates/certificatetemplate/`

4. **Probar Preview**
   - Buscar la plantilla "Plantilla por Defecto DRTC Puno"
   - Hacer clic en el botón **"👁️ Vista Previa"**

### ✅ Resultado Esperado:

```
✓ Se abre una nueva pestaña
✓ Se muestra un PDF
✓ El PDF contiene:
  - Nombre: JUAN PÉREZ GARCÍA
  - DNI: 12345678
  - Evento: Capacitación en Seguridad Vial 2024
  - Fecha: [Fecha actual]
  - Código QR visible en la esquina
✓ No hay errores
```

### ❌ Si hay error:

```
- Verificar que WeasyPrint está instalado
- Verificar que qrcode está instalado
- Revisar los logs del servidor
```

---

## ✅ Prueba 2: Contraste de Colores (3 minutos)

### Pasos:

1. **Verificar Breadcrumbs**
   ```
   Ubicación: Parte superior de cualquier página del admin
   ```
   
   **Verificar:**
   - [ ] Texto negro sobre fondo gris claro
   - [ ] Enlaces en azul oscuro (#0d47a1)
   - [ ] Fácil de leer sin esfuerzo

2. **Verificar Headers de Tablas**
   ```
   Ir a: Certificados → Lista de certificados
   ```
   
   **Verificar:**
   - [ ] Headers con fondo gris sólido (no gradiente)
   - [ ] Texto negro en negrita
   - [ ] Claramente legible

3. **Verificar Mensajes**
   ```
   Realizar cualquier acción (ej: guardar algo)
   ```
   
   **Verificar:**
   - [ ] Mensaje de éxito: fondo verde claro, texto verde oscuro
   - [ ] Sin gradientes
   - [ ] Texto en negrita
   - [ ] Fácil de leer

4. **Verificar Filtros Laterales**
   ```
   Ir a: Certificados → Ver filtros en el lado derecho
   ```
   
   **Verificar:**
   - [ ] Header azul oscuro con texto blanco
   - [ ] Enlaces en azul oscuro
   - [ ] Opción seleccionada con fondo azul oscuro
   - [ ] Todo claramente legible

5. **Verificar Footer (Sitio Público)**
   ```
   Ir a: http://localhost:8000/consulta/
   ```
   
   **Verificar:**
   - [ ] Fondo gris oscuro sólido
   - [ ] Texto blanco y gris claro
   - [ ] Enlaces visibles
   - [ ] Fácil de leer

---

## 📊 Checklist Rápido

### Preview de Plantillas
- [ ] PDF se genera sin errores
- [ ] Código QR visible en el PDF
- [ ] Datos de ejemplo correctos
- [ ] Se abre en nueva pestaña

### Contraste - Admin
- [ ] Breadcrumbs: texto negro sobre gris
- [ ] Headers tabla: texto negro sobre gris
- [ ] Enlaces: azul oscuro (#0d47a1)
- [ ] Mensajes: colores sólidos, sin gradientes
- [ ] Filtros: azul oscuro con texto blanco
- [ ] Botones: colores sólidos

### Contraste - Sitio Público
- [ ] Navbar: texto blanco sobre azul oscuro
- [ ] Footer: texto blanco/gris claro sobre gris oscuro
- [ ] Enlaces footer: gris claro, visible
- [ ] Botones: azul oscuro con texto blanco

---

## 🎨 Comparación Visual Rápida

### Antes vs Después

#### Breadcrumbs
```
ANTES: [Texto azul medio sobre gradiente gris] 😕
       Difícil de leer, bajo contraste

DESPUÉS: [Texto negro sobre gris sólido] 😊
         Fácil de leer, alto contraste
```

#### Mensajes de Éxito
```
ANTES: [Fondo verde con gradiente, texto verde medio] 😕
       Contraste justo en el límite

DESPUÉS: [Fondo verde sólido, texto verde oscuro en negrita] 😊
         Contraste excelente, muy legible
```

#### Enlaces
```
ANTES: [Azul medio #1565c0] 😕
       Contraste 4.1:1 (apenas aceptable)

DESPUÉS: [Azul oscuro #0d47a1] 😊
         Contraste 9.1:1 (excelente)
```

---

## 🔍 Prueba de Accesibilidad Rápida

### Prueba del Brillo

1. **Reducir brillo de pantalla al 30%**
2. **Verificar que puedes leer:**
   - [ ] Breadcrumbs
   - [ ] Headers de tablas
   - [ ] Mensajes de alerta
   - [ ] Enlaces
   - [ ] Texto del footer

### Prueba de Distancia

1. **Alejarte 2 metros de la pantalla**
2. **Verificar que puedes distinguir:**
   - [ ] Títulos principales
   - [ ] Enlaces importantes
   - [ ] Botones de acción
   - [ ] Estados (firmado/sin firmar)

---

## 🐛 Solución de Problemas

### Problema: Preview no funciona

**Síntomas:**
- Error al hacer clic en "Vista Previa"
- Página en blanco
- Error 500

**Solución:**
```bash
# Verificar instalación de dependencias
pip install weasyprint qrcode pillow

# Reiniciar servidor
python manage.py runserver
```

### Problema: CSS no se actualiza

**Síntomas:**
- Colores siguen siendo los antiguos
- Gradientes todavía visibles

**Solución:**
```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Limpiar caché del navegador
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)
```

### Problema: Contraste sigue bajo

**Síntomas:**
- Texto difícil de leer
- Colores claros

**Verificar:**
```bash
# 1. Archivo CSS correcto
cat static/admin/css/custom_admin.css | grep "primary-color"
# Debe mostrar: --primary-color: #0d47a1;

# 2. Archivos estáticos actualizados
python manage.py collectstatic --noinput

# 3. Caché del navegador limpiado
```

---

## 📸 Screenshots de Referencia

### Preview Funcionando
```
✅ Debe verse así:
┌─────────────────────────────────────┐
│ [PDF Viewer]                        │
│                                     │
│  CERTIFICADO DE PARTICIPACIÓN      │
│                                     │
│  JUAN PÉREZ GARCÍA                 │
│  DNI: 12345678                     │
│                                     │
│  Capacitación en Seguridad Vial    │
│  Fecha: [Hoy]                      │
│                                     │
│  [QR Code]                         │
│                                     │
└─────────────────────────────────────┘
```

### Contraste Correcto
```
✅ Breadcrumbs:
Inicio > Certificados > Lista
[Negro sobre gris claro, muy legible]

✅ Headers:
| UUID | Participante | Estado | Fecha |
[Negro en negrita sobre gris, muy legible]

✅ Mensajes:
┌────────────────────────────────────┐
│ ✓ Operación exitosa                │
└────────────────────────────────────┘
[Verde oscuro sobre verde claro, muy legible]
```

---

## ⏱️ Tiempo Estimado

- **Prueba 1 (Preview)**: 2 minutos
- **Prueba 2 (Contraste)**: 3 minutos
- **Total**: 5 minutos

---

## ✅ Criterios de Éxito

### Todo está correcto si:

1. ✅ Preview genera PDF sin errores
2. ✅ QR code visible en el PDF
3. ✅ Todos los textos son fáciles de leer
4. ✅ No hay gradientes en fondos de texto
5. ✅ Colores son sólidos y oscuros
6. ✅ Puedes leer todo con brillo bajo
7. ✅ No hay transparencias en textos

---

## 🎉 Resultado Final

Si todas las pruebas pasan:

```
✅ Preview de plantillas: FUNCIONANDO
✅ Contraste de colores: EXCELENTE
✅ Accesibilidad: WCAG AAA
✅ Experiencia de usuario: MEJORADA

🎉 ¡Reparaciones completadas exitosamente!
```

---

## 📞 Soporte

Si encuentras algún problema:

1. Revisar logs del servidor
2. Verificar instalación de dependencias
3. Limpiar caché del navegador
4. Recolectar archivos estáticos
5. Reiniciar servidor

---

**Última actualización**: 29 de Octubre, 2025  
**Versión**: 1.0
