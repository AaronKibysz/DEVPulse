# Plan técnico — Spec 001: Integración con OpenCode y métricas básicas

## 1. Objetivo
Implementar la detección de instancias, consulta de sesiones y métricas básicas usando la API HTTP oficial de OpenCode, sin bloquear la UI ni modificar datos externos.

## 2. Componentes
- `OpenCodeClient`: comunicación HTTP local.
- `OpenCodeIntegration`: descubrimiento y normalización.
- `MonitorService`: coordinación de instancias, sesiones, activos y contexto.
- `RefreshWorker`: ejecución en segundo plano.
- `MainWindow`: presentación, selección y estados.
- `SnapshotRepository`: persistencia de últimas estadísticas.

## 3. Flujo de actualización
1. `MainWindow._refresh()` valida retry policy y crea `RefreshWorker`.
2. El worker detecta instancias y selecciona la instancia guardada o la primera disponible.
3. Consulta sesiones, identifica activas y calcula contexto por sesión.
4. Emite `(instances, sessions, selected_instance_id, error)`.
5. La UI actualiza estado, lista, combo, detalles, caché y persistencia.
6. En error, conserva datos históricos y aplica backoff.

## 4. Manejo de errores
- Sin instancia: se trata como error recuperable y se conserva caché.
- Error HTTP/red: se muestra mensaje, se marca histórico y se reduce frecuencia.
- Error de autenticación: se solicita contraseña una sola vez.
- Métrica no disponible: se representa como `unavailable` sin fallar.

## 5. Persistencia
- Guardar sesiones exitosas con `is_historical=False`.
- Marcar histórico al fallar.
- Restaurar últimas sesiones al iniciar.

## 6. Pruebas
- Unitarias: cliente, mapper, repositorio, configuración.
- Integración simulada: worker y monitor service con fakes.
- Integración real: marcada con `OPENCODE_INTEGRATION=1`.

## 7. Riesgos
- Cambios de API entre versiones de OpenCode.
- Detección de múltiples instancias no verificada.
- Contexto calculado, no métrica oficial.
- Cuota restante no disponible.
