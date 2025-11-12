# 🐧 Comandos Rápidos para Ubuntu Server

## ⚡ Despliegue Rápido

### Opción 1: Script Automatizado (Recomendado)

```bash
# Dar permisos de ejecución
chmod +x deploy-ubuntu.sh

# Ejecutar
./deploy-ubuntu.sh
```

### Opción 2: Comandos Manuales

```bash
# Actualizar código
git pull origin main

# Reconstruir y desplegar
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d
```

---

## 📊 Gestión de Servicios

```bash
# Ver estado
docker compose -f docker-compose.prod.yml ps

# Ver logs en tiempo real
docker compose -f docker-compose.prod.yml logs -f

# Ver logs de un servicio
docker compose -f docker-compose.prod.yml logs web -f

# Reiniciar todos los servicios
docker compose -f docker-compose.prod.yml restart

# Reiniciar un servicio específico
docker compose -f docker-compose.prod.yml restart web

# Detener servicios
docker compose -f docker-compose.prod.yml stop

# Iniciar servicios detenidos
docker compose -f docker-compose.prod.yml start

# Detener y eliminar
docker compose -f docker-compose.prod.yml down

# Detener y eliminar con volúmenes
docker compose -f docker-compose.prod.yml down -v
```

---

## 🐍 Comandos Django

```bash
# Ejecutar migraciones
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Crear superusuario
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Recopilar archivos estáticos
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Shell de Django
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# Ejecutar comando personalizado
docker compose -f docker-compose.prod.yml exec web python manage.py tu_comando
```

---

## 🗄️ Base de Datos

```bash
# Conectar a PostgreSQL
docker compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod

# Backup de base de datos
docker compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore de base de datos
docker compose -f docker-compose.prod.yml exec -T db psql -U certificados_user certificados_prod < backup.sql

# Ver tablas
docker compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod -c "\dt"

# Ver tamaño de BD
docker compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod -c "SELECT pg_size_pretty(pg_database_size('certificados_prod'));"
```

---

## 🔴 Redis

```bash
# Conectar a Redis
docker compose -f docker-compose.prod.yml exec redis redis-cli

# Ping a Redis
docker compose -f docker-compose.prod.yml exec redis redis-cli PING

# Ver todas las claves
docker compose -f docker-compose.prod.yml exec redis redis-cli KEYS "*"

# Limpiar cache
docker compose -f docker-compose.prod.yml exec redis redis-cli FLUSHALL
```

---

## 📁 Archivos y Volúmenes

```bash
# Copiar archivos desde contenedor
docker cp certificados_web_prod:/app/media ./media_backup

# Copiar archivos a contenedor
docker cp ./media_backup certificados_web_prod:/app/media

# Ver volúmenes
docker volume ls

# Inspeccionar volumen
docker volume inspect sistema_certificados_drtc_postgres_data

# Limpiar volúmenes no usados
docker volume prune -f
```

---

## 🔍 Monitoreo y Debug

```bash
# Ver uso de recursos
docker stats

# Ver procesos en un contenedor
docker compose -f docker-compose.prod.yml exec web ps aux

# Ver variables de entorno
docker compose -f docker-compose.prod.yml exec web env

# Ver espacio en disco
df -h

# Ejecutar bash en contenedor
docker compose -f docker-compose.prod.yml exec web bash

# Ver configuración de Docker Compose
docker compose -f docker-compose.prod.yml config

# Inspeccionar contenedor
docker inspect certificados_web_prod
```

---

## 🧹 Limpieza

```bash
# Limpiar contenedores detenidos
docker container prune -f

# Limpiar imágenes no usadas
docker image prune -a -f

# Limpiar todo el sistema
docker system prune -a -f --volumes

# Limpiar solo volúmenes
docker volume prune -f
```

---

## 🔄 Actualización

```bash
# Actualizar código y reiniciar
git pull origin main
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d

# Actualizar con migraciones
git pull origin main
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.yml restart web
```

---

## 🔐 SSL/HTTPS

```bash
# Instalar Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado
sudo certbot certonly --standalone -d certificados.transportespuno.gob.pe

# Renovar certificado
sudo certbot renew

# Probar renovación
sudo certbot renew --dry-run
```

---

## 🔥 Firewall

```bash
# Permitir HTTP
sudo ufw allow 80/tcp

# Permitir HTTPS
sudo ufw allow 443/tcp

# Permitir SSH
sudo ufw allow 22/tcp

# Habilitar firewall
sudo ufw enable

# Ver estado
sudo ufw status

# Ver reglas numeradas
sudo ufw status numbered

# Eliminar regla
sudo ufw delete [número]
```

---

## 🚨 Troubleshooting

```bash
# Ver logs detallados
docker compose -f docker-compose.prod.yml logs --tail=200

# Ver logs de sistema Docker
sudo journalctl -u docker -f

# Reiniciar Docker
sudo systemctl restart docker

# Ver estado de Docker
sudo systemctl status docker

# Reconstruir completamente
docker compose -f docker-compose.prod.yml down -v
docker system prune -a -f
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

---

## 📝 Git

```bash
# Ver estado
git status

# Ver rama actual
git branch

# Actualizar desde GitHub
git pull origin main

# Ver últimos commits
git log --oneline -10

# Ver cambios
git diff

# Guardar cambios temporalmente
git stash

# Restaurar cambios guardados
git stash pop

# Ver remotes
git remote -v
```

---

## 🎯 Comandos Más Usados

```bash
# 1. Ver estado de servicios
docker compose -f docker-compose.prod.yml ps

# 2. Ver logs
docker compose -f docker-compose.prod.yml logs -f

# 3. Reiniciar servicios
docker compose -f docker-compose.prod.yml restart

# 4. Actualizar aplicación
git pull && docker compose -f docker-compose.prod.yml build web && docker compose -f docker-compose.prod.yml up -d

# 5. Backup de BD
docker compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod > backup.sql
```

---

## 📋 Checklist Rápido

```bash
# Verificar todo está funcionando
docker compose -f docker-compose.prod.yml ps  # Todos "Up"
curl http://localhost/health/                  # Responde OK
docker compose -f docker-compose.prod.yml logs --tail=50  # Sin errores
```

---

## 💡 Alias Útiles

Agrega estos alias a tu `~/.bashrc`:

```bash
# Editar .bashrc
nano ~/.bashrc

# Agregar al final:
alias dcp='docker compose -f docker-compose.prod.yml'
alias dcps='docker compose -f docker-compose.prod.yml ps'
alias dcl='docker compose -f docker-compose.prod.yml logs -f'
alias dcr='docker compose -f docker-compose.prod.yml restart'
alias dcu='docker compose -f docker-compose.prod.yml up -d'
alias dcd='docker compose -f docker-compose.prod.yml down'

# Recargar
source ~/.bashrc

# Ahora puedes usar:
dcp ps      # Ver estado
dcl         # Ver logs
dcr         # Reiniciar
```

---

**Sistema:** Ubuntu Server  
**Docker Compose:** v2 (sin guión)  
**Dominio:** certificados.transportespuno.gob.pe
