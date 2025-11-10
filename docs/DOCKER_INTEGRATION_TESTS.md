# Docker Integration Tests

## Descripción General

Los tests de integración Docker verifican que la aplicación funciona correctamente cuando se ejecuta en contenedores Docker, incluyendo la comunicación entre servicios, persistencia de datos y configuración del entorno.

## Componentes Testeados

### 1. Conexión a Base de Datos (PostgreSQL)
- Verificación de conexión activa
- Operaciones CRUD
- Transacciones y rollbacks
- Restricciones de clave foránea
- Rendimiento de consultas

### 2. Conexión a Redis
- Operaciones de cache básicas
- Expiración de cache
- Operaciones múltiples (set_many, get_many)
- Almacenamiento de sesiones
- Rendimiento de operaciones

### 3. Comunicación entre Servicios
- Web → PostgreSQL
- Web → Redis
- Persistencia después de reinicios
- Acceso concurrente

### 4. Persistencia de Datos
- Archivos media en volúmenes
- Datos de base de datos
- Relaciones complejas

### 5. Configuración de Entorno
- Variables de entorno
- Configuración de base de datos
- Configuración de cache
- Archivos estáticos y media

### 6. Health Checks
- Health check de base de datos
- Health check de cache
- Health check general del sistema

### 7. Rendimiento
- Rendimiento de consultas
- Rendimiento de cache
- Operaciones masivas

## Estructura de Archivos

```
.
├── certificates/tests/
│   └── test_docker_integration.py      # Tests de integración Docker
├── docker-compose.test.yml              # Configuración Docker para tests
├── test-docker-integration.sh           # Script de tests para Linux/Mac
├── test-docker-integration.bat          # Script de tests para Windows
├── .github/workflows/
│   └── docker-tests.yml                 # Pipeline CI/CD
└── docs/
    └── DOCKER_INTEGRATION_TESTS.md      # Esta documentación
```

## Ejecución de Tests

### Opción 1: Script Automatizado (Recomendado)

#### Linux/Mac:
```bash
chmod +x test-docker-integration.sh
./test-docker-integration.sh
```

#### Windows:
```cmd
test-docker-integration.bat
```

### Opción 2: Docker Compose Manual

```bash
# 1. Construir imágenes
docker-compose -f docker-compose.test.yml build

# 2. Iniciar servicios
docker-compose -f docker-compose.test.yml up -d test-db test-redis

# 3. Esperar a que estén listos
sleep 10

# 4. Ejecutar tests
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py test certificates.tests.test_docker_integration --verbosity=2

# 5. Limpiar
docker-compose -f docker-compose.test.yml down -v
```

### Opción 3: Tests Específicos

```bash
# Test de conexión a base de datos
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py test certificates.tests.test_docker_integration.DockerDatabaseConnectionTest

# Test de conexión a Redis
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py test certificates.tests.test_docker_integration.DockerRedisConnectionTest

# Test de comunicación entre servicios
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py test certificates.tests.test_docker_integration.DockerServiceCommunicationTest

# Test de persistencia
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py test certificates.tests.test_docker_integration.DockerDataPersistenceTest

# Test de health checks
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py test certificates.tests.test_docker_integration.DockerHealthCheckTest
```

## Clases de Test

### DockerDatabaseConnectionTest
Verifica la conexión y operaciones con PostgreSQL:
- `test_database_connection_is_active`: Conexión activa
- `test_database_is_postgresql`: Verificación del motor
- `test_database_crud_operations`: Operaciones CRUD
- `test_database_transactions`: Transacciones y rollbacks
- `test_database_foreign_key_constraints`: Restricciones FK

### DockerRedisConnectionTest
Verifica la conexión y operaciones con Redis:
- `test_redis_connection_is_active`: Conexión activa
- `test_redis_cache_operations`: Operaciones básicas
- `test_redis_cache_expiration`: Expiración de cache
- `test_redis_cache_many_operations`: Operaciones múltiples
- `test_redis_session_storage`: Almacenamiento de sesiones

### DockerServiceCommunicationTest
Verifica la comunicación entre servicios:
- `test_web_to_database_communication`: Web → DB
- `test_web_to_redis_communication`: Web → Redis
- `test_database_persistence_after_restart`: Persistencia
- `test_concurrent_database_access`: Acceso concurrente

### DockerDataPersistenceTest
Verifica la persistencia de datos:
- `test_media_files_persistence`: Archivos media
- `test_database_data_persistence`: Datos de BD

