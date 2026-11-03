# Plan técnico — Spec 003: Formato discreto, tamaño reducido y gráficos modernos

## 1. Objetivo

Transformar la ventana principal en un widget flotante discreto (sin marco, siempre encima, arrastrable, restringido al área visible), con controles revelados al pasar el mouse, configuración en vista separada, minimización a bandeja al cerrar, y gráficos con estilo neon/glow y animaciones sutiles, priorizando las librerías ya instaladas.

## 2. Componentes afectados

- `src/devpulse/ui/main_window.py`: ventana principal, arrastre, hover, bandeja, tamaño.
- `src/devpulse/ui/pie_chart.py`: gráfico circular moderno con glow y animación.
- `src/devpulse/ui/charts.py`: helpers para animación de gráficos.
- `src/devpulse/ui/theme.py`: estilos y glow (reutilizar).
- `src/devpulse/config/settings.py`: defaults de tamaño compacto 260x190.
- `src/devpulse/application/config_service.py`: sin cambios funcionales (reutilizar).

## 3. Cambios por archivo

### `settings.py`
- `window_width` default 260, `window_height` default 190 (modo compacto por defecto).

### `main_window.py`
- Establecer `Qt.FramelessWindowHint` y `Qt.WindowStaysOnTopHint`.
- Implementar arrastre con `mousePressEvent`/`mouseMoveEvent`/`mouseReleaseEvent`, clamping al área de pantalla.
- Quitar pestañas; usar un layout compacto con controles ocultos por defecto.
- Añadir botón/menú discreto para abrir configuración en `QDialog` (o ventana independiente).
- Ocultar controles por defecto; mostrar al `enterEvent`, ocultar al `leaveEvent` (con pequeño retardo opcional).
- Minimizar a bandeja en `closeEvent` si bandeja disponible.
- Mantener `_apply_mode`, animación de tamaño.
- Actualizar gráficos al cambiar datos con animación (QPropertyAnimation o QTimer).

### `pie_chart.py`
- Añadir gradientes radiales, glow en neon, animación de entrada (valor animado).
- Mantener porcentaje numérico centrado.

### `charts.py`
- Añadir helper para animar valores (opcional, puede vivir en widget).

## 4. Flujo de arrastre

1. `mousePressEvent`: registrar posición inicial y offset.
2. `mouseMoveEvent`: calcular nueva posición, clamp a `QApplication.primaryScreen().availableGeometry()`, mover.
3. `mouseReleaseEvent`: limpiar estado.

## 5. Configuración separada

- Crear `ConfigDialog` (QDialog) con los controles actuales de la pestaña Configuration.
- Botón de engranaje/menú contextual para abrirlo.
- Al guardar, aplicar tema y refrescar.

## 6. Pruebas

- Unitarias: clamping de posición, tamaño por defecto, hover muestra/oculta controles.
- Integración UI: marcadas, pueden requerir entorno gráfico.

## 7. Riesgos

- Ventana frameless puede ser difícil de mover en algunos sistemas; mitigar con área de arrastre clara.
- Animaciones pueden acumularse; usar una sola animación activa por widget.
- Bandeja no disponible: cerrar normalmente.
- Qt Charts no se adopta inicialmente; reevaluar si pyqtgraph/Painter resultan insuficientes.
