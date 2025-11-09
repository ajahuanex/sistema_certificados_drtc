# 🔑 Credenciales y Datos de Prueba

## Credenciales de Administrador

**Usuario**: `admin`  
**Contraseña**: `admin123`  
**Email**: admin@drtc.gob.pe

**URL de acceso**: 
- Desarrollo: http://127.0.0.1:8000/admin/ o http://127.0.0.1:8001/admin/
- Producción: https://tu-dominio.com/admin/

**Nota**: Si las credenciales no funcionan, ejecuta:
```bash
python manage.py create_superuser_if_not_exists --update --noinput
```

---

## 🌐 URLs del Sistema

### URLs Públicas
- **Página Principal**: http://127.0.0.1:8000/ (redirige a consulta)
- **Consulta de Certificados**: http://127.0.0.1:8000/consulta/
- **Verificar Certificado**: http://127.0.0.1:8000/verificar/{uuid}/
- **Descargar Certificado**: http://127.0.0.1:8000/certificado/{uuid}/descargar/

### URLs de Administración
- **Panel Admin**: http://127.0.0.1:8000/admin/
- **Dashboard**: http://127.0.0.1:8000/admin/dashboard/
- **Importar Excel**: http://127.0.0.1:8000/admin/import-excel/

---

## 📋 DNIs de Prueba para Consultas

### ✅ DNIs con Certificados PDF Reales (Recomendados para pruebas)

| DNI | Nombre | Evento | UUID |
|-----|--------|--------|------|
| **99238323** | Juan Morales Rodríguez | Curso de Inspección Vehicular | 9f446c3e-6acc-4ba9-a49d-8a998a331f89 |
| **88459901** | María Díaz Rodríguez | Curso de Inspección Vehicular | 424dbc11-df59-4a86-925e-b367bcbbeda2 |
| **71257548** | Carmen Gómez Jiménez | Curso de Inspección Vehicular | f11ba46c-b58a-4c6c-a2ef-310c057d9e6a |
| **81925349** | Lucía Navarro Serrano | Curso de Inspección Vehicular | ccff4c51-4be9-4202-92d5-acfac59d71c2 |
| **87140676** | Carlos Moreno Morales | Curso de Inspección Vehicular | e84fe5e8-14f3-4e15-a21e-a993d2104208 |
| **33292085** | Javier Muñoz Ortega | Curso de Inspección Vehicular | 9e335672-28dd-4f9a-80c9-acc85295bfa6 |
| **32731750** | Daniel Suárez Gil | Curso de Inspección Vehicular | 4e01cba5-cc32-422f-bd73-7071cacc4ec0 |

### DNIs de Participantes (Sin certificado aún)

| DNI | Nombre | Evento |
|-----|--------|--------|
| **20728647** | Luis Torres Morales | Capacitación en Primeros Auxilios |
| **66951204** | Carmen Alonso Torres | Capacitación en Primeros Auxilios |
| **68171699** | Alejandro Pérez Hernández | Capacitación en Primeros Auxilios |
| **73911498** | Patricia Blanco García | Capacitación en Primeros Auxilios |
| **69271021** | Jesús Serrano García | Capacitación en Primeros Auxilios |

---

## 🧪 Pruebas Recomendadas

### 1. Consulta de Certificados
1. Ve a: http://127.0.0.1:8000/consulta/
2. Ingresa uno de los DNIs con certificados (ej: **91397350**)
3. Deberías ver el certificado disponible para descargar

### 2. Verificación de Certificado
1. Usa uno de los UUIDs listados arriba
2. Ve a: http://127.0.0.1:8000/verificar/{uuid}/
3. Ejemplo: http://127.0.0.1:8000/verificar/49aea5e1-a35d-410d-be47-cb12d6c680b0/

### 3. Dashboard de Administración
1. Inicia sesión en: http://127.0.0.1:8000/admin/
2. Usuario: `admin` / Contraseña: `admin123`
3. Ve al dashboard: http://127.0.0.1:8000/admin/dashboard/
4. Explora las estadísticas y gráficos

### 4. Generar Certificados
1. Accede al admin
2. Ve a "Eventos"
3. Selecciona "Capacitación en Primeros Auxilios"
4. Usa la acción "Generar Certificados"
5. Los participantes sin certificado ahora tendrán uno

### 5. Importar Excel
1. Accede al admin
2. Ve a: http://127.0.0.1:8000/admin/import-excel/
3. Crea un archivo Excel con el formato especificado
4. Importa participantes

---

## 📊 Estadísticas del Sistema

- **Eventos**: 10
- **Participantes**: 198
- **Certificados Generados**: 147
- **Logs de Auditoría**: 500

---

## 🔧 Comandos Útiles

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Iniciar servidor
python manage.py runserver

# Crear superusuario adicional
python manage.py createsuperuser

# Generar más datos de prueba
python manage.py generate_sample_data

# Generar certificados para un evento
python manage.py generate_certificates --event-id 1

# Ver shell de Django
python manage.py shell

# Ejecutar tests
python manage.py test
```

---

## ⚠️ Notas Importantes

- **Entorno**: Desarrollo (DEBUG=True)
- **Base de datos**: SQLite (db.sqlite3)
- **Archivos media**: Se guardan en `media/`
- **Logs**: Se guardan en `logs/`

Para producción, recuerda:
- Cambiar `DEBUG=False`
- Usar PostgreSQL
- Configurar SECRET_KEY único
- Configurar ALLOWED_HOSTS
- Usar HTTPS
- Configurar servicio de firma digital real
