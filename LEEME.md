# 🎓 Sistema de Certificados DRTC Puno

Sistema web para gestión y emisión de certificados digitales de la Dirección Regional de Transportes y Comunicaciones de Puno.

---

## 🚀 Inicio Rápido (3 Pasos)

### Con Docker (Recomendado):

```bash
# 1. Clonar repositorio
git clone https://github.com/ajahuanex/sistema_certificados_drtc.git
cd sistema_certificados_drtc

# 2. Configurar
cp .env.example .env
# Editar .env con tus valores

# 3. Levantar
docker-compose up -d
```

Accede en: **http://localhost**

### Sin Docker:

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar base de datos
python manage.py migrate

# 3. Crear superusuario
python manage.py createsuperuser

# 4. Levantar servidor
python manage.py runserver
```

---

## 📚 Documentación

### Para Empezar:
- **[Despliegue con Docker](docs/deployment/DOCKER_RESUMEN.md)** - Guía rápida de Docker
- **[Guía de Despliegue](docs/DEPLOYMENT_GUIDE.md)** - Despliegue tradicional
- **[Configuración](docs/SETTINGS_CONFIGURATION.md)** - Variables de entorno

### Funcionalidades:
- **[Sistema de Certificados](docs/ADMIN_GUIDE.md)** - Gestión de certificados
- **[Procesamiento con QR](docs/features/SISTEMA_QR_COMPLETO.md)** - Certificados con códigos QR
- **[Dashboard](docs/features/DASHBOARD_IMPLEMENTADO.md)** - Panel de estadísticas
- **[Importación Excel](docs/EXCEL_FORMAT.md)** - Formato de archivos

### Técnica:
- **[Estructura del Proyecto](docs/PROJECT_STRUCTURE.md)** - Organización del código
- **[Comandos de Gestión](docs/MANAGEMENT_COMMANDS.md)** - Comandos disponibles
- **[Firma Digital](docs/DIGITAL_SIGNATURE_SERVICE.md)** - Servicio de firma

---

## ✨ Características Principales

### 🎯 Gestión de Certificados
- Generación automática de certificados PDF
- Códigos QR para verificación
- Firma digital
- Consulta pública por DNI

### 📊 Dashboard Administrativo
- Estadísticas en tiempo real
- Gráficos y métricas
- Filtros avanzados

### 🔄 Procesamiento con QR
- Importación de PDFs originales
- Generación automática de QR
- Exportación para firma externa
- Preview público

### 🔒 Seguridad
- Autenticación de usuarios
- Rate limiting
- Logs de auditoría
- Validación de firma digital

---

## 🛠️ Tecnologías

- **Backend:** Django 5.1, Python 3.11
- **Base de Datos:** PostgreSQL 15
- **Frontend:** Bootstrap 5, JavaScript
- **PDF:** ReportLab, WeasyPrint, PyPDF2
- **Servidor:** Gunicorn, Nginx
- **Contenedores:** Docker, Docker Compose

---

## 📦 Estructura del Proyecto

```
sistema_certificados_drtc/
├── certificates/          # App principal
│   ├── models.py         # Modelos de datos
│   ├── views/            # Vistas
│   ├── services/         # Lógica de negocio
│   └── templates/        # Templates HTML
├── config/               # Configuración Django
├── docs/                 # Documentación
├── static/               # Archivos estáticos
├── templates/            # Templates globales
├── docker-compose.yml    # Configuración Docker
└── requirements.txt      # Dependencias Python
```

---

## 🔧 Comandos Útiles

### Con Docker:
```bash
docker-compose up -d      # Levantar servicios
docker-compose logs -f    # Ver logs
docker-compose down       # Detener servicios
docker-compose exec web python manage.py migrate  # Migraciones
```

### Sin Docker:
```bash
python manage.py migrate              # Ejecutar migraciones
python manage.py createsuperuser      # Crear admin
python manage.py runserver            # Levantar servidor
python manage.py collectstatic        # Recolectar estáticos
```

---

## 🌐 URLs Principales

- **Inicio:** http://localhost/
- **Admin:** http://localhost/admin/
- **Consulta:** http://localhost/consulta/
- **Dashboard:** http://localhost/admin/dashboard/

---

## 👥 Credenciales por Defecto

**Usuario:** admin  
**Password:** (configurado en .env)

⚠️ **Cambiar en producción**

---

## 📝 Variables de Entorno Importantes

```env
# Django
SECRET_KEY=tu-clave-secreta
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com

# Base de Datos
DB_NAME=certificados_db
DB_USER=certificados_user
DB_PASSWORD=tu-password
DB_HOST=db
DB_PORT=5432
```

---

## 🐛 Solución de Problemas

### Error de conexión a base de datos
```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps db
# Reiniciar base de datos
docker-compose restart db
```

### Archivos estáticos no cargan
```bash
# Recolectar estáticos
python manage.py collectstatic --noinput
# O con Docker
docker-compose exec web python manage.py collectstatic --noinput
```

### Más ayuda
Ver [Troubleshooting](docs/deployment/DOCKER_DEPLOYMENT.md#solución-de-problemas)

---

## 📞 Soporte

- **Documentación:** Ver carpeta `docs/`
- **Issues:** GitHub Issues
- **Email:** admin@drtcpuno.gob.pe

---

## 📄 Licencia

Este proyecto es propiedad de la Dirección Regional de Transportes y Comunicaciones de Puno.

---

## 🎉 Versión Actual

**Versión:** 1.1.0  
**Fecha:** Enero 2025  
**Estado:** ✅ Producción

### Últimas Actualizaciones:
- ✅ Sistema de procesamiento con QR
- ✅ Dashboard de estadísticas
- ✅ Dockerización completa
- ✅ Verificación de firma digital

---

**¿Necesitas ayuda?** Lee la [documentación completa](docs/) o contacta al equipo de desarrollo.
