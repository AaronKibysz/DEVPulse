# Tareas — Spec 003: Formato discreto, tamaño reducido y gráficos modernos

## Documentación

- [ ] Crear `docs/specs/003-formato-discreto-widget/spec.md`.
- [ ] Crear `docs/plans/003-formato-discreto-widget-technical-plan.md`.
- [ ] Actualizar `docs/specs/README.md` con el estado de Spec 003.
- [ ] Actualizar `tasks.md` y `MEMORY.md`.

## Implementación

- [ ] Configurar ventana principal sin marco estándar y siempre encima.
- [ ] Implementar arrastre de la ventana desde su superficie.
- [ ] Restringir el movimiento al área visible de la pantalla.
- [ ] Reducir tamaño por defecto del modo compacto a 260x190.
- [ ] Ocultar pestaña de configuración; mover configuración a vista separada accesible desde control discreto.
- [ ] Revelar/ocultar controles al pasar el cursor (hover).
- [ ] Minimizar a bandeja del sistema al cerrar cuando esté disponible.
- [ ] Restaurar posición y tamaño entre ejecuciones.
- [ ] Modernizar `PieChartWidget` con gradientes, glow y porcentaje.
- [ ] Añadir animaciones sutiles a los gráficos al cambiar datos.
- [ ] Aplicar estilo neon/glow coherente en gráficos según tema activo.
- [ ] Asegurar legibilidad de valores numéricos en ambos temas.

## Pruebas

- [ ] Añadir/actualizar pruebas de configuración de ventana (frameless, tamaño, posición).
- [ ] Añadir/actualizar pruebas de hover/revelado de controles.
- [ ] Añadir/actualizar pruebas de minimización a bandeja.
- [ ] Añadir/actualizar pruebas de gráficos (colores, animación no bloqueante).
- [ ] Ejecutar `python -m pytest` y verificar que todas pasen.

## Validación

- [ ] Ejecutar la aplicación y verificar visualmente el formato discreto.
- [ ] Verificar que no salga del área visible al arrastrar.
- [ ] Verificar hover, minimización a bandeja y restauración de posición.
- [ ] Verificar gráficos neon/glow y animaciones.
