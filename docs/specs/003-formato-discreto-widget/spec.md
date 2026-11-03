# Spec 003 — Formato discreto, tamaño reducido y gráficos modernos del widget

## Estado

Aprobada.

## Contexto y objetivo

El widget actual se presenta como una ventana estándar con barra de título, pestañas y un tamaño relativamente grande. Los gráficos se ven convencionales. Se busca un formato más discreto, tipo widget flotante, de menor tamaño, con gráficos de estilo neon/glow y animaciones sutiles al cambiar los datos, sin interferir con el flujo de trabajo ni añadir dependencias injustificadas.

## Usuarios / actores

Usuario de DevPulse que monitoriza OpenCode mientras trabaja.

## Historias de usuario

- H1: Como usuario, quiero que el widget ocupe poco espacio y sea discreto, para no distraerme mientras programo.
- H2: Como usuario, quiero mover el widget libremente por la pantalla (sin salir del área visible), para colocarlo donde no moleste.
- H3: Como usuario, quiero acceder a la configuración y a los controles sin que ocupen espacio permanente, revelándose al pasar el mouse.
- H4: Como usuario, quiero que los gráficos tengan un estilo neon/glow y se animen al cambiar los datos, para que se vean más vivos y modernos.

## Requisitos funcionales

### Ventana y disposición

- RF-1: [Ubicuo] EL SISTEMA presentará la ventana principal sin la barra de título ni los bordes estándar del sistema operativo.
- RF-2: [Ubicuo] EL SISTEMA permitirá al usuario mover la ventana arrastrándola desde su superficie.
- RF-3: [Ubicuo] EL SISTEMA impedirá que la ventana se mueva fuera del área visible de la pantalla durante el arrastre.
- RF-4: [Estado] MIENTRAS el modo compacto esté activo, EL SISTEMA mostrará únicamente un indicador de estado de conexión y el porcentaje de contexto utilizado en un gráfico circular, con un tamaño por defecto de 260x190 píxeles.
- RF-5: [Estado] MIENTRAS el modo expandido esté activo, EL SISTEMA mostrará la información detallada disponible (sesiones, tokens, contexto, costo, gráficos).
- RF-6: [Ubicuo] EL SISTEMA mantendrá la ventana por encima de otras ventanas en todo momento.
- RF-7: [Evento] CUANDO el usuario solicite la configuración, EL SISTEMA la presentará en una vista separada (diálogo o ventana independiente) accesible desde un control discreto (botón o menú contextual), sin pestaña permanente en la ventana principal.
- RF-8: [Evento] CUANDO la ventana principal se cierre y la bandeja del sistema esté disponible, EL SISTEMA la ocultará en la bandeja en lugar de finalizar la aplicación.
- RF-9: [Ubicuo] EL SISTEMA conservará la posición y el tamaño de la ventana entre ejecuciones.
- RF-10: [Ubicuo] EL SISTEMA mantendrá los controles (refrescar, modo, configuración, selección de sesión) ocultos por defecto y los revelará al pasar el cursor sobre el widget.

### Gráficos

- RF-11: [Ubicuo] EL SISTEMA presentará los gráficos con un estilo visual coherente con el tema activo (clásico o neon), incluyendo glow y gradientes en el tema neon.
- RF-12: [Evento] CUANDO los datos de un gráfico cambien, EL SISTEMA animará la transición de forma sutil y no bloqueante.
- RF-13: [Ubicuo] EL SISTEMA mantendrá legibles los valores numéricos (porcentajes, tokens) sobre los gráficos en ambos temas.

## Requisitos no funcionales

- RNF-1: El modo compacto no superará 260x190 píxeles en su tamaño por defecto.
- RNF-2: Las transiciones entre modo compacto y expandido, y las animaciones de gráficos, no bloquearán la interfaz.
- RNF-3: La información mostrada en modo compacto será legible en el tamaño indicado.
- RNF-4: La mejora de gráficos priorizará las librerías ya instaladas; toda dependencia nueva deberá justificarse técnica y documentalmente antes de su adopción.

## Casos límite

- Ventana arrastrada contra los bordes de la pantalla: se detiene en el límite visible.
- Bandeja del sistema no disponible: el cierre finaliza la aplicación.
- Sin datos de contexto: mostrar estado de no disponible en el gráfico circular.
- Múltiples monitores: la restricción de área visible se aplica al monitor en que se encuentra la ventana.
- Datos que cambian muy rápido: las animaciones no deben acumularse ni bloquear.
- Tema clásico: los gráficos deben verse correctos sin glow.
- Cursor fuera del widget: los controles vuelven a ocultarse.

## Fuera de alcance

- Transparencia/opacity configurable.
- Redimensionado libre por el usuario.
- Temas nuevos o cambios de color más allá de los existentes (clásico/neon).
- Cambios en las métricas o fuentes de datos.
- Empaquetado/instalador.
- Adopción de nuevas librerías de gráficos sin justificación previa.

## Criterios de finalización

- La ventana principal se muestra sin marco estándar y es arrastrable, sin salir del área visible.
- El modo compacto ocupa como máximo 260x190 por defecto y muestra solo estado y porcentaje de contexto.
- La configuración se accede desde un control discreto revelado al hover, no desde una pestaña permanente.
- La ventana permanece por encima de otras.
- Posición y tamaño se restauran entre ejecuciones.
- Los controles se revelan al pasar el mouse y se ocultan al salir.
- Los gráficos presentan estilo neon/glow en tema neon y animaciones sutiles al cambiar datos.
- El cierre minimiza a bandeja cuando está disponible.
- Pruebas automatizadas actualizadas y pasando.
- Documentación actualizada.

## Dependencias y referencias

Spec de integración con OpenCode, spec de visualización avanzada, constitución del proyecto.

## Dudas abiertas

- [NECESITA ACLARACIÓN: ¿la prioridad de librerías actuales es suficiente, o se debe evaluar QtCharts si el resultado no convence?]
