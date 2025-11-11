# 🚀 Acceso Rápido - Sistema de Certificados DRTC

## 🌐 URLs de Acceso

```
🔒 HTTPS (Principal):  https://localhost:7443
🔓 HTTP (Redirige):    http://localhost:7070

👤 Admin:              https://localhost:7443/admin/
📊 Dashboard:          https://localhost:7443/dashboard/
🔍 Consulta:           https://localhost:7443/consulta/
```

## 🔑 Credenciales

```
Usuario:  admin
Email:    admin@drtc.gob.pe
Password: Ver logs de inicio o ejecutar:
          docker exec certificados_web_prod python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='admin'); print(f'Password configurado: {u.has_usable_password()}')"
```

## ⚡ Comandos Rápidos

### Ver Estado
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Ver Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f web
```

### Reiniciar
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Detener
```bash
docker-compose -f docker-compose.prod.yml down
```

### Iniciar
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔍 Verificar Servicios

### PostgreSQL
```bash
docker exec certificados_db_prod pg_isready -U certificados_user
```

### Redis
```bash
docker exec certificados_redis_prod redis-cli ping
```

### Django
```bash
docker exec certificados_web_prod python manage.py check
```

### Nginx
```bash
docker exec certificados_nginx_prod nginx -t
```

## 📝 Notas Importantes

1. **Certificado SSL:** Es autofirmado, acepta la advertencia del navegador
2. **Primera vez:** Puede tardar unos segundos en cargar
3. **Logs:** Si hay problemas, revisa los logs con el comando arriba
4. **Puertos:** 7070 (HTTP) y 7443 (HTTPS)

## ✅ Checklist de Verificación

- [ ] Abrir navegador
- [ ] Ir a https://localhost:7443
- [ ] Aceptar certificado autofirmado
- [ ] Ver página de inicio
- [ ] Acceder a /admin/
- [ ] Login con credenciales
- [ ] Verificar dashboard
- [ ] Probar consulta de certificados

## 🆘 Troubleshooting

### No carga la página
```bash
# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart
```

### Error de certificado
- Es normal, el certificado es autofirmado
- Click en "Avanzado" → "Continuar de todos modos"

### Servicios no responden
```bash
# Verificar estado
docker-compose -f docker-compose.prod.yml ps

# Reiniciar todo
docker-compose -f docker-compose.prod.yml restart
```

---

**¡Listo para usar!** 🎉
