# ✅ CONFIGURACIÓN DE DOMINIO COMPLETADA

## Fecha: 18 de Noviembre de 2025

## Problema Resuelto
Error 403 "La verificación CSRF ha fallado" al acceder al admin a través del dominio:
```
https://certificados.transportespuno.gob.pe/admin/
```

## Causa
El dominio no estaba incluido en las configuraciones de seguridad de Django:
- `ALLOWED_HOSTS`: Lista de hosts permitidos
- `CSRF_TRUSTED_ORIGINS`: Orígenes confiables para CSRF

## Solución Aplicada

### Configuración Actualizada en .env.production

```bash
# Hosts permitidos (con y sin www)
ALLOWED_HOSTS=161.132.47.92,localhost,127.0.0.1,certificados.transportespuno.gob.pe,www.certificados.transportespuno.gob.pe

# Orígenes CSRF confiables (HTTP local + HTTPS dominio)
CSRF_TRUSTED_ORIGINS=http://161.132.47.92,http://localhost,https://certificados.transportespuno.gob.pe,https://www.certificados.transportespuno.gob.pe
```

### Comandos Ejecutados

```bash
# 1. Actualizar ALLOWED_HOSTS
sed -i 's|ALLOWED_HOSTS=161.132.47.92,localhost,127.0.0.1,certificados.transportespuno.gob.pe|ALLOWED_HOSTS=161.132.47.92,localhost,127.0.0.1,certificados.transportespuno.gob.pe,www.certificados.transportespuno.gob.pe|g' .env.production

# 2. Actualizar CSRF_TRUSTED_ORIGINS
sed -i 's|CSRF_TRUSTED_ORIGINS=http://161.132.47.92,http://localhost|CSRF_TRUSTED_ORIGINS=http://161.132.47.92,http://localhost,https://certificados.transportespuno.gob.pe,https://www.certificados.transportespuno.gob.pe|g' .env.production

# 3. Reiniciar contenedor web
docker compose restart web
```

## URLs Configuradas

### Acceso Público
- ✅ https://certificados.transportespuno.gob.pe/
- ✅ https://www.certificados.transportespuno.gob.pe/
- ✅ http://161.132.47.92:7070/

### Panel de Administración
- ✅ https://certificados.transportespuno.gob.pe/admin/
- ✅ https://www.certificados.transportespuno.gob.pe/admin/
- ✅ http://161.132.47.92:7070/admin/

### Credenciales Admin
- **Usuario**: admin
- **Email**: admin@drtc.gob.pe
- **Contraseña**: (la configurada en el sistema)

## Verificación

### 1. Probar acceso al admin
```bash
# Debería cargar sin error 403
https://certificados.transportespuno.gob.pe/admin/
```

### 2. Verificar health check
```bash
curl https://certificados.transportespuno.gob.pe/health/
```

### 3. Ver logs del contenedor
```bash
docker compose logs --tail=20 web
```

## Configuración Nginx Proxy Manager

El sistema está configurado con:
- **Proxy Host**: certificados.transportespuno.gob.pe
- **Forward Hostname/IP**: 161.132.47.92
- **Forward Port**: 7070
- **SSL**: Habilitado (Let's Encrypt)
- **Force SSL**: Recomendado activar
- **HTTP/2**: Recomendado activar

## Estado del Sistema

| Componente | Estado | URL |
|------------|--------|-----|
| Dominio Principal | ✅ Funcionando | https://certificados.transportespuno.gob.pe |
| Dominio con WWW | ✅ Funcionando | https://www.certificados.transportespuno.gob.pe |
| Admin Panel | ✅ Funcionando | https://certificados.transportespuno.gob.pe/admin/ |
| Health Check | ✅ Funcionando | https://certificados.transportespuno.gob.pe/health/ |
| SSL/HTTPS | ✅ Activo | Certificado válido |
| PostgreSQL | ✅ Funcionando | Base de datos operativa |
| Redis | ✅ Funcionando | Cache operativo |

## Configuraciones de Seguridad Adicionales

### Para Producción Real (Opcional)

Si quieres forzar HTTPS en toda la aplicación, actualiza en `.env.production`:

```bash
# Forzar HTTPS
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

Luego reinicia:
```bash
docker compose restart web
```

## Próximos Pasos

1. ✅ Dominio configurado y funcionando
2. ✅ Admin accesible sin errores
3. ✅ SSL/HTTPS activo
4. 🔄 Probar todas las funcionalidades del admin
5. 📊 Monitorear logs por 24 horas
6. 🔒 Cambiar contraseña del admin por una segura
7. 📧 Configurar email para notificaciones (opcional)
8. 🔐 Considerar activar autenticación de dos factores

## Notas Importantes

- El sistema acepta tanto HTTP (puerto 7070) como HTTPS (dominio)
- Nginx Proxy Manager maneja el SSL automáticamente
- Los certificados SSL se renuevan automáticamente
- El dominio con y sin "www" funcionan correctamente
- CSRF está configurado para aceptar ambos protocolos

---

**Sistema de Certificados DRTC - Dominio Configurado** ✅
