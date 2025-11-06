# 🚨 DIAGNÓSTICO: PostgreSQL Unhealthy
## "container certificados_db_prod is unhealthy"

### 🔍 **COMANDOS DE DIAGNÓSTICO INMEDIATO**

Ejecuta estos comandos para ver qué está pasando:

```bash
# 1. Ver logs de PostgreSQL
sudo docker-compose -f docker-compose.prod.yml logs db

# 2. Ver estado detallado de contenedores
sudo docker-compose -f docker-compose.prod.yml ps

# 3. Inspeccionar el contenedor de DB
sudo docker inspect certificados_db_prod

# 4. Intentar conectar manualmente a PostgreSQL
sudo docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres
```

---

## 🛠️ **SOLUCIONES COMUNES**

### **SOLUCIÓN 1: Problema de Variables de Entorno**

Crear archivo `.env.production` si no existe:

```bash
# Crear .env.production
cat > .env.production << 'EOF'
DEBUG=False
SECRET_KEY=tu-clave-super-secreta-minimo-50-caracteres-123456789
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos
DB_NAME=certificados_prod
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=db
DB_PORT=5432

# Configuración adicional
TIME_ZONE=America/Lima
LANGUAGE_CODE=es-pe
EOF
```

### **SOLUCIÓN 2: Reiniciar Solo PostgreSQL**

```bash
# Parar solo la DB
sudo docker-compose -f docker-compose.prod.yml stop db

# Eliminar contenedor problemático
sudo docker-compose -f docker-compose.prod.yml rm -f db

# Levantar solo la DB
sudo docker-compose -f docker-compose.prod.yml up -d db

# Esperar y verificar
sleep 30
sudo docker-compose -f docker-compose.prod.yml logs db
```

### **SOLUCIÓN 3: Configuración Simplificada de PostgreSQL**

Si el problema persiste, simplificar la configuración:

```bash
# Editar docker-compose.prod.yml
nano docker-compose.prod.yml
```

Buscar la sección de PostgreSQL y simplificar:

```yaml
# CAMBIAR LA CONFIGURACIÓN COMPLEJA POR ESTA SIMPLE:
db:
  image: postgres:15-alpine
  container_name: certificados_db_prod
  restart: unless-stopped
  environment:
    POSTGRES_DB: certificados_prod
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres123
  volumes:
    - postgres_data_prod:/var/lib/postgresql/data
  networks:
    - certificados_network
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 30s
    timeout: 10s
    retries: 5
    start_period: 30s
```

---

## ⚡ **SCRIPT DE SOLUCIÓN RÁPIDA**

```bash
#!/bin/bash
echo "🔧 Solucionando PostgreSQL..."

# Crear .env.production básico
cat > .env.production << 'EOF'
DEBUG=False
SECRET_KEY=clave-super-secreta-para-produccion-minimo-50-caracteres-123
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=certificados_prod
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=db
DB_PORT=5432

TIME_ZONE=America/Lima
LANGUAGE_CODE=es-pe
EOF

echo "✅ Archivo .env.production creado"

# Parar todo
sudo docker-compose -f docker-compose.prod.yml down

# Limpiar volúmenes problemáticos
sudo docker volume rm sistema_certificados_drtc_postgres_data_prod 2>/dev/null || true

# Levantar solo PostgreSQL primero
echo "🐘 Levantando PostgreSQL..."
sudo docker-compose -f docker-compose.prod.yml up -d db

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando PostgreSQL..."
sleep 45

# Verificar PostgreSQL
echo "🔍 Verificando PostgreSQL..."
sudo docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL está funcionando"
    echo "🚀 Levantando resto de servicios..."
    sudo docker-compose -f docker-compose.prod.yml up -d
else
    echo "❌ PostgreSQL aún tiene problemas"
    echo "📋 Logs de PostgreSQL:"
    sudo docker-compose -f docker-compose.prod.yml logs db
fi
```

### Guardar y ejecutar:
```bash
nano solucionar_postgres.sh
# Copiar el script de arriba
chmod +x solucionar_postgres.sh
./solucionar_postgres.sh
```

---

## 🔍 **DIAGNÓSTICO AVANZADO**

### Ver logs detallados:
```bash
# Logs completos de PostgreSQL
sudo docker-compose -f docker-compose.prod.yml logs --tail=50 db

# Entrar al contenedor para diagnóstico
sudo docker-compose -f docker-compose.prod.yml exec db bash

# Dentro del contenedor:
ps aux | grep postgres
cat /var/log/postgresql/postgresql*.log
```

### Verificar recursos del sistema:
```bash
# Memoria disponible
free -h

# Espacio en disco
df -h

# Procesos de Docker
sudo docker stats
```

---

## 🎯 **CAUSAS COMUNES**

1. **Variables de entorno faltantes** - `.env.production` no existe
2. **Configuración compleja** - Demasiados parámetros de PostgreSQL
3. **Recursos insuficientes** - Poca RAM o espacio en disco
4. **Conflicto de puertos** - Puerto 5432 ocupado
5. **Permisos de volúmenes** - Problemas de escritura

---

## ✅ **VERIFICACIÓN FINAL**

Una vez solucionado:

```bash
# 1. Estado de contenedores
sudo docker-compose -f docker-compose.prod.yml ps

# 2. Health check de PostgreSQL
sudo docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres

# 3. Conectar a la base de datos
sudo docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d certificados_prod -c "\l"

# 4. Logs sin errores
sudo docker-compose -f docker-compose.prod.yml logs --tail=20 db
```

---

## 🚀 **PRÓXIMOS PASOS**

Una vez que PostgreSQL esté healthy:

1. ✅ Ejecutar migraciones de Django
2. ✅ Crear superusuario
3. ✅ Cargar plantilla por defecto
4. ✅ Probar el sistema completo

**¡Ejecuta el diagnóstico y dime qué encuentras!** 🔍