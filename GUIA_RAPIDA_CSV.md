# 🚀 Guía Rápida - Importación CSV Mejorada

## 📥 Cómo Importar Participantes

### Paso 1: Preparar el Archivo CSV

Crea un archivo con este formato:

```csv
DNI,Nombres y Apellidos,Fecha del Evento,Tipo de Asistente,Nombre del Evento
12345678,Juan Pérez García,15/11/2025,ASISTENTE,Capacitación 2025
87654321,María López Quispe,15/11/2025,PONENTE,Capacitación 2025
```

**Reglas:**
- DNI: 1-8 dígitos (ej: 1234567 o 12345678)
- Fecha: DD/MM/YYYY (ej: 15/11/2025)
- Tipo: ASISTENTE, PONENTE o ORGANIZADOR

---

### Paso 2: Acceder a la Importación

```
1. Ir a: http://161.132.47.92:7070/admin/
2. Login con tus credenciales
3. Click en "Participantes"
4. Click en "Importar CSV" (botón superior derecho)
```

---

### Paso 3: Subir el Archivo

**Opción A: Drag & Drop**
```
Arrastra tu archivo CSV a la zona de carga
```

**Opción B: Click**
```
Click en la zona de carga → Selecciona tu archivo
```

---

### Paso 4: Validar (Recomendado)

```
1. Click en "🔍 Validar Archivo"
2. Espera unos segundos
3. Revisa los resultados:
   - ✅ Registros válidos
   - ⚠️ Advertencias
   - ❌ Errores
```

**Si hay errores:**
- Corrige el archivo CSV
- Vuelve a subirlo
- Valida nuevamente

---

### Paso 5: Importar

```
1. Click en "✅ Importar Datos"
2. Espera a que termine
3. Verás un mensaje de éxito
4. Los participantes aparecerán en la lista
```

---

## ⚠️ Errores Comunes

### Error: "DNI inválido"
```
❌ Incorrecto: ABC12345
✅ Correcto: 12345678
```

### Error: "Tipo de Asistente inválido"
```
❌ Incorrecto: PARTICIPANTE
✅ Correcto: ASISTENTE
```

### Error: "Formato de fecha inválido"
```
❌ Incorrecto: 2025-11-15
✅ Correcto: 15/11/2025
```

### Error: "Columna faltante"
```
❌ Incorrecto: DNI,Nombre,Fecha
✅ Correcto: DNI,Nombres y Apellidos,Fecha del Evento,Tipo de Asistente,Nombre del Evento
```

---

## 💡 Consejos

### 1. Usa el Archivo de Ejemplo
```
Descarga: ejemplo-importacion.csv
Modifica con tus datos
Importa
```

### 2. Valida Siempre Primero
```
Validar → Revisar → Corregir → Importar
```

### 3. DNI con Ceros
```
El sistema normaliza automáticamente:
1234567 → 01234567
```

### 4. Importaciones Grandes
```
Si tienes más de 100 registros:
- Divide en archivos más pequeños
- Importa por lotes
```

---

## 🎯 Atajos

### Formato Rápido en Excel

1. Abre Excel
2. Crea estas columnas:
   ```
   A: DNI
   B: Nombres y Apellidos
   C: Fecha del Evento
   D: Tipo de Asistente
   E: Nombre del Evento
   ```
3. Llena los datos
4. Guardar como → CSV (delimitado por comas)

### Validación Rápida

```
Antes de importar, verifica:
☑ Todas las columnas presentes
☑ DNI solo números
☑ Fechas en formato DD/MM/YYYY
☑ Tipo es ASISTENTE, PONENTE o ORGANIZADOR
☑ Sin filas vacías
```

---

## 📊 Ejemplo Completo

```csv
DNI,Nombres y Apellidos,Fecha del Evento,Tipo de Asistente,Nombre del Evento
12345678,Juan Pérez García,15/11/2025,ASISTENTE,Capacitación en Seguridad Vial
87654321,María López Quispe,15/11/2025,PONENTE,Capacitación en Seguridad Vial
11223344,Carlos Mamani Flores,15/11/2025,ORGANIZADOR,Capacitación en Seguridad Vial
44332211,Ana Torres Condori,15/11/2025,ASISTENTE,Capacitación en Seguridad Vial
55667788,Pedro Quispe Huanca,15/11/2025,ASISTENTE,Capacitación en Seguridad Vial
```

**Resultado esperado:**
```
✅ 5 registros válidos
✅ 0 errores
✅ Importación exitosa
```

---

## 🆘 Ayuda Rápida

### La página no carga
```bash
# Verificar contenedor
ssh root@161.132.47.92 "docker ps | grep certificados"

# Ver logs
ssh root@161.132.47.92 "docker logs certificados_web --tail 50"
```

### El archivo no se sube
```
1. Verifica que sea .csv
2. Verifica que sea menor a 10MB
3. Limpia caché del navegador (Ctrl+F5)
```

### Los datos no se importan
```
1. Valida el archivo primero
2. Corrige los errores mostrados
3. Intenta nuevamente
```

---

## ✅ Checklist de Importación

Antes de importar, verifica:

- [ ] Archivo es .csv
- [ ] Tiene las 5 columnas requeridas
- [ ] Los nombres de columnas son exactos
- [ ] DNI solo tiene números
- [ ] Fechas en formato DD/MM/YYYY
- [ ] Tipo es ASISTENTE, PONENTE o ORGANIZADOR
- [ ] No hay filas vacías
- [ ] Archivo es menor a 10MB

---

## 🎉 ¡Listo!

Ahora puedes importar participantes de forma rápida y segura.

**Recuerda:**
1. Prepara el CSV
2. Valida primero
3. Importa después
4. Verifica los resultados

**¿Dudas?** Revisa MEJORA_IMPORTACION_CSV.md para más detalles.

---

**Última actualización:** 19 Nov 2025
