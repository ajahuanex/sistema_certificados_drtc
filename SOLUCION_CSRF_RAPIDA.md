# 🔧 SOLUCIÓN RÁPIDA - ERROR 403 CSRF

## Problema Detectado
Error 403: "La verificación CSRF ha fallado. Solicitud abortada."

## Causa
Falta agregar el dominio HTTP (sin HTTPS) en `CSRF_TRUSTED_ORIGINS`

## Solución Inmediata

### Opción 1: Script Automático (Recomendado)
```cmd
actualizar-csrf-produccion.bat
```

### Opción 2: Manual (Conectarse al servidor)

1. **Conectar al servidor:**
```bash
ssh administrador@161.132.47.92
```

2. **Ir al directorio:**
```bash
cd dockers/sistema_certificados_drtc
```

3. **Editar el archivo .env.production:**
```bash
nano .env.production
```

4. **Buscar la línea CSRF_TRUSTED_ORIGINS y cambiarla por:**
```
CSRF_TRUSTED_ORIGINS=http://localhost:7070,http://127.0.0.1:7070,http://161.132.47.92:7070,http://certificados.transportespuno.gob.pe,http://www.certificados.transportespuno.gob.pe,https://certificados.transportespuno.gob.pe,https://www.certificados.transportespuno.gob.pe
```

5. **Guardar (Ctrl+O, Enter, Ctrl+X)**

6. **Reiniciar contenedores:**
```bash
docker compose down
docker compose up -d
```

7. **Verificar logs:**
```bash
docker compose logs -f web
```

## Verificación

Después de aplicar la solución, prueba:

1. Ve a: http://certificados.transportespuno.gob.pe/consulta/
2. Ingresa un DNI de prueba
3. Haz clic en "Consultar"
4. Ya NO debería aparecer el error 403

## ¿Por qué pasó esto?

El dominio `certificados.transportespuno.gob.pe` está configurado en el proxy reverso pero:
- El proxy usa HTTP (puerto 80) para comunicarse con el contenedor
- Django necesita que el origen HTTP esté en la lista de orígenes confiables
- Solo teníamos HTTPS en la lista, no HTTP

## Próximos Pasos

Una vez solucionado el CSRF:
1. ✅ Verificar que las consultas funcionen
2. ✅ Probar descargas de certificados
3. ✅ Verificar el admin
4. 🔒 Configurar SSL/HTTPS (opcional, para mayor seguridad)
