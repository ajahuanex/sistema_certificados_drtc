# 📍 Dónde Encontrar la Importación de Certificados Externos

## 🎯 Ubicaciones de Acceso

La funcionalidad de importación de certificados externos está disponible en **3 lugares** del admin:

### 1. 🏠 Página Principal del Admin

**URL**: `http://127.0.0.1:8000/admin/`

**Ubicación**: En la parte superior, verás dos tarjetas:

```
┌─────────────────────────────────┐  ┌──────────────────────────────────┐
│ 📥 Importar Participantes       │  │ 🔗 Importar Certificados Externos│
│                                 │  │                                  │
│ Importa participantes desde    │  │ Importa certificados de otros    │
│ Excel y genera certificados    │  │ sistemas mediante URLs           │
│ automáticamente                │  │                                  │
│                                 │  │                                  │
│ [📄 Importar Excel]            │  │ [🌐 Importar Externos]          │
└─────────────────────────────────┘  └──────────────────────────────────┘
```

**Acción**: Haz clic en **"🌐 Importar Externos"**

---

### 2. 📋 Lista de Certificados

**URL**: `http://127.0.0.1:8000/admin/certificates/certificate/`

**Ubicación**: En la parte superior de la lista de certificados, verás un cuadro azul:

```
┌────────────────────────────────────────────────────────────────┐
│ 📤 Acciones de Importación:                                    │
│                                                                │
│ [📥 Importar Participantes]  [🔗 Importar Certificados Externos]│
│                                                                │
│ Importar Participantes: Crea participantes y genera           │
│ certificados automáticamente desde Excel.                      │
│ Importar Externos: Registra certificados de otros sistemas    │
│ mediante URLs.                                                 │
└────────────────────────────────────────────────────────────────┘
```

**Acción**: Haz clic en **"🔗 Importar Certificados Externos"**

---

### 3. 🔗 URL Directa

**URL**: `http://127.0.0.1:8000/admin/import-external/`

**Acción**: Copia y pega esta URL directamente en tu navegador

---

## 🖼️ Capturas Visuales

### Vista del Admin Principal

```
Admin Home
├── 📊 Dashboard de Estadísticas
│   └── [🚀 Ver Dashboard]
│
├── 📥 Importar Participantes          🔗 Importar Certificados Externos
│   Importa participantes desde        Importa certificados de otros
│   Excel y genera certificados        sistemas mediante URLs
│   automáticamente
│   [📄 Importar Excel]                [🌐 Importar Externos] ← AQUÍ
│
└── Aplicaciones
    ├── Certificates
    │   ├── Events
    │   ├── Participants
    │   ├── Certificates
    │   └── ...
    └── ...
```

### Vista de Lista de Certificados

```
Certificados
┌────────────────────────────────────────────────────────────┐
│ 📤 Acciones de Importación:                                │
│ [📥 Importar Participantes]  [🔗 Importar Externos] ← AQUÍ │
└────────────────────────────────────────────────────────────┘

Filtros:
☐ Firmado digitalmente
☐ Certificado Externo ← NUEVO FILTRO
☐ Generado el
☐ Firmado el

Lista de certificados:
UUID | Participante | DNI | Evento | Tipo | Estado | Generado
...
```

---

## 🎨 Identificación Visual

### Colores de las Tarjetas

- **Verde** (📥): Importar Participantes
- **Morado** (🔗): Importar Certificados Externos ← **ESTA ES LA QUE BUSCAS**

### Iconos

- 📥 = Importar Participantes (genera certificados nuevos)
- 🔗 = Importar Certificados Externos (registra URLs)

---

## 📝 Pasos Rápidos

### Opción 1: Desde el Admin Principal

1. Ve a `http://127.0.0.1:8000/admin/`
2. Busca la tarjeta **MORADA** que dice "🔗 Importar Certificados Externos"
3. Haz clic en **"🌐 Importar Externos"**

### Opción 2: Desde Lista de Certificados

1. Ve a `http://127.0.0.1:8000/admin/certificates/certificate/`
2. En la parte superior, busca el cuadro azul
3. Haz clic en **"🔗 Importar Certificados Externos"**

### Opción 3: URL Directa

1. Copia: `http://127.0.0.1:8000/admin/import-external/`
2. Pega en tu navegador
3. ¡Listo!

---

## 🔍 Características Visuales de la Página

Cuando llegues a la página de importación, verás:

```
┌─────────────────────────────────────────────────────────────┐
│ Importar Certificados Externos                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📋 Instrucciones de Importación de Certificados Externos   │
│                                                             │
│ ℹ️ ¿Qué es esto?                                           │
│ Esta funcionalidad permite importar certificados que       │
│ fueron generados en otros sistemas...                      │
│                                                             │
│ ⚠️ Importante:                                             │
│ • Los certificados externos NO se almacenan en este sistema│
│ • Se generará un código QR que apunta a la URL externa     │
│ • Los participantes podrán consultar sus certificados...   │
│                                                             │
│ Formato del Archivo Excel                                  │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ Columna              │ Descripción        │ Ejemplo  │  │
│ │ DNI                  │ 8 dígitos          │ 12345678 │  │
│ │ Nombres y Apellidos  │ Nombre completo    │ Juan...  │  │
│ │ ...                  │ ...                │ ...      │  │
│ │ URL del Certificado ⭐│ URL completa       │ https... │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                             │
│ [Choose File] [Importar Certificados Externos]             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Verificación

Para verificar que estás en el lugar correcto, busca:

1. ✅ Título: **"Importar Certificados Externos"**
2. ✅ Columna especial: **"URL del Certificado"** con estrella ⭐
3. ✅ Mención de: **"certificados de otros sistemas"**
4. ✅ Color morado en las tarjetas del admin

---

## 🆘 Si No Encuentras la Funcionalidad

### Verifica que:

1. ✅ Estás autenticado como administrador
2. ✅ El servidor está corriendo (`python manage.py runserver`)
3. ✅ Las migraciones están aplicadas (`python manage.py migrate`)
4. ✅ Estás en la URL correcta

### Prueba:

```bash
# Reiniciar servidor
python manage.py runserver

# Acceder directamente
http://127.0.0.1:8000/admin/import-external/
```

---

## 📞 Credenciales de Prueba

Si necesitas iniciar sesión:

- **Usuario**: `admin`
- **Contraseña**: `admin123`

---

## 🎯 Resumen Visual

```
ADMIN HOME
    ↓
[🔗 Importar Certificados Externos] ← TARJETA MORADA
    ↓
Página de Importación
    ↓
Subir Excel con URLs
    ↓
¡Certificados Externos Importados!
```

---

## 📚 Documentación Relacionada

- [Guía Completa de Importación Externa](docs/EXTERNAL_CERTIFICATES_IMPORT.md)
- [Feature: Certificados Externos](FEATURE_EXTERNAL_CERTIFICATES.md)

---

## 🎉 ¡Ya Puedes Importar!

Ahora que sabes dónde está, puedes:

1. Preparar tu archivo Excel con las URLs
2. Acceder a la funcionalidad
3. Importar tus certificados externos
4. ¡Disfrutar de la consulta unificada!
