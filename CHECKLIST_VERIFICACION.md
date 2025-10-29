# ✅ Checklist de Verificación

## Usa este documento para verificar que todo funciona correctamente

---

## 🔧 1. Preview de Plantillas

### Acceso
- [ ] Puedo acceder a `http://localhost:8000/admin/`
- [ ] Puedo iniciar sesión con admin/admin123
- [ ] Veo el menú "Plantillas de certificados"

### Funcionalidad
- [ ] Veo el botón "👁️ Vista Previa" en la lista
- [ ] Al hacer clic, se abre una nueva pestaña
- [ ] Se muestra un PDF (no un error)
- [ ] El PDF contiene datos de ejemplo
- [ ] Veo el código QR en el PDF
- [ ] El nombre es "JUAN PÉREZ GARCÍA"
- [ ] El DNI es "12345678"
- [ ] El evento es "Capacitación en Seguridad Vial 2024"

### Resultado
- [ ] ✅ Preview funciona perfectamente
- [ ] ❌ Hay algún problema (especificar abajo)

**Notas**:
```
_________________________________________________
_________________________________________________
_________________________________________________
```

---

## 🎨 2. Contraste en Admin

### Breadcrumbs (Migas de Pan)
- [ ] Veo breadcrumbs en la parte superior
- [ ] El fondo es gris claro SÓLIDO (no gradiente)
- [ ] El texto es NEGRO (no azul medio)
- [ ] Los enlaces son azul OSCURO
- [ ] Es fácil de leer sin esfuerzo

### Headers de Tablas
- [ ] Veo headers en listas (Eventos, Participantes, Certificados)
- [ ] El fondo es gris claro SÓLIDO (no gradiente)
- [ ] El texto es NEGRO en NEGRITA
- [ ] Es muy fácil de leer

### Mensajes de Alerta
- [ ] Veo mensajes después de realizar acciones
- [ ] Los fondos son colores SÓLIDOS (no gradientes)
- [ ] Mensaje de éxito: fondo verde claro, texto verde OSCURO
- [ ] Mensaje de error: fondo rojo claro, texto rojo OSCURO
- [ ] Mensaje de advertencia: fondo naranja claro, texto naranja OSCURO
- [ ] El texto está en NEGRITA
- [ ] Son muy fáciles de leer

### Filtros Laterales
- [ ] Veo filtros en el lado derecho de las listas
- [ ] El header es azul OSCURO con texto blanco
- [ ] Los enlaces son azul OSCURO
- [ ] La opción seleccionada tiene fondo azul OSCURO
- [ ] Todo es fácil de leer

