#!/bin/bash

echo "=========================================="
echo "PRUEBA DE IMPORTACIÓN CSV EN PRODUCCIÓN"
echo "=========================================="
echo ""

# Crear archivo CSV de prueba
cat > test_participantes.csv << 'EOF'
DNI,Nombres y Apellidos,Fecha del Evento,Tipo de Asistente,Nombre del Evento
12345678,Juan Pérez García,15/08/2024,ASISTENTE,Capacitación en Seguridad Vial 2024
87654321,María López Quispe,15/08/2024,PONENTE,Capacitación en Seguridad Vial 2024
EOF

echo "✓ Archivo CSV de prueba creado: test_participantes.csv"
echo ""
echo "Contenido del archivo:"
cat test_participantes.csv
echo ""
echo "=========================================="
echo "INSTRUCCIONES:"
echo "=========================================="
echo ""
echo "1. Accede a: http://161.132.47.92:7070/admin/"
echo "2. Inicia sesión con tus credenciales"
echo "3. Ve a 'Participantes'"
echo "4. Haz clic en 'Importar desde CSV'"
echo "5. Sube el archivo: test_participantes.csv"
echo "6. Marca 'Solo validar' para probar primero"
echo "7. Haz clic en 'Importar'"
echo ""
echo "Si la validación es exitosa:"
echo "8. Vuelve a subir el archivo"
echo "9. NO marques 'Solo validar'"
echo "10. Haz clic en 'Importar' para importar los datos"
echo ""
echo "=========================================="
echo "FORMATO DEL CSV:"
echo "=========================================="
echo ""
echo "Columnas requeridas:"
echo "  - DNI: Número de DNI (8 dígitos)"
echo "  - Nombres y Apellidos: Nombre completo"
echo "  - Fecha del Evento: Formato DD/MM/YYYY"
echo "  - Tipo de Asistente: ASISTENTE, PONENTE u ORGANIZADOR"
echo "  - Nombre del Evento: Nombre del evento"
echo ""
echo "Archivo de prueba listo en: $(pwd)/test_participantes.csv"
echo ""
