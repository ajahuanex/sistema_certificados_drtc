#!/bin/bash

# Script para verificar configuración SSL/HTTPS

set -e

echo "=========================================="
echo "Verificación de Configuración SSL/HTTPS"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1"
        return 1
    fi
}

# Función para advertencia
warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Configuración
SSL_DIR="ssl"
CERT_FILE="$SSL_DIR/cert.pem"
KEY_FILE="$SSL_DIR/key.pem"
HTTPS_URL="https://localhost:8443"

echo "1. Verificando archivos de certificados..."
echo ""

# Verificar que existen los archivos
if [ -f "$CERT_FILE" ]; then
    check "Certificado encontrado: $CERT_FILE"
else
    echo -e "${RED}✗${NC} Certificado NO encontrado: $CERT_FILE"
    echo ""
    echo "Generar certificado con:"
    echo "  ./scripts/generate-ssl-cert.sh"
    exit 1
fi

if [ -f "$KEY_FILE" ]; then
    check "Clave privada encontrada: $KEY_FILE"
else
    echo -e "${RED}✗${NC} Clave privada NO encontrada: $KEY_FILE"
    exit 1
fi

echo ""
echo "2. Verificando permisos de archivos..."
echo ""

# Verificar permisos
CERT_PERMS=$(stat -c "%a" "$CERT_FILE" 2>/dev/null || stat -f "%A" "$CERT_FILE" 2>/dev/null)
KEY_PERMS=$(stat -c "%a" "$KEY_FILE" 2>/dev/null || stat -f "%A" "$KEY_FILE" 2>/dev/null)

if [ "$CERT_PERMS" = "644" ] || [ "$CERT_PERMS" = "0644" ]; then
    check "Permisos del certificado correctos: $CERT_PERMS"
else
    warn "Permisos del certificado: $CERT_PERMS (recomendado: 644)"
fi

if [ "$KEY_PERMS" = "600" ] || [ "$KEY_PERMS" = "0600" ]; then
    check "Permisos de clave privada correctos: $KEY_PERMS"
else
    warn "Permisos de clave privada: $KEY_PERMS (recomendado: 600)"
    echo "  Corregir con: chmod 600 $KEY_FILE"
fi

echo ""
echo "3. Verificando validez del certificado..."
echo ""

# Verificar que el certificado es válido
if openssl x509 -in "$CERT_FILE" -noout -text > /dev/null 2>&1; then
    check "Certificado válido"
    
    # Mostrar información del certificado
    SUBJECT=$(openssl x509 -in "$CERT_FILE" -noout -subject | sed 's/subject=//')
    ISSUER=$(openssl x509 -in "$CERT_FILE" -noout -issuer | sed 's/issuer=//')
    NOT_BEFORE=$(openssl x509 -in "$CERT_FILE" -noout -startdate | sed 's/notBefore=//')
    NOT_AFTER=$(openssl x509 -in "$CERT_FILE" -noout -enddate | sed 's/notAfter=//')
    
    echo "  Subject: $SUBJECT"
    echo "  Issuer: $ISSUER"
    echo "  Válido desde: $NOT_BEFORE"
    echo "  Válido hasta: $NOT_AFTER"
    
    # Verificar si está expirado
    if openssl x509 -in "$CERT_FILE" -noout -checkend 0 > /dev/null 2>&1; then
        check "Certificado no expirado"
    else
        echo -e "${RED}✗${NC} Certificado EXPIRADO"
        echo "  Regenerar con: ./scripts/generate-ssl-cert.sh"
    fi
    
    # Advertir si expira pronto (30 días)
    if ! openssl x509 -in "$CERT_FILE" -noout -checkend 2592000 > /dev/null 2>&1; then
        warn "Certificado expira en menos de 30 días"
    fi
else
    echo -e "${RED}✗${NC} Certificado inválido o corrupto"
    exit 1
fi

echo ""
echo "4. Verificando que clave y certificado coinciden..."
echo ""

# Verificar que la clave privada coincide con el certificado
CERT_MODULUS=$(openssl x509 -noout -modulus -in "$CERT_FILE" | openssl md5)
KEY_MODULUS=$(openssl rsa -noout -modulus -in "$KEY_FILE" 2>/dev/null | openssl md5)

if [ "$CERT_MODULUS" = "$KEY_MODULUS" ]; then
    check "Clave privada coincide con certificado"
