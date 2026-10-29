# Arquitectura — DevPulse

## Visión general

DevPulse será una aplicación de escritorio local construida con Python y PySide6. Su núcleo será independiente de la interfaz gráfica y estará organizado por capas para facilitar pruebas, mantenimiento y la incorporación futura de otras herramientas de programación con IA.

## Capas

1. **Interfaz gráfica (PySide6)**
   - Widget compacto.
   - Modo expandido.
   - Ventana de configuración.
   - Bandeja del sistema.
   - Estados visuales.

2. **Lógica de aplicación**
   - Coordinación de actualizaciones.
   - Selección de instancia y sesión.
   - Gestión del estado de conexión.
   - Reglas de actualización adaptativa.

3. **Dominio y modelos**
   - Entidades normalizadas: `Instance`, `Session`, `Model`, `TokenUsage`, `ContextMetrics`, `Cost`, `DataSource`.
   - Reglas de negocio independientes de la UI.

4. **Integraciones externas**
   - Interfaz común `IntegrationProvider`.
   - Implementación inicial `OpenCodeIntegration`.
   - Descubrimiento de instancias.
   - Consulta de sesiones, modelos, métricas y eventos.

5. **Almacenamiento**
   - SQLite para historial y últimas estadísticas conocidas.
   - Archivos locales para preferencias.

6. **Configuración**
   - Preferencias visuales y de comportamiento.
   - Posición y tamaño del widget.
   - Instancia y sesión seleccionadas.

7. **Registro**
   - Logging estructurado.
   - Sin secretos, transcripciones ni código fuente.

8. **Pruebas**
   - Pruebas unitarias de dominio, normalización y cálculos.
   - Pruebas de integración con respuestas simuladas.
   - Pruebas de integración real marcadas explícitamente.

## Integración con OpenCode

La integración inicial utilizará la API HTTP oficial de OpenCode como fuente principal, complementada por la CLI y los eventos SSE cuando aporten valor.

Fuentes verificadas: ver `docs/research/opencode-api-summary.md`.

La integración no modificará sesiones ni ejecutará acciones de programación.

## Modelo de datos normalizado

Conceptos principales:

- **Instance:** identificador, origen, estado de conexión, última actualización.
- **Session:** identificador, proyecto, modelo, tokens, costo, tiempos, estado activo/inactivo.
- **Model:** identificador, proveedor, capacidades, límite de contexto, costo por token.
- **TokenUsage:** entrada, salida, razonamiento, caché leída, caché escrita.
- **ContextMetrics:** contexto utilizado, capacidad, restante, porcentaje, procedencia.
- **Cost:** costo reportado y, si corresponde, estimación claramente marcada.
- **DataSource:** tipo de dato (oficial, calculado, estimación, no disponible).

## Actualización adaptativa

1. Suscripción a eventos SSE cuando esté disponible y sea fiable.
2. Sondeo eficiente como respaldo.
3. Reducción de frecuencia cuando no haya actividad.
4. Manejo de errores temporales sin bloquear la interfaz.

## Seguridad y privacidad

Ver `docs/security.md` para el plan completo.

- Comunicación local con la instancia de OpenCode.
- Sin cuentas propias ni sincronización en la nube en la primera versión.
- Sin envío de conversaciones ni código fuente a servicios externos.
- Sin almacenamiento de credenciales en texto plano.
- Sin modificación de datos de OpenCode.

## Riesgos técnicos

- Validación de OpenCode Desktop pendiente en Windows.
- Detección de múltiples instancias no verificada completamente.
- Posibles cambios de API entre versiones de OpenCode.
- El contexto actual debe calcularse, no leerse como métrica oficial.
- La cuota restante del servicio no está disponible en la API observada.
