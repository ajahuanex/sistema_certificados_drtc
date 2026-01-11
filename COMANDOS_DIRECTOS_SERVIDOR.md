# 🚨 COMANDOS DIRECTOS PARA EL SERVIDOR

## Ejecuta estos comandos DIRECTAMENTE en el servidor 161.132.47.92

### 1. Conectar al servidor
```bash
ssh administrador@161.132.47.92
cd sistema_certificados_drtc
```

### 2. Agregar CSRF_TRUSTED_ORIGINS al .env.production
```bash
echo "CSRF_TRUSTED_ORIGINS=https://certificados.transportespuno.gob.pe,http://certificados.transportespuno.gob.pe,http://161.132.47.92,https://161.132.47.92" >> .env.production
```

### 3. Verificar que se agregó correctamente
```bash
tail -5 .env.production
```

### 4. Reiniciar la aplicación
```bash
docker compose restart web
```

### 5. Esperar y probar
```bash
sleep 15
curl -I http://localhost:7070/admin/
```

## ¡Eso es todo!

Después de estos comandos, el error CSRF 403 debería desaparecer y podrás acceder al admin normalmente.

## Si quieres verificar el contenido completo del .env.production:
```bash
cat .env.production
```

## Para ver los logs si algo sale mal:
```bash
docker compose logs web --tail=20
```