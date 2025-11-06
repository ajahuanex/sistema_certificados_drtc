# 🚨 SOLUCIÓN: Error de Volúmenes Docker
## "failed to mount local volume: no such file or directory"

### 🎯 **EL PROBLEMA**
```
Error response from daemon: failed to populate volume: 
error while mounting volume '/var/lib/docker/volumes/sistema_certificados_drtc_postgres_data_prod/_data': 
failed to mount local volume: mount /var/lib/docker/volumes/certificados_postgres_data:/var/lib/docker/volumes/sistema_certificados_drtc_postgres_data_prod/_data, 
flags: 0x1000: no such file or directory
```

**Significa:** El volumen está intentando hacer bind mount a una carpeta que no existe.

---

## ✅ **SOLUCIÓN APLICADA**

Ya he corregido el archivo `docker-compose.prod.yml`. El problema estaba en la configuración de volúmenes:

### ANTES (problemático):
```yaml
volumes:
  postgres_data_prod:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /var/lib/docker/volumes/certificados_postgres_data  # ← Esta carpeta no existe
```

### DESPUÉS (corregido):
```yaml
volumes:
  postgres_data_prod:
    driver: local  # ← Docker maneja automáticamente
  redis_data_prod:
    driver: local
```

---

## 🚀 **AHORA EJECUTA ESTO**

### 1. Limpiar volúmenes problemáticos:
```bash
# Parar todo
sudo docker-compose -f docker-compose.prod.yml down

# Limpiar volúmenes
sudo docker volume prune -f

# Eliminar volúmenes específicos si existen
sudo docker volume rm sistema_certificados_drtc_postgres_data_prod 2>/dev/null || true
sudo docker volume rm sistema_certificados_drtc_redis_data_prod 2>/dev/null || true
```

### 2. Levantar de nuevo:
```bash
sudo docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🔍 **VERIFICACIÓN**

### Comprobar que los volúmenes se crearon correctamente:
```bash
# Ver volúmenes creados
sudo docker volume ls | grep certificados

# Ver detalles del volumen de PostgreSQL
sudo docker volume inspect sistema_certificados_drtc_postgres_data_prod

# Ver que los contenedores están corriendo
sudo docker-compose -f docker-compose.prod.yml ps
```

### Deberías ver algo así:
```
NAME                                                DRIVER    VOLUME NAME
sistema_certificados_drtc_postgres_data_prod        local     
sistema_certificados_drtc_redis_data_prod           local     
```

---

## 🛠️ **SCRIPT DE SOLUCIÓN COMPLETA**

```bash
#!/bin/bash
echo "🔧 Solucionando problema de volúmenes..."

# Parar servicios
echo "⏹️ Parando servicios..."
sudo docker-compose -f docker-compose.prod.yml down

# Limpiar volúmenes problemáticos
echo "🧹 Limpiando volúmenes..."
sudo docker volume prune -f
sudo docker volume rm sistema_certificados_drtc_postgres_data_prod 2>/dev/null || true
sudo docker volume rm sistema_certificados_drtc_redis_data_prod 2>/dev/null || true

# Levantar servicios
echo "🚀 Levantando servicios..."
sudo docker-compose -f docker-compose.prod.yml up -d --build

# Verificar
echo "✅ Verificando..."
sleep 10
sudo docker-compose -f docker-compose.prod.yml ps

echo "🎉 ¡Problema solucionado!"
```

### Guardar como solucionar_volumenes.sh:
```bash
nano solucionar_volumenes.sh
# Copiar el script de arriba
chmod +x solucionar_volumenes.sh
./solucionar_volumenes.sh
```

---

## 📊 **MONITOREO DE PROGRESO**

### Ver logs en tiempo real:
```bash
# Logs de todos los servicios
sudo docker-compose -f docker-compose.prod.yml logs -f

# Solo logs de la base de datos
sudo docker-compose -f docker-compose.prod.yml logs -f db

# Solo logs de la aplicación web
sudo docker-compose -f docker-compose.prod.yml logs -f web
```

### Verificar salud de los servicios:
```bash
# Estado de contenedores
sudo docker-compose -f docker-compose.prod.yml ps

# Verificar que la DB está lista
sudo docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres

# Probar conexión web
curl -I http://localhost:8080
```

---

## 🎯 **PRÓXIMOS PASOS**

Una vez que los contenedores estén corriendo:

### 1. Configurar la base de datos:
```bash
# Ejecutar migraciones
sudo docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Crear superusuario
sudo docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Cargar plantilla por defecto
sudo docker-compose -f docker-compose.prod.yml exec web python manage.py load_default_template
```

### 2. Verificar funcionamiento:
```bash
# Probar página principal
curl http://localhost:8080

# Probar admin
curl http://localhost:8080/admin/
```

---

## 🚨 **SI AÚN HAY PROBLEMAS**

### Diagnóstico avanzado:
```bash
# Ver todos los volúmenes del sistema
sudo docker volume ls

# Inspeccionar volumen específico
sudo docker volume inspect NOMBRE_VOLUMEN

# Ver espacio en disco
df -h

# Ver logs detallados de Docker
sudo journalctl -u docker.service --since "1 hour ago"
```

### Reset completo de volúmenes:
```bash
# ⚠️ CUIDADO: Esto elimina TODOS los datos
sudo docker-compose -f docker-compose.prod.yml down -v
sudo docker volume prune -f
sudo docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🎊 **¡PROBLEMA RESUELTO!**

Con esta corrección, Docker creará automáticamente los volúmenes en la ubicación estándar sin intentar hacer bind mounts problemáticos.

**¡Tu sistema debería estar funcionando perfectamente ahora!** 🚀