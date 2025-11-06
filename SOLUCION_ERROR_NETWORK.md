# 🚨 SOLUCIÓN: Error de Red Docker
## "Pool overlaps with other one on this address space"

### 🎯 **EL PROBLEMA**
```
failed to create network sistema_certificados_drtc_certificados_network: 
Error response from daemon: invalid pool request: 
Pool overlaps with other one on this address space
```

**Significa:** Ya tienes otra red Docker usando el mismo rango de IPs (172.20.0.0/16)

---

## ⚡ **SOLUCIÓN RÁPIDA (Recomendada)**

### 1. Limpiar redes Docker existentes:
```bash
# Ver todas las redes
docker network ls

# Eliminar redes no utilizadas
docker network prune -f

# Si eso no funciona, eliminar redes específicas
docker network rm $(docker network ls -q)
```

### 2. Reintentar:
```bash
sudo docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🔧 **SOLUCIÓN ALTERNATIVA: Cambiar Rango de Red**

Si la solución rápida no funciona, cambiar el rango de IP:

### Editar docker-compose.prod.yml:
```bash
nano docker-compose.prod.yml
```

### Buscar la sección networks (al final del archivo):
```yaml
# ANTES (líneas 150-158 aproximadamente)
networks:
  certificados_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16    # ← CAMBIAR ESTE
    driver_opts:
      com.docker.network.bridge.name: br-certificados
```

### Cambiar por un rango diferente:
```yaml
# DESPUÉS - Opción A
networks:
  certificados_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.25.0.0/16    # ← NUEVO RANGO
    driver_opts:
      com.docker.network.bridge.name: br-certificados

# DESPUÉS - Opción B (más seguro)
networks:
  certificados_network:
    driver: bridge
    ipam:
      config:
        - subnet: 192.168.100.0/24  # ← RANGO ALTERNATIVO
    driver_opts:
      com.docker.network.bridge.name: br-certificados
```

---

## 🛠️ **COMANDOS COMPLETOS DE LIMPIEZA**

### Script de limpieza total:
```bash
#!/bin/bash
echo "🧹 Limpiando Docker completamente..."

# Parar todos los contenedores
sudo docker-compose -f docker-compose.prod.yml down

# Limpiar redes
sudo docker network prune -f

# Limpiar volúmenes no utilizados
sudo docker volume prune -f

# Limpiar imágenes no utilizadas
sudo docker image prune -f

# Limpiar sistema completo (opcional - más agresivo)
# sudo docker system prune -a -f

echo "✅ Limpieza completada"
echo "🚀 Intentando levantar servicios..."

sudo docker-compose -f docker-compose.prod.yml up -d --build
```

### Guardar como limpiar_docker.sh:
```bash
nano limpiar_docker.sh
# Copiar el script de arriba
chmod +x limpiar_docker.sh
./limpiar_docker.sh
```

---

## 🔍 **DIAGNÓSTICO AVANZADO**

### Ver redes existentes con detalles:
```bash
# Listar todas las redes
docker network ls

# Ver detalles de una red específica
docker network inspect NOMBRE_DE_RED

# Ver qué redes están usando el rango 172.20.x.x
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}" | grep bridge
```

### Identificar conflictos:
```bash
# Ver todas las subredes en uso
docker network ls -q | xargs docker network inspect | grep -E "Subnet|Name"
```

---

## 🎯 **RANGOS DE IP RECOMENDADOS**

### Para evitar conflictos futuros:
```yaml
# Opción 1 - Rango privado clase A
subnet: 10.10.0.0/16

# Opción 2 - Rango privado clase B  
subnet: 172.25.0.0/16

# Opción 3 - Rango privado clase C
subnet: 192.168.100.0/24

# Opción 4 - Rango específico para certificados
subnet: 172.30.0.0/16
```

---

## 🚨 **SI NADA FUNCIONA - RESET COMPLETO**

### Opción nuclear (cuidado - elimina TODO):
```bash
# ⚠️ CUIDADO: Esto elimina TODOS los contenedores, redes, volúmenes
sudo docker system prune -a -f --volumes

# Reiniciar Docker
sudo systemctl restart docker

# Intentar de nuevo
sudo docker-compose -f docker-compose.prod.yml up -d --build
```

---

## ✅ **VERIFICACIÓN FINAL**

### Después de la solución:
```bash
# 1. Ver que la red se creó correctamente
docker network ls | grep certificados

# 2. Ver detalles de la red
docker network inspect sistema_certificados_drtc_certificados_network

# 3. Verificar que los contenedores están corriendo
sudo docker-compose -f docker-compose.prod.yml ps

# 4. Probar conectividad
curl http://localhost:8080  # o el puerto que uses
```

---

## 🎊 **¡PROBLEMA RESUELTO!**

Una vez solucionado, tu sistema debería estar funcionando perfectamente.

### Comandos de verificación final:
```bash
# Estado de servicios
sudo docker-compose -f docker-compose.prod.yml ps

# Logs para verificar que no hay errores
sudo docker-compose -f docker-compose.prod.yml logs --tail=20

# Probar la aplicación
curl -I http://localhost:8080
```

**¡Tu sistema de certificados está listo!** 🚀