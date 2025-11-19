#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║         🎨 ACTUALIZAR DASHBOARD - CSS MODERNO                 ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Subir cambios a GitHub
echo "📤 Subiendo cambios a GitHub..."
git add static/admin/css/dashboard.css templates/admin/dashboard.html
git commit -m "Actualizar dashboard con CSS moderno y mejor contraste"
git push origin main

echo ""
echo "✅ Cambios subidos a GitHub"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 COMANDOS PARA EJECUTAR EN EL SERVIDOR:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "ssh root@161.132.47.92"
echo "cd sistema_certificados_drtc"
echo "git pull origin main"
echo "docker compose exec web python manage.py collectstatic --noinput"
echo "docker compose restart web"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Luego abre el navegador y presiona Ctrl+Shift+R para limpiar cache"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