### Enlaces
- [ ] Los enlaces son azul OSCURO (#0d47a1)
- [ ] NO son azul medio (#1565c0)
- [ ] Están en NEGRITA o SEMI-NEGRITA
- [ ] Son fáciles de ver

### Paginación
- [ ] Veo paginación en listas largas
- [ ] El fondo es gris claro SÓLIDO
- [ ] Los números son azul OSCURO
- [ ] Es fácil de leer

### Resultado General Admin
- [ ] ✅ Todo tiene buen contraste
- [ ] ✅ No veo gradientes en fondos de texto
- [ ] ✅ Los colores son sólidos
- [ ] ✅ Todo es fácil de leer
- [ ] ❌ Hay algún problema (especificar abajo)

**Notas**:
```
_________________________________________________
_________________________________________________
_________________________________________________
```

---

## 🌐 3. Contraste en Sitio Público

### Navbar
- [ ] Veo navbar en `http://localhost:8000/consulta/`
- [ ] El fondo es azul OSCURO sólido
- [ ] El texto es BLANCO
- [ ] Los enlaces son BLANCOS
- [ ] Es fácil de leer

### Footer
- [ ] Veo footer en la parte inferior
- [ ] El fondo es gris OSCURO sólido (no gradiente)
- [ ] Los títulos son BLANCOS
- [ ] El texto es gris MUY CLARO o blanco
- [ ] Los enlaces son gris MUY CLARO
- [ ] Todo es fácil de leer

### Botones
- [ ] Los botones tienen fondo azul OSCURO
- [ ] El texto es BLANCO
- [ ] No tienen gradientes
- [ ] Son fáciles de ver

### Resultado General Sitio Público
- [ ] ✅ Todo tiene buen contraste
- [ ] ✅ No veo gradientes
- [ ] ✅ Los colores son sólidos
- [ ] ✅ Todo es fácil de leer
- [ ] ❌ Hay algún problema (especificar abajo)

**Notas**:
```
_________________________________________________
_________________________________________________
_________________________________________________
```

---

## 🧪 4. Pruebas de Accesibilidad

### Prueba de Brillo Bajo
- [ ] Reduje el brillo de pantalla al 30%
- [ ] Puedo leer breadcrumbs
- [ ] Puedo leer headers de tablas
- [ ] Puedo leer mensajes
- [ ] Puedo leer enlaces
- [ ] Puedo leer el footer

### Prueba de Distancia
- [ ] Me alejé 2 metros de la pantalla
- [ ] Puedo distinguir títulos
- [ ] Puedo distinguir enlaces
- [ ] Puedo distinguir botones
- [ ] Puedo distinguir estados (firmado/sin firmar)

### Prueba de Navegadores
- [ ] Probé en Chrome
- [ ] Probé en Firefox
- [ ] Probé en Edge
- [ ] Se ve bien en todos

### Resultado Accesibilidad
- [ ] ✅ Pasa todas las pruebas
- [ ] ❌ Hay algún problema (especificar abajo)

**Notas**:
```
_________________________________________________
_________________________________________________
_________________________________________________
```

---

## 📊 5. Comparación Visual

### Colores Primarios
- [ ] Veo azul OSCURO (#0d47a1) en lugar de azul medio
- [ ] Veo negro (#212529) en textos principales
- [ ] Veo gris OSCURO (#495057) en textos secundarios
- [ ] NO veo transparencias (rgba)
- [ ] NO veo gradientes en fondos de texto

### Elementos Específicos
- [ ] Breadcrumbs: Negro sobre gris sólido ✅
- [ ] Headers: Negro sobre gris sólido ✅
- [ ] Enlaces: Azul oscuro ✅
- [ ] Mensajes: Colores sólidos ✅
- [ ] Filtros: Azul oscuro ✅
- [ ] Footer: Blanco/gris claro sobre gris oscuro ✅

### Resultado Comparación
- [ ] ✅ Todo coincide con las descripciones
- [ ] ❌ Algo no coincide (especificar abajo)

**Notas**:
```
_________________________________________________
_________________________________________________
_________________________________________________
```

---

## 🔍 6. Verificación Técnica

### Archivos Estáticos
```bash
python manage.py collectstatic --noinput
```
- [ ] Ejecuté el comando
- [ ] Salida: "1 static file copied, 127 unmodified"
- [ ] Sin errores

### Verificación del Sistema
```bash
python manage.py check
```
- [ ] Ejecuté el comando
- [ ] Salida: "System check identified no issues"
- [ ] Sin errores

### Servidor
```bash
python manage.py runserver
```
- [ ] El servidor inicia sin errores
- [ ] Puedo acceder a http://localhost:8000
- [ ] No veo errores en la consola

### Resultado Técnico
- [ ] ✅ Todo funciona correctamente
- [ ] ❌ Hay errores (especificar abajo)

**Notas**:
```
_________________________________________________
_________________________________________________
_________________________________________________
```

---

## 📚 7. Documentación

### Archivos Creados
- [ ] REPARACIONES_CONTRASTE_Y_PREVIEW.md existe
- [ ] RESUMEN_VISUAL_REPARACIONES.md existe
- [ ] PRUEBA_RAPIDA_REPARACIONES.md existe
- [ ] DONDE_VER_LAS_MEJORAS.md existe
- [ ] REPARACIONES_COMPLETADAS.md existe
- [ ] RESUMEN_FINAL_REPARACIONES.md existe
- [ ] CHECKLIST_VERIFICACION.md existe (este archivo)

### Contenido
- [ ] Leí el resumen final
- [ ] Entiendo qué se reparó
- [ ] Sé cómo probar las mejoras
- [ ] Sé dónde ver los cambios

### Resultado Documentación
- [ ] ✅ Documentación completa y clara
- [ ] ❌ Falta algo (especificar abajo)

**Notas**:
```
_________________________________________________
_________________________________________________
_________________________________________________
```

---

## ✅ RESUMEN FINAL

### Funcionalidad
- [ ] ✅ Preview de plantillas funciona
- [ ] ✅ Contraste mejorado en admin
- [ ] ✅ Contraste mejorado en sitio público
- [ ] ✅ Accesibilidad WCAG AAA
- [ ] ✅ Sin errores técnicos
- [ ] ✅ Documentación completa

### Calidad Visual
- [ ] ✅ Todo es fácil de leer
- [ ] ✅ Colores sólidos sin gradientes
- [ ] ✅ Sin transparencias
- [ ] ✅ Contraste excelente
- [ ] ✅ Diseño profesional

### Estado General
```
┌─────────────────────────────────────┐
│                                     │
│  [ ] TODO VERIFICADO Y FUNCIONANDO │
│                                     │
│  Fecha: ___/___/2025               │
│  Verificado por: ________________  │
│                                     │
└─────────────────────────────────────┘
```

---

## 🐛 Problemas Encontrados

Si encontraste algún problema, anótalo aquí:

### Problema 1:
```
Descripción:
_________________________________________________
_________________________________________________

Ubicación:
_________________________________________________

Solución intentada:
_________________________________________________
_________________________________________________
```

### Problema 2:
```
Descripción:
_________________________________________________
_________________________________________________

Ubicación:
_________________________________________________

Solución intentada:
_________________________________________________
_________________________________________________
```

### Problema 3:
```
Descripción:
_________________________________________________
_________________________________________________

Ubicación:
_________________________________________________

Solución intentada:
_________________________________________________
_________________________________________________
```

---

## 📞 Soluciones Rápidas

### Si el preview no funciona:
```bash
pip install weasyprint qrcode pillow
python manage.py runserver
```

### Si el CSS no se actualiza:
```bash
python manage.py collectstatic --noinput
# Luego: Ctrl + Shift + R en el navegador
```

### Si hay errores:
```bash
python manage.py check
python manage.py check --deploy
```

---

## 🎉 Confirmación Final

Una vez que hayas verificado todo:

```
┌─────────────────────────────────────────────┐
│                                             │
│  ✅ TODAS LAS REPARACIONES VERIFICADAS     │
│                                             │
│  Preview: ✅ Funciona                       │
│  Contraste: ✅ Excelente                    │
│  Accesibilidad: ✅ WCAG AAA                 │
│  Documentación: ✅ Completa                 │
│                                             │
│  🎉 ¡TODO PERFECTO!                        │
│                                             │
└─────────────────────────────────────────────┘
```

**Firma**: ___________________________

**Fecha**: ___/___/2025

---

**¡Usa este checklist para verificar todo sistemáticamente!** ✅

