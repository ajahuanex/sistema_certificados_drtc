#!/bin/bash

echo "🌐 CONFIGURANDO DOMINIO OFICIAL: certificados.transportespuno.gob.pe"
echo "=================================================================="
echo ""

# Actualizar .env.production con el dominio oficial
echo "📝 Actualizando configuración con dominio oficial..."

# Crear backup
cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)

# Actualizar ALLOWED_HOSTS para incluir el dominio
sed -i 's/ALLOWED_HOSTS=161.132.47.99,localhost,127.0.0.1,certificados.transportespuno.gob.pe/ALLOWED_HOSTS=certificados.transportespuno.gob.pe,www.certificados.transportespuno.gob.pe,161.132.47.99,localhost,127.0.0.1/g' .env.production

# Actualizar CSRF_TRUSTED_ORIGINS para incluir el dominio
sed -i 's|CSRF_TRUSTED_ORIGINS=http://161.132.47.99:7070,http://localhost:7070,http://certificados.transportespuno.gob.pe|CSRF_TRUSTED_ORIGINS=http://certificados.transportespuno.gob.pe,https://certificados.transportespuno.gob.pe,http://www.certificados.transportespuno.gob.pe,https://www.certificados.transportespuno.gob.pe,http://161.132.47.99:7070,http://localhost:7070|g' .env.production

# Actualizar SITE_URL
sed -i 's|SITE_URL=http://161.132.47.99:7070|SITE_URL=http://certificados.transportespuno.gob.pe|g' .env.production

echo "✅ Configuración actualizada"
echo ""

echo "📋 Nueva configuración:"
echo "ALLOWED_HOSTS: $(grep ALLOWED_HOSTS .env.production | cut -d'=' -f2)"
echo "CSRF_TRUSTED_ORIGINS: $(grep CSRF_TRUSTED_ORIGINS .env.production | cut -d'=' -f2)"
echo "SITE_URL: $(grep SITE_URL .env.production | cut -d'=' -f2)"
echo ""

echo "🔄 Reiniciando servicio web..."
docker compose -f docker-compose.prod.yml --env-file .env.production restart web

echo "⏳ Esperando 30 segundos..."
sleep 30

echo "🧪 Verificando configuración:"
echo ""

echo "1. Estado de servicios:"
docker compose -f docker-compose.prod.yml --env-file .env.production ps

echo ""
echo "2. Prueba con dominio (si está configurado en DNS):"
curl -I http://certificados.transportespuno.gob.pe/consulta/ 2>/dev/null || echo "❌ Dominio aún no resuelve (normal si DNS aún se propaga)"

echo ""
echo "3. Prueba con IP (debería seguir funcionando):"
curl -I http://161.132.47.99:7070/consulta/ 2>/dev/null || echo "❌ IP no responde"

echo ""
echo "🎯 CONFIGURACIÓN COMPLETADA"
echo ""
echo "URLs de acceso:"
echo "🌐 Dominio principal: http://certificados.transportespuno.gob.pe"
echo "🔍 Consulta pública: http://certificados.transportespuno.gob.pe/consulta/"
echo "⚙️ Panel admin: http://certificados.transportespuno.gob.pe/admin/"
echo ""
echo "🔄 Respaldo por IP (mientras DNS se propaga):"
echo "🌐 IP directa: http://161.132.47.99:7070"
echo ""
echo "📝 Nota: Si el dominio no responde inmediatamente, espera unos minutos"
echo "    para que la propagación DNS se complete globalmente."