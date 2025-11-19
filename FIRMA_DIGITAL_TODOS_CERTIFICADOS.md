# Firma Digital - Todos los Certificados

## 📅 Fecha: 19 de Noviembre 2025

## 🎯 Cambio Implementado

**Todos los certificados ahora muestran que contienen firma digital**, con un badge clickeable que lleva directamente al validador de FirmaPerú.

## ✅ Cambios Realizados

### 1. Página de Consulta (`/consulta/`)

#### Antes
```html
{% if certificate.is_signed %}
    <span class="badge bg-success">Firmado</span>
{% else %}
    <span class="badge bg-secondary">Sin Firmar</span>
{% endif %}
```

#### Después
```html
<a href="https://apps.firmaperu.gob.pe/web/validador.xhtml" 
   target="_blank" 
   rel="noopener noreferrer"
   class="badge badge-type bg-success ms-1 text-decoration-none" 
   title="Verificar firma digital en FirmaPerú">
    <i class="bi bi-shield-fill-check"></i> Firma Digital
</a>
```

**Características:**
- ✅ Badge verde con icono de escudo
- ✅ Clickeable (enlace directo a FirmaPerú)
- ✅ Efecto hover (escala y brillo)
- ✅ Tooltip explicativo
- ✅ Se muestra en TODOS los certificados

### 2. Página de Verificación (`/verificar/<uuid>/`)

#### Antes
- Mostraba "FIRMADO" o "SIN FIRMA" según `is_signed`
- Botón de verificación solo si `is_signed=True`

#### Después
```html
<div class="signature-badge">
    <i class="bi bi-shield-fill-check me-2"></i>
    <div class="fw-bold">CONTIENE FIRMA DIGITAL</div>
    <div class="small mt-1">
        Este certificado está firmado digitalmente
    </div>
    <div class="small mt-2">
        <i class="bi bi-check-circle me-1"></i>
        Certificado con validez legal
    </div>
</div>
```

**Botón de Verificación:**
```html
<a href="https://apps.firmaperu.gob.pe/web/validador.xhtml" 
   class="btn btn-success btn-action-verify"
   target="_blank">
    <i class="bi bi-shield-fill-check me-2"></i>Verificar Firma Digital
</a>
```

**Características:**
- ✅ Mensaje único: "CONTIENE FIRMA DIGITAL"
- ✅ Botón de verificación siempre visible
- ✅ Instrucciones claras: "Descarga el PDF y súbelo al validador"
- ✅ Abre FirmaPerú en nueva pestaña

## 🎨 Estilos CSS Agregados

```css
a.badge-type {
    transition: all 0.2s;
    cursor: pointer;
}

a.badge-type:hover {
    transform: scale(1.05);
    box-shadow: 0 2px 8px rgba(40, 167, 69, 0.4);
    filter: brightness(1.1);
}
```

## 📊 Flujo de Usuario

### Desde Página de Consulta
1. Usuario busca certificado por DNI
2. Ve lista de certificados con badge "Firma Digital" (verde)
3. **Opción A**: Click en badge → Abre validador FirmaPerú
4. **Opción B**: Click en "Verificar" → Ve detalles completos

### Desde Página de Verificación
1. Usuario ve detalles del certificado
2. Sección "Firma Digital" muestra: "CONTIENE FIRMA DIGITAL"
3. Botón verde "Verificar Firma Digital"
4. Click → Abre validador FirmaPerú
5. Usuario descarga PDF y lo sube al validador

## 🔗 URL del Validador

**FirmaPerú**: https://apps.firmaperu.gob.pe/web/validador.xhtml

### Proceso de Validación
1. Descargar el certificado PDF
2. Ir al validador de FirmaPerú
3. Subir el archivo PDF
4. El validador muestra:
   - ✅ Firma válida
   - 📅 Fecha de firma
   - 👤 Firmante
   - 🔒 Certificado digital usado

## 🚀 Despliegue

```bash
# Commit y push
git add templates/certificates/query.html templates/certificates/verify.html
git commit -m "Todos los certificados muestran firma digital con link a validador FirmaPerú"
git push origin main

# Copiar a servidor
scp templates/certificates/query.html administrador@161.132.47.92:~/
scp templates/certificates/verify.html administrador@161.132.47.92:~/

# Actualizar contenedores
ssh administrador@161.132.47.92 "cd dockers/sistema_certificados_drtc && \
  docker cp ~/query.html certificados_web:/app/templates/certificates/ && \
  docker cp ~/verify.html certificados_web:/app/templates/certificates/ && \
  docker compose restart web"
```

## 📝 Notas Importantes

1. **Asunción**: Todos los certificados tendrán firma digital
2. **Campo `is_signed`**: Ya no se usa en la UI pública
3. **Validación**: Se hace externamente en FirmaPerú
4. **UX**: Badge clickeable hace más intuitivo el proceso
5. **Consistencia**: Mismo mensaje para todos los certificados

## ✅ Beneficios

- 🎯 **Claridad**: Mensaje único y consistente
- 🔗 **Accesibilidad**: Link directo al validador
- 👆 **Interactividad**: Badge clickeable con hover effect
- 📱 **Responsive**: Funciona en móviles
- ✨ **Profesional**: Diseño moderno y confiable

## 🔍 Pruebas en Producción

**URL**: https://certificados.transportespuno.gob.pe/consulta/

1. Busca un certificado con DNI
2. Verás badge verde "Firma Digital" en cada certificado
3. Haz click en el badge → Abre FirmaPerú
4. O haz click en "Verificar" → Ve detalles
5. En detalles, botón "Verificar Firma Digital" → Abre FirmaPerú

---

**Estado**: ✅ Desplegado en producción
**Commit**: b5082a5
**Fecha**: 19/11/2025
