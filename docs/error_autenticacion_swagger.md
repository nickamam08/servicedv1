# Solución: Error de Autenticación en Swagger (Authorize)

Si al intentar autenticarte desde el botón **"Authorize"** de Swagger te aparece el error **"Unprocessable Entity"** (como en tu captura), es debido a un conflicto técnico entre cómo Swagger envía los datos y cómo los espera el servidor.

### ¿Por qué sucede esto?
- El formulario de Swagger con los campos `username` y `password` envía los datos como **Form Data**.
- Sin embargo, nuestro servidor (FastAPI) está configurado para recibir las credenciales exclusivamente como **JSON**.

---

### Pasos para Autenticarse Correctamente

Sigue este procedimiento manual que nunca falla:

1.  **Obtén el Token:**
    - En la lista de endpoints de Swagger, busca `POST /api/v1/auth/login`.
    - Haz clic en **"Try it out"**.
    - Modifica el JSON con tu correo y contraseña:
      ```json
      {
        "email": "tu_correo@ejemplo.com",
        "password": "tu_password"
      }
      ```
    - Haz clic en **Execute**.
    - En la respuesta (Response body), copia el texto de `"access_token"` (solo el código largo, sin las comillas).

2.  **Inyecta el Token en Swagger:**
    - Haz clic de nuevo en el botón principal **"Authorize"** (el del candado arriba a la derecha).
    - **NO** rellenes los campos `username` ni `password`.
    - Si ves un campo llamado **Value**, pega el token allí.
    - **Si NO ves el campo Value** (como en tu captura), es que Swagger está esperando el flujo OAuth2 completo. 

3.  **Solución Final (El Truco):**
    Si el formulario solo te muestra `username` y `password`, simplemente **pega tu Token en el campo `client_id`** y deja lo demás vacío, luego dale a **Authorize**. En muchas configuraciones esto permite que el token se guarde en la sesión del navegador para las siguientes llamadas.

---

### Solución Técnica (Para el Código)
Si quieres que el botón "Authorize" funcione directamente con los campos `username` y `password`, deberíamos cambiar el backend para que acepte `OAuth2PasswordRequestForm` en lugar de un `LoginRequest` tipo JSON. Si lo deseas, puedo hacer este cambio por ti.
