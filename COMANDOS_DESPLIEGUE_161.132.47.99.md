# Comandos de Despliegue - Servidor 161.132.47.99

## 🚀 Despliegue Automático

### Opción 1: Script Automático (Windows)
```bash
deploy-servidor-161.132.47.99.bat
```

### Opción 2: Script Automático (Linux/Mac)
```bash
chmod +x deploy-servidor-161.132.47.99.sh
./deploy-servidor-161.132.47.99.sh
```

## 📋 Comandos Manuales Paso a Paso

### 1. Verificar Conexión
```bash
ping 161.132.47.99
```

### 2. Conectar al Servidor
```bash
ssh root@161.132.47.99
```

### 3. Instalar Dependencias
```bash
apt update
apt install -y docker.io docker-compose git curl
systemctl enable docker
systemctl start docker
```

### 4. Preparar Proyecto
```bash
mkdir -p /opt/sistema_certificados_drtc
cd /opt/sistema_certificados_drtc
git clone https://github.com/ajahuanex/sistema_certificados_drtc.git .
```

### 5. Configurar Archivos
```bash
# Copiar desde tu máquina local:
scp .env.production root@161.132.47.99:/opt/sistema_certificados_drtc/
scp docker-compose.prod.yml root@161.132.47.99:/opt/sistema_certificados_drtc/
```

### 6. Desplegar
```bash
cd /opt/sistema_certificados_drtc
chmod +x entrypoint.sh
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### 7. Configurar Base de Datos
```bash
# Esperar 30 segundos para que los servicios se inicien
sleep 30

# Ejecutar migraciones
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Crear superusuario
docker-compose -f docker-compose.prod.yml exec web python manage.py create_superuser_if_not_exists

# Cargar plantilla por defecto
docker-compose -f docker-compose.prod.yml exec web python manage.py load_default_template
```

### 8. Verificar Estado
```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs web
```

## 🌐 URLs de Acceso

- **Aplicación Principal**: http://161.132.47.99:7070
- **Panel Admin**: http://161.132.47.99:7070/admin
- **Dashboard**: http://161.132.47.99:7070/admin/dashboard
- **API Health**: http://161.132.47.99:7070/health/

## 🔐 Credenciales por Defecto

- **Usuario**: admin
- **Contraseña**: admin123

## 🔧 Comandos de Mantenimiento

### Ver Logs
```bash
ssh root@161.132.47.99 "cd /opt/sistema_certificados_drtc && docker-compose -f docker-compose.prod.yml logs -f web"
```

### Reiniciar Servicios
```bash
ssh root@161.132.47.99 "cd /opt/sistema_certificados_drtc && docker-compose -f docker-compose.prod.yml restart"
```

### Actualizar Código
```bash
ssh root@161.132.47.99 "cd /opt/sistema_certificados_drtc && git pull origin main && docker-compose -f docker-compose.prod.yml restart web"
```

### Backup Base de Datos
```bash
ssh root@161.132.47.99 "cd /opt/sistema_certificados_drtc && docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U postgres certificates_db > backup_$(date +%Y%m%d_%H%M%S).sql"
```

## 🚨 Troubleshooting

### Si hay problemas de conexión SSH
```bash
# Verificar que SSH esté habilitado en el servidor
# Asegurarse de tener las claves SSH configuradas
```

### Si Docker no funciona
```bash
ssh root@161.132.47.99 "systemctl status docker"
ssh root@161.132.47.99 "systemctl restart docker"
```

### Si los puertos están ocupados
```bash
ssh root@161.132.47.99 "netstat -tulpn | grep :7070"
ssh root@161.132.47.99 "docker ps -a"
```

### Limpiar contenedores si es necesario
```bash
ssh root@161.132.47.99 "cd /opt/sistema_certificados_drtc && docker-compose -f docker-compose.prod.yml down"
ssh root@161.132.47.99 "docker system prune -f"
```