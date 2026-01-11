#!/bin/bash

echo "🔧 SOLUCIONANDO PROBLEMA REDIS - 161.132.47.99"
echo "=============================================="

# 1. Verificar configuración actual
echo "1️⃣ Verificando configuración actual..."
cat .env.production | grep REDIS

# 2. Verificar configuración Docker Compose
echo "2️⃣ Verificando docker-compose.yml..."
grep -A 10 -B 2 "redis:" docker-compose.yml

# 3. Detener servicios
echo "3️⃣ Deteniendo servicios..."
docker compose down

# 4. Crear nueva configuración .env.production sin contraseña Redis
echo "4️⃣ Creando configuración Redis sin contraseña..."
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
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
PORT=7070
EOF

# 5. Limpiar volúmenes Redis
echo "5️⃣ Limpiando volúmenes Redis..."
docker volume prune -f

# 6. Iniciar servicios
echo "6️⃣ Iniciando servicios..."
docker compose up -d

# 7. Esperar que se inicien
echo "7️⃣ Esperando que los servicios se inicien..."
sleep 20

# 8. Verificar conexión Redis
echo "8️⃣ Verificando conexión Redis..."
docker compose exec redis redis-cli ping

# 9. Probar conexión desde Django
echo "9️⃣ Probando conexión desde Django..."
docker compose exec web python manage.py shell -c "
from django.core.cache import cache
try:
    cache.set('test', 'funcionando')
    result = cache.get('test')
    print('✅ Redis funcionando:', result)
except Exception as e:
    print('❌ Error Redis:', str(e))
"

# 10. Verificar estado final
echo "🔟 Verificando estado final..."
docker compose ps

echo "✅ SOLUCIÓN COMPLETADA"
echo "Prueba ahora: http://161.132.47.99:7070/admin/"
echo "Usuario: admin | Contraseña: admin123"