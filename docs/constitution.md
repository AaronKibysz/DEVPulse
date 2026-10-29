# Constitución — DevPulse

Principios innegociables que toda especificación, plan y tarea del proyecto debe cumplir.

## 1. Simplicidad y complejidad justificada

Utilizar las tecnologías acordadas y evitar dependencias, abstracciones, servicios y capas innecesarias.

No introducir microservicios, contenedores, bases de datos remotas, sincronización en la nube ni backend propio para resolver problemas que puedan solucionarse localmente.

No agregar una dependencia sin justificar su necesidad técnica y su impacto en el rendimiento, el empaquetado y el mantenimiento.

## 2. La especificación aprobada es el contrato

Ningún comportamiento nuevo debe implementarse si no está contemplado en una especificación aprobada.

Si falta una decisión que pueda cambiar el comportamiento esperado, detener el trabajo y consultar al usuario. No convertir suposiciones en requisitos silenciosos.

Las especificaciones describen qué debe hacer el sistema y por qué. Los planes técnicos describen cómo implementarlo.

## 3. Separación de responsabilidades

La arquitectura debe distinguir, al menos conceptualmente:

- Interfaz gráfica.
- Lógica de aplicación.
- Dominio y modelos.
- Integraciones externas.
- Gestión de sesiones e instancias.
- Almacenamiento.
- Configuración.
- Registro de eventos y errores.
- Pruebas.

La lógica de negocio no debe depender de la interfaz gráfica. Las integraciones no deben modificar directamente los componentes visuales. Evitar dependencias circulares.

## 4. Pruebas como puerta de entrada

Cada tarea debe contar con las pruebas pertinentes a su alcance.

No declarar una tarea terminada si las pruebas relevantes fallan. No ocultar fallos ni desactivar pruebas para conseguir una ejecución satisfactoria.

Si no es posible ejecutar una prueba, documentar el motivo y distinguirlo de una prueba aprobada.

Utilizar `pytest` para las pruebas automatizadas de Python. Marcar claramente las pruebas que requieran una instalación real de OpenCode o conexión a Internet.

## 5. Integridad y procedencia de los datos

No inventar métricas, tokens, costos, cuotas ni estados.

Distinguir explícitamente entre:

1. Datos proporcionados directamente por OpenCode.
2. Datos calculados a partir de información verificable.
3. Estimaciones.
4. Datos no disponibles.

No presentar los tokens procesados acumulados como si fueran el contexto actual de la conversación.

No presentar la capacidad máxima teórica de un modelo como si fuera necesariamente el límite efectivo de una sesión.

No deducir la cuota restante de una suscripción a partir de los tokens de una sesión.

No calcular costos inventando tarifas. Si se implementa una estimación de costos, debe utilizar tarifas identificables, documentar sus supuestos y mostrar claramente que se trata de una estimación.

## 6. Seguridad y privacidad

La aplicación debe funcionar localmente y minimizar las comunicaciones externas.

Reglas obligatorias:

- No crear cuentas de usuario propias en la primera versión.
- No incorporar sincronización en la nube inicialmente.
- No enviar conversaciones ni código fuente a servicios externos.
- No solicitar credenciales de OpenCode sin una necesidad técnica justificada.
- No almacenar contraseñas ni tokens de acceso en texto plano.
- No imprimir secretos en registros.
- No exponer un servidor local a la red sin necesidad.
- No enlazar servicios locales a todas las interfaces de red por defecto.
- No desactivar mecanismos de autenticación existentes.
- No ejecutar comandos arbitrarios obtenidos de los datos de una sesión.
- No modificar ni eliminar datos de OpenCode.
- No ejecutar operaciones de programación en nombre del usuario.

La primera versión se limita a la monitorización.

Los registros de la aplicación no deben contener transcripciones, código fuente ni credenciales.

## 7. Documentación y decisiones

Toda decisión arquitectónica importante debe justificarse y documentarse.

Actualizar la documentación cuando una tarea cambie la arquitectura, las instrucciones de desarrollo, el modelo de datos o el comportamiento especificado.

Distinguir las decisiones confirmadas de las propuestas y las cuestiones pendientes.

## 8. Idioma y convenciones

- Código, identificadores, clases, métodos, variables y nombres de módulos en inglés.
- Documentación técnica, especificaciones y mensajes de usuario en español, salvo que exista una razón concreta para otro idioma.
- Tipado adecuado cuando el lenguaje lo permita.
- Nombres descriptivos y convenciones coherentes en todo el repositorio.

## 9. Cambios controlados

Trabajar únicamente sobre el alcance de la tarea asignada.

No eliminar archivos, sobrescribir datos, ejecutar operaciones destructivas ni introducir cambios de arquitectura no autorizados.

Antes de finalizar, revisar los cambios y comprobar que no se hayan incorporado funcionalidades fuera de la especificación activa.

## 10. Respeto a OpenCode

No modificar las sesiones ni ejecutar acciones de programación en nombre del usuario.

Si la aplicación necesita consultar información almacenada por OpenCode, investigar primero las interfaces soportadas. No asumir que leer directamente su base de datos es una integración estable.

La integración debe priorizar interfaces oficiales y documentadas.
