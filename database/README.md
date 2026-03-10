# Configuración de Base de Datos - SERVICED

Esta carpeta contiene todo lo necesario para inicializar la base de datos PostgreSQL del proyecto SERVICED.

## Contenido

- `schema.sql`: Crea las tablas `users`, `services` y `service_requests`.
- `seed.sql`: Inserta datos de prueba (usuarios, servicios, solicitudes).
- `connect.js`: Script de Node.js para probar la conexión.
- `.env.example`: Plantilla para tus credenciales.

## Pasos para la Configuración

### 1. Preparar PostgreSQL
Asegúrate de tener PostgreSQL instalado y en ejecución.
Crea una base de datos vacía llamada `serviced_db` (o el nombre que prefieras).

```sql
CREATE DATABASE serviced_db;
```

### 2. Ejecutar Scripts SQL
Ejecuta el script de esquema y luego el de datos. Puedes hacerlo desde la línea de comandos o usando una herramienta visual (pgAdmin, DBeaver).

**Línea de comandos:**
```bash
psql -U postgres -d serviced_db -f schema.sql
psql -U postgres -d serviced_db -f seed.sql
```

### 3. Configurar Conexión (Node.js)
Este proyecto incluye un script de prueba para verificar que tu aplicación pueda conectarse a la base de datos.

1.  Abre una terminal en esta carpeta (`database`).
2.  Instala las dependencias:
    ```bash
    npm install
    ```
3.  Crea un archivo `.env` basado en el ejemplo:
    ```bash
    cp .env.example .env
    ```
    *(O simplemente crea un archivo llamado `.env` y copia el contenido)*
4.  Edita el archivo `.env` y pon **tu contraseña real** de PostgreSQL.

### 4. Probar Conexión
Ejecuta el script de prueba:

```bash
npm run test-connection
```

Si todo está bien, verás un mensaje verde: `✅ ¡Conexión exitosa!` y la lista de tablas creadas.