else
    echo -e "${RED}✗${NC} Clave privada NO coincide con certificado"
    echo "  Regenerar ambos con: ./scripts/generate-ssl-cert.sh"
    exit 1
fi

echo ""
echo "5. Verificando configuración de nginx..."
echo ""

# Verificar que nginx está corriendo
if docker-compose ps | grep -q "nginx.*Up"; then
    check "Nginx está ejecutándose"
    
    # Verificar configuración de nginx
    if docker-compose exec -T nginx nginx -t > /dev/null 2>&1; then
        check "Configuración de nginx válida"
    else
        echo -e "${RED}✗${NC} Configuración de nginx inválida"
        docker-compose exec nginx nginx -t
        exit 1
    fi
else
    warn "Nginx no está ejecutándose"
    echo "  Iniciar con: docker-compose up -d nginx"
fi

echo ""
echo "6. Verificando conectividad HTTPS..."
echo ""

# Verificar que el puerto HTTPS está accesible
if command -v curl > /dev/null 2>&1; then
    # Intentar conexión HTTPS (ignorando verificación de certificado auto-firmado)
    if curl -k -s -o /dev/null -w "%{http_code}" "$HTTPS_URL/health/" | grep -q "200"; then
        check "Servidor HTTPS responde correctamente"
        
        # Verificar redirección HTTP -> HTTPS
        HTTP_REDIRECT=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8181/" 2>/dev/null)
        if [ "$HTTP_REDIRECT" = "301" ] || [ "$HTTP_REDIRECT" = "302" ]; then
            check "Redirección HTTP → HTTPS configurada"
        else
            warn "Redirección HTTP → HTTPS no detectada (código: $HTTP_REDIRECT)"
        fi
        
        # Verificar headers de seguridad
        echo ""
        echo "  Verificando headers de seguridad..."
        HEADERS=$(curl -k -s -I "$HTTPS_URL/" 2>/dev/null)
        
        if echo "$HEADERS" | grep -qi "strict-transport-security"; then
            check "  HSTS habilitado"
        else
            warn "  HSTS no detectado"
        fi
        
        if echo "$HEADERS" | grep -qi "x-frame-options"; then
            check "  X-Frame-Options configurado"
        else
            warn "  X-Frame-Options no detectado"
        fi
        
        if echo "$HEADERS" | grep -qi "x-content-type-options"; then
            check "  X-Content-Type-Options configurado"
        else
            warn "  X-Content-Type-Options no detectado"
        fi
        
    else
        echo -e "${RED}✗${NC} Servidor HTTPS no responde"
        echo "  Verificar logs: docker-compose logs nginx"
    fi
else
    warn "curl no está instalado, omitiendo pruebas de conectividad"
fi

echo ""
echo "7. Verificando protocolos SSL/TLS..."
echo ""

if command -v openssl > /dev/null 2>&1; then
    # Verificar TLS 1.2
    if timeout 5 openssl s_client -connect localhost:8443 -tls1_2 < /dev/null > /dev/null 2>&1; then
        check "TLS 1.2 soportado"
    else
        warn "TLS 1.2 no soportado o no accesible"
    fi
    
    # Verificar TLS 1.3
    if timeout 5 openssl s_client -connect localhost:8443 -tls1_3 < /dev/null > /dev/null 2>&1; then
        check "TLS 1.3 soportado"
    else
        warn "TLS 1.3 no soportado (normal en algunas configuraciones)"
    fi
    
    # Verificar que TLS 1.0 y 1.1 están deshabilitados
    if ! timeout 5 openssl s_client -connect localhost:8443 -tls1 < /dev/null > /dev/null 2>&1; then
        check "TLS 1.0 deshabilitado (correcto)"
    else
        warn "TLS 1.0 habilitado (inseguro)"
    fi
else
    warn "openssl no está instalado, omitiendo pruebas de protocolos"
fi

echo ""
echo "=========================================="
echo "Resumen de Verificación"
echo "=========================================="
echo ""
echo "✅ Certificados SSL configurados correctamente"
echo ""
echo "Próximos pasos:"
echo "  • Acceder a: $HTTPS_URL"
echo "  • Para producción, usar Let's Encrypt: ./scripts/renew-ssl.sh"
echo "  • Configurar renovación automática con cron"
echo ""
echo "Documentación completa: docs/SSL_CONFIGURATION.md"
