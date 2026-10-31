# Spec 002 — Visualización avanzada con historial temporal

## Estado

Aprobada.

## Contexto y objetivo

Mostrar de forma clara y profesional las métricas de la sesión seleccionada de OpenCode, incluyendo un historial temporal en memoria para observar tendencias recientes sin persistir datos sensibles.

## Usuarios / actores

Usuario que monitoriza una sesión de OpenCode desde el widget de DevPulse.

## Historias de usuario

- H1: Como usuario, quiero ver un gráfico de tokens de la sesión seleccionada para entender el consumo.
- H2: Como usuario, quiero ver el contexto usado y restante para controlar el límite de la sesión.
- H3: Como usuario, quiero ver una tendencia temporal reciente para detectar cambios de consumo.
- H4: Como usuario, quiero una vista compacta con información mínima y una vista expandida con gráficos detallados.

## Requisitos funcionales

- RF-1: [Ubicuo] EL SISTEMA mostrará un gráfico de barras con tokens de entrada, salida y caché de la sesión seleccionada cuando estén disponibles.
- RF-2: [Ubicuo] EL SISTEMA mostrará el contexto utilizado, la capacidad y el porcentaje de la sesión seleccionada cuando puedan calcularse.
- RF-3: [Ubicuo] EL SISTEMA mostrará el costo reportado de la sesión seleccionada cuando esté disponible.
- RF-4: [Evento] CUANDO se complete un refresh exitoso, EL SISTEMA añadirá una muestra temporal en memoria para la sesión seleccionada.
- RF-5: [Evento] CUANDO existan muestras temporales, EL SISTEMA mostrará una tendencia reciente de contexto o tokens.
- RF-6: [Estado] MIENTRAS el modo compacto esté activo, EL SISTEMA mostrará un gráfico o indicador mínimo de contexto.
- RF-7: [Estado] MIENTRAS el modo expandido esté activo, EL SISTEMA mostrará los gráficos detallados y la tendencia temporal.
- RF-8: [Evento] CUANDO cambie la sesión seleccionada, EL SISTEMA actualizará los gráficos con los datos y el historial de esa sesión.
- RF-9: [Error] SI una métrica no está disponible, ENTONCES EL SISTEMA mostrará un estado apropiado sin provocar errores.

## Requisitos no funcionales

- RNF-1: La interfaz no se bloqueará durante las actualizaciones.
- RNF-2: El historial temporal se mantendrá solo en memoria y se limitará a 50 muestras por sesión.
- RNF-3: No se inventarán métricas ni costos; solo se mostrarán datos oficiales o calculados.
- RNF-4: No se persistirán muestras temporales en SQLite en esta iteración.

## Casos límite

- Sesión sin mensajes.
- Modelo sin límite de contexto informado.
- Costo reportado igual a cero.
- Datos incompletos o versión incompatible.
- Cambio rápido de sesión.
- Refresh fallido: no se añade muestra.

## Fuera de alcance

- Gráficos históricos persistentes entre ejecuciones.
- Comparación entre varias sesiones.
- Alertas de consumo.
- Recomendaciones inteligentes.
- Integraciones con otras herramientas.

## Criterios de finalización

- Existe una visualización funcional para la sesión seleccionada.
- El historial temporal en memoria se actualiza en refresh exitosos.
- El modo compacto muestra un indicador mínimo.
- El modo expandido muestra gráficos detallados y tendencia.
- Las pruebas pertinentes se ejecutan y documentan.

## Dependencias y referencias

- `docs/constitution.md`
- `docs/specs/001-opencode-integration/spec.md`
- `docs/architecture.md`

## Dudas abiertas

No quedan dudas relevantes para esta iteración.