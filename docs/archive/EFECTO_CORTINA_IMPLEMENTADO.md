# ✨ Efecto Cortina Implementado

## 🎭 Descripción:
Se ha implementado un elegante efecto de cortina (cascade/curtain) que despliega los certificados uno por uno cuando se busca por DNI, creando una experiencia visual fluida y profesional.

---

## 🎬 Animaciones Implementadas:

### 1. Efecto Cortina Principal (Cascade)
```css
@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
        max-height: 0;
    }
    to {
        opacity: 1;
        transform: translateY(0);
        max-height: 500px;
    }
}
```

**Características:**
- Cada certificado aparece desde arriba
- Desplazamiento suave de 20px
- Transición de opacidad 0 → 1
- Duración: 0.4s por certificado

### 2. Delay Escalonado (Efecto Cortina)
```css
.certificates-table tbody tr:nth-child(1) { animation-delay: 0.1s; }
.certificates-table tbody tr:nth-child(2) { animation-delay: 0.2s; }
.certificates-table tbody tr:nth-child(3) { animation-delay: 0.3s; }
/* ... hasta 10 certificados */
```

**Resultado:**
- Los certificados aparecen uno tras otro
- Intervalo de 0.1s entre cada uno
- Efecto visual de "cortina cayendo"

### 3. Fade In para Elementos Principales
```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
```

**Aplicado a:**
- Header de resultados (0.3s)
- Info del participante (0.5s)
- Tabla completa (0.4s)
- Alert de información (0.6s con delay de 1.2s)

### 4. Hover Mejorado
```css
.certificates-table tbody tr:hover {
    background-color: #e3f2fd !important;
    transform: scale(1.01);
    box-shadow: 0 2px 8px rgba(13, 71, 161, 0.15);
    transition: all 0.2s ease-out;
}
```

**Efectos:**
- Fondo azul claro al pasar el mouse
- Escala ligeramente (1%)
- Sombra sutil
- Transición suave

### 5. Botones Interactivos
```css
.btn-download:hover, .btn-verify:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
```

**Efectos:**
- Elevación de 2px al hover
- Sombra más pronunciada
- Feedback visual inmediato

### 6. Badges con Pulso
```javascript
badge.addEventListener('mouseenter', function() {
    this.style.animation = 'pulse 0.5s ease-in-out';
});
```

```css
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}
```

**Efectos:**
- Pulso al pasar el mouse
- Escala 1 → 1.1 → 1
- Duración: 0.5s

---

## 🎯 Secuencia de Animación:

### Tiempo 0s:
- ✅ Header aparece (fade in)

### Tiempo 0.3s:
- ✅ Info del participante aparece

### Tiempo 0.4s:
- ✅ Tabla aparece (contenedor)

### Tiempo 0.5s - 1.5s:
- ✅ Certificados aparecen uno por uno (efecto cortina)
- Certificado 1: 0.5s
- Certificado 2: 0.6s
- Certificado 3: 0.7s
- Certificado 4: 0.8s
- Certificado 5: 0.9s
- ...

### Tiempo 1.8s:
- ✅ Alert de información aparece

---

## 📊 Timing Detallado:

| Elemento | Inicio | Duración | Tipo |
|----------|--------|----------|------|
| **Header** | 0s | 0.3s | Fade In |
| **Info Participante** | 0s | 0.5s | Fade In |
| **Tabla** | 0s | 0.4s | Fade In |
| **Certificado 1** | 0.1s | 0.4s | Slide Down |
| **Certificado 2** | 0.2s | 0.4s | Slide Down |
| **Certificado 3** | 0.3s | 0.4s | Slide Down |
| **Certificado 4** | 0.4s | 0.4s | Slide Down |
| **Certificado 5** | 0.5s | 0.4s | Slide Down |
| **Alert Info** | 1.2s | 0.6s | Fade In |

---

## 🎨 Efectos Interactivos:

### Al Pasar el Mouse:

1. **Sobre una Fila:**
   - Fondo cambia a azul claro
   - Fila se agranda 1%
   - Aparece sombra sutil

2. **Sobre un Botón:**
   - Se eleva 2px
   - Sombra más pronunciada
   - Color más intenso

3. **Sobre un Badge:**
   - Pulso de escala (1 → 1.1 → 1)
   - Duración 0.5s

---

## 💻 JavaScript Adicional:

### Intersection Observer
```javascript
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.1 });
```

**Función:**
- Detecta cuando una fila es visible
- Activa la animación solo cuando entra en viewport
- Optimiza rendimiento en listas largas

---

## ✨ Ventajas del Efecto Cortina:

1. **Visual Atractivo** - Experiencia moderna y profesional
2. **Feedback Claro** - El usuario ve que se están cargando resultados
3. **Jerarquía Visual** - Guía la atención del usuario
4. **Rendimiento** - Animaciones CSS optimizadas
5. **Accesibilidad** - No interfiere con lectores de pantalla
6. **Responsive** - Funciona en todos los dispositivos

---

## 🎬 Cómo se Ve:

### Secuencia Visual:
```
1. [Fade In] Header aparece suavemente
2. [Fade In] Info del participante aparece
3. [Fade In] Tabla (estructura) aparece
4. [Slide Down] Certificado 1 ↓ (desde arriba)
5. [Slide Down] Certificado 2 ↓ (0.1s después)
6. [Slide Down] Certificado 3 ↓ (0.1s después)
7. [Slide Down] Certificado 4 ↓ (0.1s después)
8. [Slide Down] Certificado 5 ↓ (0.1s después)
9. [Fade In] Alert de información aparece
```

### Efecto de Cortina:
```
█████████████████  ← Certificado 1 aparece
  ↓ 0.1s
█████████████████  ← Certificado 2 aparece
  ↓ 0.1s
█████████████████  ← Certificado 3 aparece
  ↓ 0.1s
█████████████████  ← Certificado 4 aparece
  ↓ 0.1s
█████████████████  ← Certificado 5 aparece
```

---

## 🔄 Para Ver el Efecto:

1. Recarga la página: `Ctrl + Shift + R`
2. Busca un DNI con certificados
3. Observa cómo los certificados "caen" como una cortina

---

## 🎯 Personalización:

### Cambiar Velocidad:
```css
/* Más rápido */
.certificates-table tbody tr {
    animation: slideDown 0.2s ease-out forwards;
}

/* Más lento */
.certificates-table tbody tr {
    animation: slideDown 0.6s ease-out forwards;
}
```

### Cambiar Delay:
```css
/* Más rápido (cortina más rápida) */
.certificates-table tbody tr:nth-child(1) { animation-delay: 0.05s; }
.certificates-table tbody tr:nth-child(2) { animation-delay: 0.10s; }

/* Más lento (cortina más dramática) */
.certificates-table tbody tr:nth-child(1) { animation-delay: 0.2s; }
.certificates-table tbody tr:nth-child(2) { animation-delay: 0.4s; }
```

---

**¡Efecto cortina implementado con éxito!** 🎭✨

Los certificados ahora se despliegan elegantemente como una cortina cayendo.
