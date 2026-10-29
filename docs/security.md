# Seguridad y privacidad — DevPulse

## Principio general

DevPulse operará en modo solo lectura y con mínimo privilegio. No modificará datos de OpenCode ni ejecutará acciones de programación.

## Medidas de seguridad

### Conexión con OpenCode
- Conectar únicamente a `127.0.0.1` o `localhost`.
- Usar la autenticación existente de OpenCode cuando esté disponible.
- No desactivar mecanismos de autenticación.
- Verificar la versión de la API antes de usar endpoints.
- Degradar de forma segura si la API cambia.

### Credenciales
- No almacenar contraseñas ni tokens en texto plano.
- Usar el almacén seguro del sistema operativo si es necesario.
- No mostrar credenciales en la UI.
- No registrar secretos en logs.
- Permitir funcionamiento sin credenciales cuando la integración no las requiera.

### Validación de datos
- Validar estructura y tipos de las respuestas de OpenCode.
- Rechazar campos inesperados o malformados.
- No ejecutar código basado en datos recibidos.
- Sanitizar rutas e identificadores.

### Almacenamiento local
- Guardar solo métricas normalizadas.
- No guardar conversaciones, código fuente ni transcripciones.
- Usar SQLite con permisos adecuados.
- Separar preferencias de datos históricos.
- No duplicar la base de datos de OpenCode.

### Actualización y procesos
- Evitar múltiples procesos CLI simultáneos.
- Limitar la frecuencia de sondeo.
- Cerrar conexiones cuando no se necesiten.
- Manejar reconexiones de forma controlada.

### Interfaz
- No ejecutar comandos arbitrarios desde la UI.
- Validar configuraciones antes de aplicarlas.
- No permitir que datos de sesión influyan en rutas o comandos.
- Mantener la ventana de configuración separada del widget.

### Privacidad por defecto
- Sin telemetría.
- Sin sincronización en la nube en la primera versión.
- Sin envío de datos a servicios externos.
- Logs sin secretos, código ni transcripciones.

### Empaquetado e instalación
- Instalador con permisos mínimos.
- No modificar el sistema sin autorización.
- Desinstalación limpia sin borrar datos personales sin confirmación.

## Módulo de seguridad propuesto

Un componente `security` o `privacy` puede centralizar:

- Validación de entradas.
- Sanitización de rutas e identificadores.
- Gestión segura de credenciales.
- Control de permisos de archivos.
- Registro seguro.

## Relación con funcionalidades

| Funcionalidad | Riesgo principal | Medida |
|---|---|---|
| Detección de instancias | Conexión a endpoints incorrectos | Solo localhost y validación de origen |
| Consulta de sesiones | Exposición de datos sensibles | Solo métricas normalizadas |
| Tokens y contexto | Interpretación incorrecta | Distinguir oficial/calculado/estimación |
| Costos | Tarifas inventadas | Solo costo reportado o estimación documentada |
| Configuración | Credenciales en texto plano | Almacén seguro o sin credenciales |
| Historial | Almacenamiento excesivo | Solo métricas necesarias |
| UI | Ejecución de comandos | Solo lectura y validación |
