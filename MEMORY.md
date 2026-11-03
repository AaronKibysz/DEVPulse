# MEMORY.md — DevPulse

## Decisiones vigentes
- Widget de escritorio para monitorizar OpenCode Desktop y CLI.
- Windows primero; arquitectura ampliable.
- Stack aprobado: Python + PySide6.
- Métricas solo si son fiables; distinguir oficial/calculado/estimación/no disponible.
- API HTTP oficial de OpenCode como fuente principal.
- Sin cuentas, nube ni sincronización en v1.

## Estado actual
Fase 1 avanzada. Validación real con OpenCode ejecutada correctamente. Visualización avanzada, fuente CLI, tema neon/clásico, rediseño de interfaz, animaciones sutiles, accesibilidad básica, formato discreto (Spec 003), contexto en CLI y uso del servicio implementados. 31 pruebas pasando, 1 omitida.

## Logros verificados
- Entorno inspeccionado.
- PySide6 instalado y verificado.
- Esqueleto mínimo de aplicación creado.
- Ventana inicial funcional verificada.
- Prueba básica pasando.
- API de OpenCode v2.1.2 verificada.
- Disponibilidad de métricas documentada.
- Stack aprobado y documentado.
- Visualización avanzada con historial temporal en memoria.
- Tema neon/clásico configurable con glow, tipografía y accesibilidad básica.
- Rediseño profundo de la interfaz con cards y animaciones sutiles.
- Formato discreto: ventana sin marco, siempre encima, arrastrable, restricción al área visible, controles por hover, minimización a bandeja.
- Gráfico circular modernizado con glow y animación.
- Context Trend simplificado con tiempo relativo.
- Uso del servicio (tokens/costo) y botón opcional a OpenCode Console.
- Contexto en modo CLI: export corregido a `session export`, resolución de límites de modelo vía `opencode api`, cálculo de porcentaje cuando es posible.

## Próximos pasos
1. Validar la integración real en Windows.
2. Probar modo compacto/expandido y bandeja del sistema.
3. Evaluar empaquetado con PyInstaller.
4. Diseñar mecanismo seguro para credenciales de OpenCode Console.
5. Investigar cuota restante/reset (API o consola web).

## Archivos clave
- `AGENTS.md`
- `docs/constitution.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `tasks.md`

## Problemas conocidos
- OpenCode Desktop no disponible en este entorno.
- Cuota restante no disponible en la API observada.
- Detección de múltiples instancias no verificada.

## Última actualización
2026-11-03: iteraciones visuales finalizadas; modo compacto sin superposicion, modo extendido restaurado con scroll, paleta nueva, traducciones, optimizaciones; pruebas 40 passed, 1 skipped.

## Rediseño integral (Etapa 1-2 parcial)

- QtAwesome instalado. Paleta centralizada en theme.py (COLORS).
- Componentes: SectionHeader, MetricCard, ContextProgress, QuotaCard, ContextSummary, ContextChart.
- MainWindow: context_ring=ContextProgress, context_summary, quota_card=QuotaCard, trend_chart=ContextChart.
- Data-binding actualizado. Tests: 40 passed, 1 skipped.

## Rediseño completo (Etapa 3-6)

- Estado de conexion con icono y color.
- Tarjetas secundarias con iconos QtAwesome.
- Top bar con iconos.
- Config dialog con iconos en botones.
- Boton Console (opcional) conectado a _open_console.
- Tray icon con QtAwesome.
- Correccion de _apply_glow_effects (referencias inexistentes).
- Tests: 40 passed, 1 skipped. App sin errores (temas clasico y neon verificados).
