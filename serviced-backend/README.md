# Serviced Backend API

## Requisitos previos

- Python 3.9+ installed
- PostgreSQL installed and running locally
- Virtual Environment (recommended)

## Configuración inicial

1.  **Variable de entorno**:
    Asegúrate de que el archivo `.env` exista y tenga las credenciales correctas de tu base de datos local:

    ```ini
    DB_USER=postgres
    DB_PASSWORD=admin
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=serviced_db
    ```

2.  **Instalar dependencias**:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Inicializar Base de Datos**:
    Ejecuta el script para crear las tablas e insertar datos de prueba:
    ```bash
    python init_db.py
    ```

## Ejecución del Servidor

Para iniciar la API en modo de desarrollo (con recarga automática):

```bash
uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000`.
La documentación interactiva (Swagger UI) está en `http://localhost:8000/docs`.

## Pruebas

Para verificar que la API funciona correctamente, puedes ejecutar el script de prueba:

```bash
python test_api.py
```
