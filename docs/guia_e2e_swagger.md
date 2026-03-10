# Guía de Pruebas End-to-End (E2E) con Swagger UI
Esta guía te llevará paso a paso para probar el flujo completo de creación de un servicio utilizando la documentación interactiva de la API.

---

## Paso 1: Acceder a Swagger UI
1. Asegúrate de que el servidor backend esté corriendo (por defecto en `http://localhost:8000`).
2. Abre tu navegador y dirígete a: `http://localhost:8000/docs`.
   *   *Verás todos los endpoints organizados por módulos (Auth, Services, Users, etc.).*

## Paso 2: Autenticación (Obtener el Token)
Dado que la creación de servicios requiere ser un proveedor autenticado, primero debemos obtener un token de acceso.

1. Busca la sección **Auth** y el endpoint `POST /api/v1/auth/login`.
2. Haz clic en **"Try it out"**.
3. En el cuerpo (Request body), ingresa las credenciales de una cuenta de **Proveedor**:
   ```json
   {
     "email": "tu_correo@ejemplo.com",
     "password": "TuPassword123!"
   }
   ```
4. Haz clic en **Execute**.
5. En la respuesta (Response body), copia el valor de `"access_token"` (sin las comillas).

## Paso 3: Autorizar en Swagger
1. Sube al inicio de la página y busca el botón **"Authorize"** (con un candado).
2. En el campo **Value**, pega el token que copiaste.
3. Haz clic en **Authorize** y luego en **Close**.
   *   *Ahora Swagger incluirá automáticamente el encabezado `Authorization: Bearer <token>` en tus peticiones.*

## Paso 4: Crear el Servicio
1. Busca la sección **Services** y el endpoint `POST /api/v1/services/`.
2. Haz clic en **"Try it out"**.
3. Completa el cuerpo del mensaje con los datos del servicio que quieres crear:
   ```json
   {
     "title": "Limpieza Profunda de Interiores",
     "description": "Servicio profesional de limpieza para hogares y oficinas con equipos de alta gama.",
     "price": 85000,
     "category": "Limpieza",
     "image_urls": [
       "https://images.unsplash.com/photo-1581578731522-a2046a66ec07"
     ]
   }
   ```
4. Haz clic en **Execute**.

## Paso 5: Verificar Resultados
*   **Código 201 (Created) o 200:** Significa que el servicio se creó con éxito. Se te devolverá el objeto del servicio con su nuevo **ID**.
*   **Código 401/403:** Revisa si el token expiró o si el usuario no tiene rol de `provider`.
*   **Verificación en DB:** Puedes ir al endpoint `GET /api/v1/services/` y ejecutarlo para ver si tu nuevo servicio aparece en la lista global.

---
**Tip Pro:** Si necesitas probar la subida de imágenes real, usa el endpoint `POST /api/v1/services/upload-image` que permite cargar archivos binarios y te devuelve la URL para usarla en el paso de creación.
