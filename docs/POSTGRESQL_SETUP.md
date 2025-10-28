# Configuración de PostgreSQL

## Instalación de PostgreSQL

### Windows

1. Descargar PostgreSQL desde: https://www.postgresql.org/download/windows/
2. Ejecutar el instalador y seguir las instrucciones
3. Recordar la contraseña del usuario `postgres`

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### macOS

```bash
brew install postgresql
brew services start postgresql
```

## Crear la Base de Datos

1. Conectarse a PostgreSQL:
```bash
psql -U postgres
```

2. Crear la base de datos:
```sql
CREATE DATABASE certificados_drtc;
```

3. Crear un usuario (opcional):
```sql
CREATE USER drtc_user WITH PASSWORD 'tu_contraseña';
GRANT ALL PRIVILEGES ON DATABASE certificados_drtc TO drtc_user;
```

4. Salir de psql:
```sql
\q
```

## Configurar Django para usar PostgreSQL

### Instalar psycopg2

#### En Linux/macOS:
```bash
pip install psycopg2-binary
```

#### En Windows:

Si tienes problemas instalando psycopg2-binary, tienes dos opciones:

**Opción 1: Instalar Visual C++ Build Tools**
1. Descargar desde: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Instalar "Desktop development with C++"
3. Ejecutar: `pip install psycopg2-binary`

**Opción 2: Usar un wheel precompilado**
1. Descargar el wheel apropiado desde: https://www.lfd.uci.edu/~gohlke/pythonlibs/#psycopg
2. Instalar: `pip install psycopg2‑2.9.9‑cp313‑cp313‑win_amd64.whl`

### Actualizar configuración

1. Editar `config/settings/development.py`
2. Descomentar la configuración de PostgreSQL
3. Comentar la configuración de SQLite
4. Actualizar el archivo `.env` con las credenciales correctas:

```env
DB_NAME=certificados_drtc
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
```

### Ejecutar migraciones

```bash
python manage.py migrate
```

## Verificar la conexión

```bash
python manage.py dbshell
```

Si se conecta correctamente, verás el prompt de PostgreSQL.

## Troubleshooting

### Error: "role does not exist"
Asegúrate de que el usuario especificado en `.env` existe en PostgreSQL.

### Error: "database does not exist"
Crea la base de datos usando los comandos SQL anteriores.

### Error: "password authentication failed"
Verifica que la contraseña en `.env` sea correcta.

### Error: "could not connect to server"
Asegúrate de que PostgreSQL esté ejecutándose:
- Windows: Verifica en Servicios
- Linux: `sudo systemctl status postgresql`
- macOS: `brew services list`
