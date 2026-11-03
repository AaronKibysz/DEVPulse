# Spec 004 — Refinamiento visual y mejora de UI/UX

## Estado
Aprobada (documento proporcionado por el usuario).

## Contexto y objetivo
Segunda iteración de diseño para perfeccionar la interfaz existente, corregir inconsistencias visuales y mejorar la experiencia de usuario, sin reconstruir la aplicación ni modificar su arquitectura general.

Identidad visual: Dark Premium + minimalismo tecnológico. Tema oscuro, violeta como identidad, azul secundario, verde para estados positivos, iluminación sutil, tarjetas con profundidad moderada, bordes discretos, tipografía moderna, excelente legibilidad.

## Usuarios / actores
Usuario de DevPulse que monitoriza OpenCode mientras trabaja.

## Principios de diseño
1. La información tiene prioridad sobre los efectos visuales.
2. Los elementos importantes destacan por tamaño, jerarquía y contraste.
3. El violeta identifica la aplicación, no decora todo.
4. Sombras discretas.
5. Bordes ayudan a separar secciones sin llamar la atención.
6. Animaciones breves e imperceptibles.
7. Cada componente tiene función visual clara.
8. Evitar elementos innecesarios.

## Requisitos funcionales (resumen)
- Fondos opacos en áreas principales; transparencia solo como decisión de diseño.
- Paleta centralizada con los valores definidos.
- Tipografía Inter con fallback a Segoe UI.
- Indicador circular de contexto rediseñado con QPainter (anillo gris azulado, progreso violeta, gradiente discreto, extremos redondeados, animación suave).
- Información de contexto coherente (porcentaje utilizado vs disponible).
- Tarjeta de contexto: anillo a la izquierda, métricas a la derecha.
- Tarjeta de cuota: barra horizontal, porcentaje restante, renovación, estado, botón discreto.
- Gráfico de contexto con PyQtGraph integrado, selector temporal (1h/6h/24h/7d/30d), estado vacío en español.
- Tarjetas inferiores: Tokens (filas compactas), Sesión actual, Proyecto actual.
- Recomendaciones con icono, título, mensaje y severidad.
- Detalles técnicos con botón compacto y expansión.
- Barra superior rediseñada.
- Scrollbar discreta.
- Botones con estados unificados.
- Layout responsive.

## Requisitos no funcionales
- No migrar de framework.
- No introducir bibliotecas visuales adicionales sin justificación.
- No cambiar lógica de negocio para resolver problemas visuales, salvo corrección de etiqueta inconsistente.
- No introducir datos ficticios.
- Mantener rendimiento adecuado.

## Criterios de aceptación
Ver documento completo (sección 16). Incluye: sin superposiciones, sin franjas de transparencia no deseadas, anillo alineado, métricas coherentes, tarjetas uniformes, gráfico integrado, textos en español, rutas sin desbordamiento, scrollbar discreto, botones unificados, iluminación sutil, rendimiento adecuado, funcionalidades conservadas, app inicia sin errores.

## Dependencias y referencias
Constitución, Spec 001-003, arquitectura.