# 📚 Sistema de Certificados DRTC Puno - Índice de Documentación

## 🚀 Inicio Rápido

### ¿Primera vez aquí?

1. **[LEEME.md](LEEME.md)** ⭐ - **EMPIEZA AQUÍ** - Guía rápida en español
2. **[README.md](README.md)** - Documentación completa (inglés)

### Despliegue Rápido

```bash
# Con Docker (3 comandos)
git clone https://github.com/ajahuanex/sistema_certificados_drtc.git
cd sistema_certificados_drtc
docker-compose up -d
```

Accede en: **http://localhost**

---

## 📖 Documentación por Tema

### 🐳 Despliegue con Docker
- **[DOCKER_RESUMEN.md](docs/deployment/DOCKER_RESUMEN.md)** - Guía rápida de Docker
- **[DOCKER_DEPLOYMENT.md](docs/deployment/DOCKER_DEPLOYMENT.md)** - Guía completa de despliegue
- **[Makefile](docs/deployment/Makefile)** - Comandos simplificados

### ✨ Funcionalidades
- **[Sistema de QR](docs/features/SISTEMA_QR_COMPLETO.md)** - Procesamiento de certificados con QR
- **[Cómo Usar QR](docs/features/COMO_USAR_PROCESAMIENTO_QR.md)** - Guía paso a paso
- **[Dashboard](docs/features/DASHBOARD_IMPLEMENTADO.md)** - Panel de estadísticas
- **[Verificación de Firma](docs/features/VERIFICACION_FIRMA_DIGITAL_AGREGADA.md)** - FirmaPerú

### 📋 Administración
- **[Guía de Admin](docs/ADMIN_GUIDE.md)** - Manual del administrador
- **[Formato Excel](docs/EXCEL_FORMAT.md)** - Cómo importar participantes
- **[Comandos](docs/MANAGEMENT_COMMANDS.md)** - Comandos de gestión
- **[Firma Digital](docs/DIGITAL_SIGNATURE_SERVICE.md)** - Servicio de firma

### ⚙️ Configuración
- **[Guía de Despliegue](docs/DEPLOYMENT_GUIDE.md)** - Despliegue tradicional
- **[Configuración](docs/SETTINGS_CONFIGURATION.md)** - Variables de entorno
- **[PostgreSQL](docs/POSTGRESQL_SETUP.md)** - Configuración de base de datos
- **[Estructura](docs/PROJECT_STRUCTURE.md)** - Organización del proyecto

---

## 🎯 Guías por Rol

### Para Desarrolladores:
1. Leer [README.md](README.md)
2. Ver [Estructura del Proyecto](docs/PROJECT_STRUCTURE.md)
3. Configurar entorno de desarrollo
4. Levantar con Docker: `docker-compose up -d`

### Para Administradores:
1. Leer [LEEME.md](LEEME.md)
2. Ver [Guía de Admin](docs/ADMIN_GUIDE.md)
3. Aprender [Formato Excel](docs/EXCEL_FORMAT.md)
4. Usar [Dashboard](docs/features/DASHBOARD_IMPLEMENTADO.md)

### Para DevOps:
1. Ver [Docker Deployment](docs/deployment/DOCKER_DEPLOYMENT.md)
2. Configurar [Variables de Entorno](docs/SETTINGS_CONFIGURATION.md)
3. Seguir [Guía de Despliegue](docs/DEPLOYMENT_GUIDE.md)
4. Configurar [PostgreSQL](docs/POSTGRESQL_SETUP.md)

---

## 🔍 Buscar por Tema

### Certificados:
- Generar certificados → [Admin Guide](docs/ADMIN_GUIDE.md)
- Importar Excel → [Excel Format](docs/EXCEL_FORMAT.md)
- Firmar digitalmente → [Digital Signature](docs/DIGITAL_SIGNATURE_SERVICE.md)

### QR:
- Sistema completo → [Sistema QR](docs/features/SISTEMA_QR_COMPLETO.md)
- Cómo usar → [Guía de Uso](docs/features/COMO_USAR_PROCESAMIENTO_QR.md)
- Detalles técnicos → [Implementación](docs/features/PROCESAMIENTO_QR_IMPLEMENTADO.md)

### Docker:
- Inicio rápido → [Docker Resumen](docs/deployment/DOCKER_RESUMEN.md)
- Guía completa → [Docker Deployment](docs/deployment/DOCKER_DEPLOYMENT.md)
- Comandos → [Makefile](docs/deployment/Makefile)

### Problemas:
- Troubleshooting → [Docker Deployment](docs/deployment/DOCKER_DEPLOYMENT.md#solución-de-problemas)
- Configuración → [Settings](docs/SETTINGS_CONFIGURATION.md)

---

## 📊 Estructura de Carpetas

```
sistema_certificados_drtc/
├── INICIO.md              ← Estás aquí
├── LEEME.md               ← Guía rápida en español
├── README.md              ← Documentación completa
│
├── docs/                  ← Documentación organizada
│   ├── deployment/        ← Guías de despliegue
│   ├── features/          ← Documentación de funcionalidades
│   ├── ADMIN_GUIDE.md     ← Manual del administrador
│   ├── EXCEL_FORMAT.md    ← Formato de importación
│   └── ...
│
├── certificates/          ← Aplicación principal
├── config/                ← Configuración Django
├── static/                ← Archivos estáticos
├── templates/             ← Templates HTML
└── docker-compose.yml     ← Configuración Docker
```

---

## ⚡ Comandos Rápidos

```bash
# Levantar con Docker
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Detener servicios
docker-compose down
```

---

## 🆘 ¿Necesitas Ayuda?

1. **Primero:** Lee [LEEME.md](LEEME.md) para inicio rápido
2. **Luego:** Busca en este índice el tema que necesitas
3. **Problemas:** Ver sección de troubleshooting en cada guía
4. **Contacto:** admin@drtcpuno.gob.pe

---

## 📝 Notas

- Todos los archivos .md en la raíz son documentación de sesiones de desarrollo
- La documentación organizada está en la carpeta `docs/`
- Para producción, lee [Docker Deployment](docs/deployment/DOCKER_DEPLOYMENT.md)

---

**Versión:** 1.1.0  
**Última actualización:** Enero 2025  
**Estado:** ✅ Producción
