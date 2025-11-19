# 📥 Cómo Importar Participantes desde CSV

## 🎯 Guía Visual Paso a Paso

---

## Paso 1️⃣: Preparar tu Archivo CSV

### Formato Requerido

Tu archivo CSV debe tener exactamente estas 5 columnas:

```
DNI | Nombres y Apellidos | Fecha del Evento | Tipo de Asistente | Nombre del Evento
```

### Ejemplo Correcto

```csv
DNI,Nombres y Apellidos,Fecha del Evento,Tipo de Asistente,Nombre del Evento
12345678,Juan Pérez García,15/11/2025,ASISTENTE,Capacitación en Seguridad Vial
87654321,María López Quispe,15/11/2025,PONENTE,Capacitación en Seguridad Vial
11223344,Carlos Mamani Flores,15/11/2025,ORGANIZADOR,Capacitación en Seguridad Vial
```

### Reglas Importantes

| Campo | Regla | Ejemplo Correcto | Ejemplo Incorrecto |
|-------|-------|------------------|-------------------|
| **DNI** | Solo números, 1-8 dígitos | `12345678` | `ABC12345` |
| **Nombres** | Texto, no vacío | `Juan Pérez García` | ` ` (vacío) |
| **Fecha** | Formato DD/MM/YYYY | `15/11/2025` | `2025-11-15` |
| **Tipo** | ASISTENTE, PONENTE u ORGANIZADOR | `ASISTENTE` | `PARTICIPANTE` |
| **Evento** | Texto, no vacío | `Capacitación 2025` | ` ` (vacío) |

---

## Paso 2️⃣: Acceder al Sistema

### 1. Abrir el navegador
```
Chrome, Firefox o Edge
```

### 2. Ir a la URL
```
http://161.132.47.92:7070/admin/
```

### 3. Iniciar sesión
```
Usuario: admin
Contraseña: [tu contraseña]
```

### 4. Ir a Participantes
```
Click en "Participantes" en el menú lateral
```

### 5. Click en "Importar CSV"
```
Botón en la parte superior derecha
```

---

## Paso 3️⃣: Subir tu Archivo

### Opción A: Arrastrar y Soltar (Drag & Drop)

```
1. Abre la carpeta donde está tu archivo CSV
2. Arrastra el archivo a la zona de carga
3. Suelta el archivo
4. Verás el nombre del archivo aparecer
```

### Opción B: Seleccionar Archivo

```
1. Click en la zona de carga
2. Se abre el explorador de archivos
3. Busca tu archivo CSV
4. Click en "Abrir"
5. Verás el nombre del archivo aparecer
```

---

## Paso 4️⃣: Validar el Archivo (IMPORTANTE)

### ¿Por qué validar?

✅ Detecta errores ANTES de importar  
✅ Te muestra qué datos se van a importar  
✅ Te da tiempo para corregir errores  
✅ Evita problemas en la base de datos  

### Cómo validar

```
1. Después de subir el archivo
2. Click en el botón "🔍 Validar Archivo"
3. Espera unos segundos
4. Revisa los resultados
```

### Interpretando los Resultados

#### ✅ Todo Válido
```
Registros Válidos: 50
Advertencias: 0
Errores: 0

→ Puedes importar sin problemas
```

#### ⚠️ Con Advertencias
```
Registros Válidos: 50
Advertencias: 5
Errores: 0

Ejemplo de advertencia:
"Fila 2: DNI '1234567' se normalizará a '01234567'"

→ Puedes importar, pero revisa las advertencias
```

#### ❌ Con Errores
```
Registros Válidos: 45
Advertencias: 0
Errores: 5

Ejemplo de error:
"Fila 3: Tipo de Asistente 'PARTICIPANTE' no es válido"

→ NO puedes importar, debes corregir los errores
```

---

## Paso 5️⃣: Corregir Errores (si es necesario)

### Errores Comunes y Soluciones

#### Error: "DNI inválido"
```
❌ Problema: DNI tiene letras o símbolos
✅ Solución: Usa solo números

Incorrecto: ABC12345, 12-345-678
Correcto: 12345678
```

#### Error: "Tipo de Asistente inválido"
```
❌ Problema: Tipo no es válido
✅ Solución: Usa solo estos valores

Incorrecto: PARTICIPANTE, INVITADO, EXPOSITOR
Correcto: ASISTENTE, PONENTE, ORGANIZADOR
```

#### Error: "Formato de fecha inválido"
```
❌ Problema: Fecha en formato incorrecto
✅ Solución: Usa formato DD/MM/YYYY

Incorrecto: 2025-11-15, 15-11-2025, 11/15/2025
Correcto: 15/11/2025
```

#### Error: "Columna faltante"
```
❌ Problema: Falta una columna requerida
✅ Solución: Agrega la columna faltante

Verifica que tengas las 5 columnas:
1. DNI
2. Nombres y Apellidos
3. Fecha del Evento
4. Tipo de Asistente
5. Nombre del Evento
```

### Cómo Corregir

