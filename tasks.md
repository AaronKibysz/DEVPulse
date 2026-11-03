# Tareas — DevPulse

## Fase 0

- [x] Inspeccionar el directorio y el repositorio.
- [x] Verificar el entorno de desarrollo.
- [x] Investigar la API real de OpenCode.
- [x] Documentar la disponibilidad de métricas.
- [x] Comparar tecnologías y aprobar stack.
- [x] Crear `docs/constitution.md`.
- [x] Crear `AGENTS.md`.
- [x] Crear `MEMORY.md`.
- [x] Crear `README.md`.
- [x] Crear `docs/architecture.md`.
- [x] Crear `docs/roadmap.md`.
- [x] Crear `docs/decisions/ADR-001-stack-python-pyside6.md`.
- [x] Crear `docs/specs/README.md`.
- [x] Crear `skills/spec-generator/SKILL.md`.
- [x] Crear `skills/spec-generator/spec-template.md`.
- [x] Generar `directory-tree.txt`.
- [x] Crear `docs/research/opencode-api-summary.md`.

## Fase 1

- [x] Definir la especificación funcional inicial para la integración con OpenCode.
- [x] Aprobar la especificación.
- [x] Diseñar el plan técnico.
- [x] Instalar y verificar PySide6.
- [x] Crear la estructura de código del proyecto.
- [x] Implementar configuración y almacenamiento local.
- [x] Crear modelos internos.
- [x] Establecer el sistema de registros.
- [x] Implementar prueba básica de importación.
- [x] Crear una ventana inicial funcional.

## Seguridad

- [x] Crear módulo de validación y sanitización.
- [x] Implementar gestión segura de credenciales.
- [x] Asegurar que los logs no contengan secretos.
- [x] Validar respuestas de la API de OpenCode.
- [x] Restringir conexiones a localhost.

## Fase 1 — Visualización avanzada

- [x] Crear Spec 002.
- [x] Implementar gráficos de tokens, contexto y tendencia temporal en memoria.
- [x] Implementar modo compacto con gráfico mínimo.
- [x] Añadir pruebas de historial y gráficos.

- [x] Crear modelos de dominio.
- [x] Crear interfaz de integración.
- [x] Implementar cliente de OpenCode.
- [x] Implementar mapeo de datos.
- [x] Crear servicio de monitorización.
- [x] Integrar actualización básica en la UI.
- [x] Añadir pruebas de mapeo y cliente.
- [x] Implementar configuración y almacenamiento local.
- [x] Implementar sistema de registros.
## Fase 1 — Fuente CLI e híbrida

- [x] Implementar proveedor CLI de OpenCode.
- [x] Implementar modo auto (HTTP con fallback a CLI).
- [x] Ocultar consolas de subprocesos en Windows.
- [x] Añadir gráfico de torta con porcentaje numérico.

## Fase 1 � UX y empaquetado

- [x] Implementar modo compacto/expandido.
- [x] Implementar bandeja del sistema.
- [x] Crear spec y script de empaquetado con PyInstaller.
- [x] Implementar tema clásico/neon configurable.
- [x] Rediseñar la interfaz con cards y jerarquía visual.
- [x] Añadir animaciones sutiles y accesibilidad básica.

## Fase 1 — Formato discreto (Spec 003)

- [x] Crear Spec 003 y aprobarla.
- [x] Crear plan técnico Spec 003.
- [x] Implementar ventana sin marco y siempre encima.
- [x] Implementar arrastre restringido al área visible.
- [x] Reducir tamaño por defecto a 260x190 en modo compacto.
- [x] Mover configuración a diálogo accesible desde control discreto.
- [x] Revelar/ocultar controles al pasar el mouse.
- [x] Minimizar a bandeja al cerrar.
- [x] Modernizar gráfico circular con glow y animación.
- [x] Corregir export CLI y habilitar contexto/porcentaje en modo CLI.
- [x] Simplificar Context Trend (tiempo relativo) y añadir uso del servicio (tokens/costo).
- [x] Mejorar visualización de Context Trend (área, marcadores, leyenda).
- [x] Añadir gráfico de tokens (input/output, por muestra/acumulado).
- [x] Añadir botón opcional a OpenCode Console (sin credenciales).
- [x] Verificar pruebas y ejecución.

## Trabajo futuro

- [ ] Integrar cuota restante y fecha de reseteo si la API o la consola web lo exponen.
- [ ] Definir mecanismo seguro para almacenar credenciales de OpenCode Console (cifrado).
- [ ] Evaluar automatización segura del acceso a la consola (scraping) con consentimiento explícito.
- [ ] Mostrar cantidad de prompts usados cuando se decida incluirla.
- [ ] Evaluar QtCharts si pyqtgraph/Painter resultan insuficientes.

## Fase 2 - Rediseño integral (en progreso)

- [x] Instalar QtAwesome y añadir a pyproject.toml.
- [x] Centralizar paleta en theme.py (COLORS).
- [x] Actualizar QSS global.
- [x] Crear SectionHeader, MetricCard.
- [x] Crear ContextProgress.
- [x] Crear QuotaCard.
- [x] Crear ContextSummary.
- [x] Crear ContextChart.
- [x] Integrar en MainWindow.

- [x] Etapa 3 completa: estado de conexion, iconos en tarjetas, top bar.
- [x] Etapa 4 completa: widget compacto.
- [x] Etapa 5 completa: dialogo de config con iconos, boton Console (opcional) conectado, tray icon con QtAwesome, alias usage_page_button.
- [x] Etapa 6: validacion y tests (40 passed, 1 skipped); correccion de _apply_glow_effects (AttributeError).
- [x] Ajustes visuales iterativos: modo compacto sin superposicion, modo extendido restaurado con scroll, paleta nueva, traducciones, optimizaciones.
