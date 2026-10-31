# SQLite local con Docker Compose y DataGrip

Fecha de consulta y comprobación: 2026-09-24

## Qué se está ejecutando

El archivo [`docker-compose.yml`](../../docker-compose.yml) usa `alpine/sqlite:latest`. El servicio `sqlite` mantiene visible un contenedor de herramientas, pero SQLite sigue siendo una base embebida: los datos viven en `.data/estadistica-dev.db` y no existe un servidor ni un puerto de base de datos.

El directorio local `.data/` se monta como `/data` dentro del contenedor. Las migraciones de `migrations/` se montan como solo lectura en `/migrations`.

## Arrancar y detener

Desde la raíz de `estadistica-forms-api`:

```bash
# Descargar la versión más reciente de la etiqueta latest
docker compose pull sqlite

# Arrancar el contenedor en segundo plano
docker compose up --detach sqlite

# Verificar que está running/healthy
docker compose ps

# Detenerlo sin borrar la base
docker compose stop sqlite

# Retirar el contenedor y la red; el archivo .data/estadistica-dev.db permanece
docker compose down
```

## Aplicar migraciones

```bash
docker compose run --rm migrate
```

El comando:

1. crea `schema_migrations` si no existe;
2. lee en orden los archivos `migrations/NNN_nombre.sql`;
3. omite los que ya están registrados;
4. aplica cada migración pendiente dentro de una transacción;
5. registra la versión aplicada.

Para migrar otro archivo dentro de `.data/`:

```bash
docker compose run --rm \
  -e SQLITE_DATABASE=/data/otra-base.db \
  migrate
```

## Abrir la consola SQLite

Con el contenedor arrancado:

```bash
docker compose exec sqlite sqlite3 /data/estadistica-dev.db
```

Comandos útiles dentro de la consola:

```sql
.tables
.schema app_users
.schema statistical_spaces
SELECT * FROM schema_migrations ORDER BY version;
PRAGMA foreign_key_check;
.quit
```

También se puede ejecutar una consulta sin abrir la consola interactiva:

```bash
docker compose exec sqlite \
  sqlite3 /data/estadistica-dev.db \
  "SELECT version FROM schema_migrations ORDER BY version;"
```

## Conexión local creada en DataGrip

Proyecto de DataGrip:

```text
/Users/benji/DataGripProjects/Estadistica-proyect-db
```

Fuente de datos:

```text
Nombre: Estadistica Local SQLite
DBMS: SQLite
JDBC URL: jdbc:sqlite:/Users/benji/Documents/NEST+ASTRO/estadistica-forms-api/.data/estadistica-dev.db
```

DataGrip abre directamente el archivo del host. No debe configurarse `localhost`, un puerto, usuario ni contraseña. La prueba automática terminó sin problemas usando SQLite JDBC 3.51.1.0.

## Comprobación realizada

- `alpine/sqlite:latest` resolvió SQLite 3.53.4 al comprobar esta configuración.
- El contenedor `sqlite` puede mantenerse en ejecución sin levantar Nest.
- El migrador reconoció las tres migraciones existentes.
- Una base temporal nueva recibió `001`, `002` y `003` y expuso `app_users`, `schema_migrations` y `statistical_spaces`.
- La conexión `Estadistica Local SQLite` respondió correctamente desde DataGrip.

## Fuentes

- [Imagen `alpine/sqlite` en Docker Hub](https://hub.docker.com/r/alpine/sqlite)
- [SQLite: cuándo usar SQLite](https://www.sqlite.org/whentouse.html)
- [JetBrains: DataGrip MCP Server](https://www.jetbrains.com/help/datagrip/mcp-server.html)
