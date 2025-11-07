#!/bin/bash
# Script de diagnóstico rápido - Linux/Mac
# Sistema de Certificados DRTC

echo "========================================"
echo "DIAGNOSTICO RAPIDO DE PRODUCCION"
echo "========================================"
echo ""

echo "[1] Estado de contenedores:"
echo "----------------------------------------"
docker compose -f docker-compose.prod.yml ps
echo ""

echo "[2] Variables de entorno en contenedor web:"
echo "----------------------------------------"
docker compose -f docker-compose.prod.yml exec web env | grep DJANGO
echo ""

echo "[3] Ultimos 20 logs del contenedor web:"
echo "----------------------------------------"
docker compose -f docker-compose.prod.yml logs --tail=20 web
echo ""

echo "[4] Health checks:"
echo "----------------------------------------"
docker compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Health}}"
echo ""

echo "[5] Uso de recursos:"
echo "----------------------------------------"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo ""

echo "========================================"
echo "DIAGNOSTICO COMPLETADO"
echo "========================================"
echo ""
