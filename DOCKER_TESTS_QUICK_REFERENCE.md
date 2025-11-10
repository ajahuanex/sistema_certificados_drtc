# Docker Integration Tests - Quick Reference

## Comandos Rápidos

### Ejecutar Todos los Tests

```bash
# Linux/Mac
./test-docker-integration.sh

# Windows
test-docker-integration.bat
```

### Ejecutar Tests Específicos

```bash
# Test de base de datos
docker-compose -f docker-compose.test.yml run --rm test-web \
  python manage.py test certificates.tests.test_docker_integration.DockerDatabaseConnectionTest

# Test de Redis
docker-compose -f docker-compose.test.yml run --rm test-web \
  python manage.py test certificates.tests.test_docker_integration.DockerRedisConnectionTest

# Test de comunicación
docker-compose -f docker-compose.test.yml run --rm test-web \
  python manage.py test certificates.tests.test_docker_integration.DockerServiceCommunicationTest

# Test de persistencia
docker-compose -f docker-compose.test.yml run --rm test-web \
  python manage.py test certificates.tests.test_docker_integration.DockerDataPersistenceTest

# Test de health checks
docker-compose -f docker-compose.test.yml run --rm test-web \
  python manage.py test certificates.tests.test_docker_integration.DockerHealthCheckTest

# Test de rendimiento
docker-compose -f docker-compose.test.yml run --rm test-web \
  python manage.py test certificates.tests.test_docker_integration.DockerPerformanceTest
```

### Verificación Manual de Servicios

```bash
# Verificar PostgreSQL
docker-compose -f docker-compose.test.yml exec test-db \
  pg_isready -U test_user -d test_certificados

# Verificar Redis
docker-compose -f docker-compose.test.yml exec test-redis redis-cli ping

# Verificar conexión desde web
docker-compose -f docker-compose.test.yml run --rm test-web \
  python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('OK')"
```

### Limpieza

```bash
# Detener y eliminar contenedores
docker-compose -f docker-compose.test.yml down

# Detener y eliminar contenedores + volúmenes
docker-compose -f docker-compose.test.yml down -v

# Limpiar todo (incluyendo imágenes)
docker-compose -f docker-compose.test.yml down -v --rmi all
```

### Debugging

```bash
# Ver logs de todos los servicios
docker-compose -f docker-compose.test.yml logs

# Ver logs de un servicio específico
docker-compose -f docker-compose.test.yml logs test-db
docker-compose -f docker-compose.test.yml logs test-redis
docker-compose -f docker-compose.test.yml logs test-web

# Seguir logs en tiempo real
docker-compose -f docker-compose.test.yml logs -f

# Entrar a un contenedor
docker-compose -f docker-compose.test.yml exec test-db bash
docker-compose -f docker-compose.test.yml exec test-redis sh
docker-compose -f docker-compose.test.yml run --rm test-web bash
```

### Reconstruir Imágenes

```bash
# Reconstruir sin cache
docker-compose -f docker-compose.test.yml build --no-cache

# Reconstruir solo el servicio web
docker-compose -f docker-compose.test.yml build test-web
```

## Estructura de Tests

```
certificates/tests/test_docker_integration.py
├── DockerDatabaseConnectionTest
│   ├── test_database_connection_is_active
│   ├── test_database_is_postgresql
│   ├── test_database_crud_operations
│   ├── test_database_transactions
│   └── test_database_foreign_key_constraints
├── DockerRedisConnectionTest
│   ├── test_redis_connection_is_active
│   ├── test_redis_cache_operations
│   ├── test_redis_cache_expiration
│   ├── test_redis_cache_many_operations
│   └── test_redis_session_storage
├── DockerServiceCommunicationTest
│   ├── test_web_to_database_communication
│   ├── test_web_to_redis_communication
│   ├── test_database_persistence_after_restart
│   └── test_concurrent_database_access
├── DockerDataPersistenceTest
│   ├── test_media_files_persistence
│   └── test_database_data_persistence
├── DockerEnvironmentConfigTest
│   ├── test_environment_variables_loaded
│   ├── test_database_configuration
│   ├── test_cache_configuration
│   └── test_static_and_media_configuration
├── DockerHealthCheckTest
│   ├── test_database_health_check
│   ├── test_cache_health_check
│   └── test_overall_health_check
└── DockerPerformanceTest
    ├── test_database_query_performance
    └── test_cache_performance
```

## Solución Rápida de Problemas

| Problema | Solución |
|----------|----------|
| PostgreSQL no inicia | `docker-compose -f docker-compose.test.yml restart test-db` |
| Redis no responde | `docker-compose -f docker-compose.test.yml restart test-redis` |
| Tests fallan por timeout | Aumentar `sleep` en el script de tests |
| Puerto en uso | Cambiar puertos en `docker-compose.test.yml` |
| Datos antiguos | `docker-compose -f docker-compose.test.yml down -v` |
| Imagen corrupta | `docker-compose -f docker-compose.test.yml build --no-cache` |

## Variables de Entorno para Tests

```bash
# En docker-compose.test.yml
DJANGO_SETTINGS_MODULE=config.settings.base
DEBUG=True
SECRET_KEY=test-secret-key-for-testing-only
DB_ENGINE=django.db.backends.postgresql
DB_NAME=test_certificados
DB_USER=test_user
DB_PASSWORD=test_password
DB_HOST=test-db
DB_PORT=5432
REDIS_URL=redis://test-redis:6379/0
```

## Checklist de Verificación

- [ ] PostgreSQL está corriendo y responde
- [ ] Redis está corriendo y responde
- [ ] Migraciones aplicadas correctamente
- [ ] Tests de conexión pasan
- [ ] Tests de CRUD pasan
- [ ] Tests de persistencia pasan
- [ ] Tests de health check pasan
- [ ] Tests de rendimiento pasan
- [ ] No hay memory leaks
- [ ] Logs sin errores críticos

## Comandos de Mantenimiento

```bash
# Limpiar contenedores detenidos
docker container prune -f

# Limpiar volúmenes no usados
docker volume prune -f

# Limpiar imágenes no usadas
docker image prune -a -f

# Limpiar todo el sistema Docker
docker system prune -a -f --volumes
```

## Integración con CI/CD

```bash
# Ejecutar en GitHub Actions
gh workflow run docker-tests.yml

# Ver estado del workflow
gh run list --workflow=docker-tests.yml

# Ver logs del último run
gh run view --log
```

## Métricas Esperadas

- **Tiempo de ejecución**: < 5 minutos
- **Tasa de éxito**: 100%
- **Cobertura de código**: > 80%
- **Uso de memoria**: < 2GB
- **Uso de CPU**: < 50%

## Contacto y Soporte

- Documentación completa: `docs/DOCKER_INTEGRATION_TESTS.md`
- Issues: GitHub Issues
- Equipo: Desarrollo DRTC