```
1. Anota los errores mostrados
2. Abre tu archivo CSV
3. Corrige los errores
4. Guarda el archivo
5. Vuelve al paso 3 (subir archivo)
6. Valida nuevamente
```

---

## Paso 6️⃣: Importar los Datos

### Cuando estés listo

```
1. Asegúrate de que la validación fue exitosa
2. Click en el botón "✅ Importar Datos"
3. Espera a que termine (puede tomar unos segundos)
4. Verás un mensaje de confirmación
```

### Mensajes de Confirmación

#### ✅ Importación Exitosa
```
"✓ Se importaron 50 participantes exitosamente"

→ Todos los datos se guardaron correctamente
```

#### ⚠️ Importación Parcial
```
"✓ Se importaron 45 participantes exitosamente"
"⚠ Se encontraron 5 errores"

→ Algunos datos se guardaron, otros no
→ Revisa los errores mostrados
```

#### ❌ Importación Fallida
```
"✗ Error en la importación"

→ Ningún dato se guardó
→ Revisa los errores y vuelve a intentar
```

---

## Paso 7️⃣: Verificar los Datos

### Después de importar

```
1. Ve a la lista de Participantes
2. Busca los participantes importados
3. Verifica que los datos sean correctos
4. Si hay errores, puedes editarlos manualmente
```

### Búsqueda Rápida

```
Usa el buscador en la parte superior:
- Busca por DNI
- Busca por nombre
- Filtra por evento
```

---

## 💡 Consejos y Trucos

### 1. Usa el Archivo de Ejemplo

```
Descarga: ejemplo-importacion.csv
Modifica con tus datos
Importa
```

### 2. Valida Siempre Primero

```
NUNCA importes sin validar primero
La validación te ahorra tiempo y problemas
```

### 3. Importa en Lotes Pequeños

```
Si tienes muchos participantes:
- Divide en archivos de 50-100 registros
- Importa uno por uno
- Verifica cada lote
```

### 4. Guarda una Copia de Seguridad

```
Antes de importar:
- Guarda una copia de tu archivo CSV
- Por si necesitas volver a intentar
```

### 5. Revisa los DNI

```
El sistema normaliza automáticamente:
1234567 → 01234567

Esto es normal y correcto
```

---

## ❓ Preguntas Frecuentes

### ¿Puedo importar el mismo participante dos veces?

```
Sí, pero se actualizarán sus datos.
Si el DNI y evento ya existen, se actualiza.
Si no existen, se crea uno nuevo.
```

### ¿Qué pasa si me equivoco?

```
Puedes:
1. Editar manualmente en la lista de participantes
2. Eliminar el participante y volver a importar
3. Importar nuevamente con los datos correctos
```

### ¿Cuántos participantes puedo importar a la vez?

```
Recomendado: 50-100 por archivo
Máximo: Sin límite, pero archivos grandes son más lentos
Tamaño máximo del archivo: 10MB
```

### ¿Puedo usar Excel?

```
Sí, pero debes guardar como CSV:
1. Abre tu archivo en Excel
2. Archivo → Guardar como
3. Tipo: CSV (delimitado por comas)
4. Guardar
```

### ¿Qué hago si el sistema está lento?

```
1. Divide tu archivo en partes más pequeñas
2. Importa en horarios de menor uso
3. Contacta al administrador si persiste
```

---

## 🆘 ¿Necesitas Ayuda?

### Si algo no funciona:

1. **Revisa esta guía nuevamente**
   - Asegúrate de seguir todos los pasos

2. **Verifica tu archivo CSV**
   - Usa el archivo de ejemplo como referencia
   - Compara con el formato requerido

3. **Limpia la caché del navegador**
   - Presiona Ctrl + F5 (Windows)
   - Presiona Cmd + Shift + R (Mac)

4. **Contacta al administrador**
   - Proporciona el mensaje de error
   - Envía tu archivo CSV (si es posible)

---

## ✅ Checklist Final

Antes de importar, verifica:

- [ ] Mi archivo es .csv
- [ ] Tiene las 5 columnas requeridas
- [ ] Los nombres de columnas son exactos
- [ ] Los DNI solo tienen números
- [ ] Las fechas están en formato DD/MM/YYYY
- [ ] Los tipos son ASISTENTE, PONENTE u ORGANIZADOR
- [ ] No hay filas vacías
- [ ] El archivo es menor a 10MB
- [ ] Validé el archivo primero
- [ ] Revisé los resultados de la validación
- [ ] Corregí todos los errores

---

## 🎉 ¡Listo!

Ahora sabes cómo importar participantes desde CSV.

**Recuerda los pasos:**
1. Preparar archivo CSV
2. Acceder al sistema
3. Subir archivo
4. Validar (IMPORTANTE)
5. Corregir errores (si hay)
6. Importar
7. Verificar

**¡Buena suerte con tu importación!** 🚀

---

**Última actualización:** 19 Nov 2025  
**Versión:** 1.0  
**Soporte:** Contacta al administrador del sistema
