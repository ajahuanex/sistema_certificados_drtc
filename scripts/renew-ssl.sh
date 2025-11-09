#!/bin/bash

# Script para renovar certificados SSL de Let's Encrypt
# Usar con cron para renovación automática

set -e

echo "=========================================="
echo "Renovación de Certificados SSL"
echo "=========================================="
echo ""

# Configuración
DOMAIN="${SSL_DOMAIN:-localhost}"
EMAIL="${SSL_EMAIL:-admin@example.com}"
SSL_DIR="ssl"
LETSENCRYPT_DIR="/etc/letsencrypt/live/$DOMAIN"

# Verificar si estamos usando Let's Encrypt
if [ ! -d "$LETSENCRYPT_DIR" ]; then
    echo "⚠️  No se encontraron certificados de Let's Encrypt para $DOMAIN"
    echo "   Directorio esperado: $LETSENCRYPT_DIR"
    echo ""
    echo "Para obtener certificados de Let's Encrypt:"
    echo "  1. Instalar certbot: sudo apt-get install certbot"
    echo "  2. Obtener certificado: sudo certbot certonly --standalone -d $DOMAIN"
    echo "  3. Ejecutar este script nuevamente"
    exit 1
fi

echo "📋 Dominio: $DOMAIN"
echo "📧 Email: $EMAIL"
echo ""

# Intentar renovar certificados
echo "🔄 Intentando renovar certificados..."
if sudo certbot renew --quiet; then
    echo "✅ Renovación exitosa"
    
    # Verificar si los certificados fueron actualizados
    CERT_DATE=$(sudo openssl x509 -in "$LETSENCRYPT_DIR/fullchain.pem" -noout -enddate)
    echo "📅 Fecha de expiración: $CERT_DATE"
    
    # Copiar certificados actualizados
    echo "📝 Copiando certificados actualizados..."
    sudo cp "$LETSENCRYPT_DIR/fullchain.pem" "$SSL_DIR/cert.pem"
    sudo cp "$LETSENCRYPT_DIR/privkey.pem" "$SSL_DIR/key.pem"
    
    # Ajustar permisos
    sudo chown $(whoami):$(whoami) "$SSL_DIR/cert.pem" "$SSL_DIR/key.pem"
    chmod 644 "$SSL_DIR/cert.pem"
    chmod 600 "$SSL_DIR/key.pem"
    
    # Recargar nginx sin downtime
    echo "🔄 Recargando nginx..."
    if docker-compose ps | grep -q nginx; then
        docker-compose exec nginx nginx -s reload
        echo "✅ Nginx recargado exitosamente"
    else
        echo "⚠️  Nginx no está ejecutándose, reiniciar manualmente"
    fi
    
    echo ""
    echo "✅ Certificados renovados y aplicados exitosamente"
    
    # Enviar notificación (opcional)
    if command -v mail &> /dev/null; then
        echo "Certificados SSL renovados exitosamente para $DOMAIN" | \
            mail -s "SSL Renewal Success - $DOMAIN" "$EMAIL"
    fi
else
    echo "❌ Error al renovar certificados"
    
    # Enviar notificación de error (opcional)
    if command -v mail &> /dev/null; then
        echo "Error al renovar certificados SSL para $DOMAIN. Revisar logs." | \
            mail -s "SSL Renewal Failed - $DOMAIN" "$EMAIL"
    fi
    
    exit 1
fi

echo ""
echo "📊 Estado de certificados:"
sudo certbot certificates

echo ""
echo "Próxima renovación automática: dentro de 60 días"
echo "Los certificados de Let's Encrypt expiran cada 90 días"
