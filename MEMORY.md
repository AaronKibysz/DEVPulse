# MEMORY.md — DevPulse

## Decisiones vigentes
- Widget de escritorio para monitorizar OpenCode Desktop y CLI.
- Windows primero; arquitectura ampliable.
- Stack aprobado: Python + PySide6.
- Métricas solo si son fiables; distinguir oficial/calculado/estimación/no disponible.
- API HTTP oficial de OpenCode como fuente principal.
- Sin cuentas, nube ni sincronización en v1.

## Estado actual
Fase 1 avanzada. Validación real con OpenCode ejecutada correctamente. 10 pruebas pasando, 1 omitida.

## Logros verificados
- Entorno inspeccionado.
- PySide6 instalado y verificado.
- Esqueleto mínimo de aplicación creado.
- Ventana inicial funcional verificada.
- Prueba básica pasando.
- API de OpenCode v2.1.2 verificada.
- Disponibilidad de métricas documentada.
- Stack aprobado y documentado.

## Próximos pasos
1. Validar la integración real en Windows.
2. Implementar modo compacto/expandido y bandeja del sistema.
3. Evaluar empaquetado con PyInstaller.

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
2026-10-30: documentación alineada con el código existente y pruebas verificadas.
