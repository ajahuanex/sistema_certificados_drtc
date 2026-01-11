# 🚨 SOLUCIÓN INMEDIATA - ERROR CSRF 403

## El Problema
La aplicación está mostrando "Prohibido (403) - La verificación CSRF ha fallado" porque falta configurar `CSRF_TRUSTED_ORIGINS` en el archivo `.env.production`.

## Solución Rápida

### 1. Conectar al servidor
```bash
ssh administrador@161.132.47.92
cd sistema_certificados_drtc
```

### 2. Actualizar .env.production
```bash
# Agregar la línea CSRF_TRUSTED_ORIGINS al archivo
echo "CSRF_TRUSTED_ORIGINS=https://certificados.transportespuno.gob.pe,http://certificados.transportespuno.gob.pe,http://161.132.47.92,https://161.132.47.92" >> .env.production
```

### 3. Reiniciar la aplicación
```bash
docker compose restart web
```

### 4. Verificar
```bash
# Esperar 10 segundos y probar
sleep 10
curl -I http://localhost:7070/admin/
```

## Explicación
- `CSRF_TRUSTED_ORIGINS` le dice a Django qué dominios son confiables para formularios
- Debe incluir tanto HTTP como HTTPS
- Debe incluir tanto el dominio como la IP del servidor

## Resultado Esperado
Después de aplicar esta solución, el admin de Django debería cargar correctamente sin el error 403.

## Si Persiste el Error
Si el error continúa, ejecutar:
```bash
docker compose logs web --tail=50
```

Y revisar los logs para más detalles.