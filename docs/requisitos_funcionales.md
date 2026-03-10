# Documento de Requisitos Funcionales - SERVICED

Este documento detalla las funcionalidades principales del sistema **SERVICED**, una plataforma para conectar clientes con profesionales expertos.

---

## 1. Módulo Público y Registro

### RF-01: Landing Page Informativa
El sistema debe contar con una página de inicio moderna y minimalista que presente los beneficios, categorías de servicios, cómo funciona la plataforma y testimonios de usuarios.

### RF-02: Registro de Usuarios
El sistema permitirá el registro de nuevos usuarios bajo dos roles principales:
- **Cliente**: Usuario que busca contratar servicios.
- **Profesional (Provider)**: Usuario que ofrece sus servicios y habilidades.

### RF-03: Validación de Seguridad en Registro
El sistema debe validar en tiempo real que la contraseña cumpla con estándares de seguridad:
- Mínimo 8 caracteres.
- Al menos una letra mayúscula y una minúscula.
- Al menos un número y un carácter especial.

### RF-04: Autenticación de Usuarios
El sistema debe permitir el inicio de sesión seguro y la recuperación de contraseña mediante correo electrónico.

---

## 2. Módulo del Cliente (User)

### RF-05: Dashboard de Cliente
Panel principal para visualizar el estado de sus solicitudes activas y servicios recientes.

### RF-06: Búsqueda de Servicios
Los clientes podrán buscar servicios por categorías (Hogar, IT, Diseño, etc.), filtrar por ubicación y ver detalles del profesional.

### RF-07: Gestión de Solicitudes
El cliente puede crear solicitudes de servicio, ver el historial de sus pedidos y cancelar solicitudes si es necesario.

### RF-08: Sistema de Chat Real-Time
Comunicación directa y segura entre clientes y profesionales para acordar detalles del servicio.

### RF-09: Valoraciones y Calificaciones
Posibilidad de calificar y dejar reseñas sobre el servicio recibido para generar confianza en la comunidad.

---

## 3. Módulo del Profesional (Provider)

### RF-10: Dashboard de Profesional
Visualización de métricas clave como ingresos totales, servicios pendientes, calificación promedio y próximos trabajos.

### RF-11: Gestión de Servicios Propios
El profesional puede crear, editar y eliminar los servicios que ofrece en la plataforma.

### RF-12: Gestión de Solicitudes Entrantes
Recibir y gestionar solicitudes de clientes, permitiendo aceptarlas o rechazarlas.

### RF-13: Estadísticas e Informes
Generación de reportes de ganancias y estadísticas de desempeño laboral.

---

## 4. Módulo Administrativo (Admin)

### RF-14: Gestión Global de Usuarios
Control total sobre las cuentas de clientes y profesionales (activación, desactivación y eliminación).

### RF-15: Gestión de Categorías
Creación y administración de las categorías de servicios disponibles en la plataforma.

### RF-16: Auditoría de Servicios y Solicitudes
Supervisar todos los servicios ofrecidos y las solicitudes realizadas para garantizar la calidad y seguridad.

### RF-27: Reportes Avanzados
Generación de informes detallados sobre el crecimiento de la plataforma, transacciones y métricas de uso generales.

---

## 5. Requisitos Transversales

### RF-18: Sistema de Notificaciones
Notificaciones en tiempo real (vía interfaz y sonido) para alertas de nuevos mensajes, cambios en el estado de servicios y recordatorios.

### RF-19: Interfaz Responsiva (Mobile-First)
Toda la plataforma debe ser completamente accesible y funcional desde dispositivos móviles, tablets y ordenadores.
