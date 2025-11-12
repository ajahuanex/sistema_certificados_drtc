# 🚀 Instrucciones Simples

## 📍 Ahora (En Windows)

### Ejecuta esto:

```cmd
subir-a-github.bat
```

Esto subirá todos los cambios a GitHub.

---

## 🐧 Después (En Ubuntu)

### Conéctate a tu servidor:

```bash
ssh usuario@tu-servidor
```

### Ve al directorio del proyecto:

```bash
cd /ruta/al/proyecto
```

### Ejecuta estos 3 comandos:

```bash
git pull origin main
chmod +x deploy-ubuntu.sh
./deploy-ubuntu.sh
```

---

## ✅ Verificar

```bash
docker compose -f docker-compose.prod.yml ps
```

Todos los servicios deben estar "Up".

---

## 🌐 Acceder

Abre en tu navegador:
- http://TU_IP_SERVIDOR/
- http://TU_IP_SERVIDOR/admin/

---

## 📚 Más Información

- **Windows:** `PROCESO_COMPLETO.md`
- **Ubuntu:** `EJECUTA_EN_UBUNTU.md`

---

**¡Eso es todo! 🎉**
