#!/bin/bash

echo "🔧 SOLUCIÓN DEFINITIVA - DESHABILITANDO REDIS"
echo "============================================="

# 1. Detener todos los servicios
echo "1️⃣ Deteniendo servicios..."
docker compose down

# 2. Crear configuración sin Redis
echo "2️⃣ Creando configuración sin Redis..."
cat > .env.production << 'EOF'
SECRET_KEY=8k#m9@x2v$n4p7q!w5e8r1t6y3u0i9o2p5a7s4d6f8g1h3j5k7l9z0x2c4v6b8n
DEBUG=False
ALLOWED_HOSTS=161.132.47.99,localhost,127.0.0.1,certificados.transportespuno.gob.pe
DB_NAME=certificados_db
DB_USER=certificados_user
DB_PASSWORD=X9K2mP8vQ5nR7tY4wE6rT1yU3iO9pA5sD7fG0hJ2kL4zX6cV8bN1mQ3wE5rT7yU
DB_HOST=postgres
DB_PORT=5432
POSTGRES_DB=certificados_db
POSTGRES_USER=certificados_user
POSTGRES_PASSWORD=X9K2mP8vQ5nR7tY4wE6rT1yU3iO9pA5sD7fG0hJ2kL4zX6cV8bN1mQ3wE5rT7yU
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
USE_REDIS=False
REDIS_HOST=
REDIS_PORT=
REDIS_PASSWORD=
PORT=7070
EOF

# 3. Crear docker-compose simplificado (solo web y postgres)
echo "3️⃣ Creando docker-compose simplificado..."
cat > docker-compose-simple.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: certificados_postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  web:
    build: .
    container_name: certificados_web_simple
    ports:
      - "7070:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
    env_file:
      - .env.production
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
EOF

# 4. Iniciar servicios simplificados
echo "4️⃣ Iniciando servicios simplificados..."
docker compose -f docker-compose-simple.yml up -d

# 5. Esperar que se inicien
echo "5️⃣ Esperando que los servicios se inicien..."
sleep 30

# 6. Ejecutar migraciones
echo "6️⃣ Ejecutando migraciones..."
docker compose -f docker-compose-simple.yml exec web python manage.py migrate

# 7. Crear superusuario
echo "7️⃣ Creando superusuario..."
docker compose -f docker-compose-simple.yml exec web python manage.py create_superuser_if_not_exists --noinput

# 8. Recolectar archivos estáticos
echo "8️⃣ Recolectando archivos estáticos..."
docker compose -f docker-compose-simple.yml exec web python manage.py collectstatic --noinput

# 9. Verificar estado
echo "9️⃣ Verificando estado..."
docker compose -f docker-compose-simple.yml ps

# 10. Probar acceso
echo "🔟 Probando acceso..."
sleep 10
curl -I http://localhost:7070/

echo "✅ SOLUCIÓN COMPLETADA"
echo "Prueba ahora: http://161.132.47.99:7070/admin/"
echo "Usuario: admin | Contraseña: admin123"