### DockerEnvironmentConfigTest
Verifica la configuración del entorno:
- `test_environment_variables_loaded`: Variables de entorno
- `test_database_configuration`: Config de BD
- `test_cache_configuration`: Config de cache
- `test_static_and_media_configuration`: Config de archivos

### DockerHealthCheckTest
Verifica los health checks:
- `test_database_health_check`: Health check de BD
- `test_cache_health_check`: Health check de cache
- `test_overall_health_check`: Health check general

### DockerPerformanceTest
Verifica el rendimiento:
- `test_database_query_performance`: Rendimiento de consultas
- `test_cache_performance`: Rendimiento de cache

## Configuración de Test

### docker-compose.test.yml

El archivo de configuración define servicios aislados para testing:

```yaml
services:
  test-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: test_certificados
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 5s
      timeout: 5s
      retries: 5

  test-redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  test-web:
    build: .
    command: python manage.py test
    depends_on:
      test-db:
        condition: service_healthy
      test-redis:
        condition: service_healthy
```

## CI/CD Integration

### GitHub Actions

El workflow `.github/workflows/docker-tests.yml` ejecuta automáticamente los tests en cada push o pull request:

```yaml
name: Docker Integration Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  docker-integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Docker tests
        run: ./test-docker-integration.sh
```

### Ejecución Manual del Workflow

```bash
# Desde GitHub UI: Actions → Docker Integration Tests → Run workflow
# O usando GitHub CLI:
gh workflow run docker-tests.yml
```

## Troubleshooting

### Error: "PostgreSQL no está disponible"

```bash
# Verificar logs de PostgreSQL
docker-compose -f docker-compose.test.yml logs test-db

# Verificar que el puerto no está en uso
netstat -an | grep 5433

# Reiniciar servicios
docker-compose -f docker-compose.test.yml restart test-db
```

### Error: "Redis no está disponible"

```bash
# Verificar logs de Redis
docker-compose -f docker-compose.test.yml logs test-redis

# Verificar conexión manual
docker-compose -f docker-compose.test.yml exec test-redis redis-cli ping

# Reiniciar servicios
docker-compose -f docker-compose.test.yml restart test-redis
```

### Error: "Tests fallan por timeout"

```bash
# Aumentar tiempo de espera en el script
# Editar test-docker-integration.sh y cambiar:
sleep 10  # a sleep 20 o más
```

### Error: "Volúmenes con datos antiguos"

```bash
# Limpiar completamente
docker-compose -f docker-compose.test.yml down -v
docker volume prune -f

# Reconstruir desde cero
docker-compose -f docker-compose.test.yml build --no-cache
```

### Error: "Puertos en uso"

```bash
# Cambiar puertos en docker-compose.test.yml
# PostgreSQL: 5433 → 5434
# Redis: 6380 → 6381
```

## Mejores Prácticas

### 1. Aislamiento de Tests
- Usar base de datos separada para tests
- Limpiar datos después de cada test
- No compartir estado entre tests

### 2. Velocidad de Ejecución
- Usar imágenes Alpine cuando sea posible
- Cachear capas de Docker
- Ejecutar tests en paralelo cuando sea posible

### 3. Mantenibilidad
- Documentar cada test claramente
- Usar nombres descriptivos
- Mantener tests independientes

### 4. Cobertura
- Cubrir casos exitosos y de error
- Probar límites y casos extremos
- Verificar comportamiento bajo carga

## Métricas de Éxito

Los tests deben cumplir con:
- ✅ 100% de tests pasando
- ✅ Tiempo de ejecución < 5 minutos
- ✅ Cobertura de código > 80%
- ✅ Sin warnings de deprecación
- ✅ Sin memory leaks

## Integración con Desarrollo

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
./test-docker-integration.sh
if [ $? -ne 0 ]; then
    echo "Docker integration tests failed. Commit aborted."
    exit 1
fi
```

### Pre-push Hook

```bash
# .git/hooks/pre-push
#!/bin/bash
echo "Running Docker integration tests before push..."
./test-docker-integration.sh
```

## Recursos Adicionales

- [Docker Documentation](https://docs.docker.com/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [PostgreSQL in Docker](https://hub.docker.com/_/postgres)
- [Redis in Docker](https://hub.docker.com/_/redis)

## Soporte

Para problemas o preguntas:
1. Revisar esta documentación
2. Verificar logs de contenedores
3. Consultar issues en el repositorio
4. Contactar al equipo de desarrollo
