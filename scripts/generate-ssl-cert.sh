#!/bin/bash

# Script para generar certificados SSL auto-firmados para desarrollo/testing
# NO usar en producción - usar Let's Encrypt o certificados comerciales

set -e

echo "=========================================="
echo "Generador de Certificados SSL Auto-firmados"
echo "=========================================="
echo ""
echo "⚠️  ADVERTENCIA: Este script genera certificados auto-firmados"
echo "   Solo usar para desarrollo y testing local"
echo "   Para producción, usar Let's Encrypt o certificados comerciales"
echo ""

# Directorio de certificados
SSL_DIR="ssl"
mkdir -p "$SSL_DIR"

# Configuración por defecto
COUNTRY="PE"
STATE="Lima"
CITY="Lima"
ORGANIZATION="DRTC"
COMMON_NAME="localhost"
DAYS=365

# Permitir personalización
read -p "País (default: PE): " input_country
COUNTRY=${input_country:-$COUNTRY}

read -p "Estado/Provincia (default: Lima): " input_state
STATE=${input_state:-$STATE}

read -p "Ciudad (default: Lima): " input_city
CITY=${input_city:-$CITY}

read -p "Organización (default: DRTC): " input_org
ORGANIZATION=${input_org:-$ORGANIZATION}

read -p "Nombre de dominio (default: localhost): " input_cn
COMMON_NAME=${input_cn:-$COMMON_NAME}

read -p "Días de validez (default: 365): " input_days
DAYS=${input_days:-$DAYS}

echo ""
echo "Generando certificados con la siguiente configuración:"
echo "  País: $COUNTRY"
echo "  Estado: $STATE"
echo "  Ciudad: $CITY"
echo "  Organización: $ORGANIZATION"
echo "  Dominio: $COMMON_NAME"
echo "  Validez: $DAYS días"
echo ""

# Generar clave privada y certificado
echo "📝 Generando clave privada y certificado..."
openssl req -x509 -nodes -days "$DAYS" -newkey rsa:2048 \
  -keyout "$SSL_DIR/key.pem" \
  -out "$SSL_DIR/cert.pem" \
  -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORGANIZATION/CN=$COMMON_NAME"

# Establecer permisos seguros
chmod 600 "$SSL_DIR/key.pem"
chmod 644 "$SSL_DIR/cert.pem"

echo "✅ Certificado generado exitosamente"
echo ""

# Generar parámetros Diffie-Hellman (opcional pero recomendado)
read -p "¿Generar parámetros Diffie-Hellman? (mejora seguridad, toma ~1 minuto) [y/N]: " generate_dh

if [[ "$generate_dh" =~ ^[Yy]$ ]]; then
    echo "🔐 Generando parámetros Diffie-Hellman (esto puede tardar un momento)..."
    openssl dhparam -out "$SSL_DIR/dhparam.pem" 2048
    chmod 644 "$SSL_DIR/dhparam.pem"
    echo "✅ Parámetros DH generados"
    echo ""
    echo "Para usar DH params, descomenta esta línea en nginx.prod.conf:"
    echo "  ssl_dhparam /etc/nginx/ssl/dhparam.pem;"
    echo ""
fi

# Mostrar información del certificado
echo "📋 Información del certificado:"
openssl x509 -in "$SSL_DIR/cert.pem" -noout -subject -dates

echo ""
echo "✅ Certificados SSL generados en el directorio: $SSL_DIR/"
echo ""
echo "Archivos creados:"
echo "  - $SSL_DIR/cert.pem (certificado público)"
echo "  - $SSL_DIR/key.pem (clave privada)"
if [[ "$generate_dh" =~ ^[Yy]$ ]]; then
    echo "  - $SSL_DIR/dhparam.pem (parámetros DH)"
fi
echo ""
echo "Próximos pasos:"
echo "  1. Reiniciar nginx: docker-compose restart nginx"
echo "  2. Acceder a: https://$COMMON_NAME"
echo "  3. Aceptar la advertencia de seguridad del navegador"
echo ""
echo "⚠️  Recuerda: Para producción, usar Let's Encrypt o certificados comerciales"
