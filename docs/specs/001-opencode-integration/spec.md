# Spec 001 — Integración con OpenCode y métricas básicas

## Estado

Aprobada.

## Contexto y objetivo

Permitir que DevPulse detecte instancias de OpenCode, consulte sesiones y muestre métricas básicas de forma fiable, sin modificar datos de OpenCode.

## Usuarios / actores

Usuario que utiliza OpenCode Desktop o CLI y desea monitorizar su uso desde un widget.

## Historias de usuario

- H1: Como usuario, quiero ver la sesión activa y su proyecto para saber en qué contexto estoy trabajando.
- H2: Como usuario, quiero ver el modelo utilizado y el consumo de tokens para controlar el uso.
- H3: Como usuario, quiero distinguir datos disponibles de datos no disponibles para no confundir métricas.

## Requisitos funcionales

- RF-1: [Ubicuo] EL SISTEMA mostrará la instancia de OpenCode detectada cuando exista una disponible.
- RF-2: [Evento] CUANDO existan varias instancias, EL SISTEMA permitirá seleccionar una manualmente.
- RF-3: [Ubicuo] EL SISTEMA mostrará la sesión activa cuando pueda identificarla.
- RF-4: [Evento] CUANDO existan varias sesiones, EL SISTEMA permitirá seleccionar una manualmente.
- RF-5: [Ubicuo] EL SISTEMA mostrará el modelo y proveedor de la sesión seleccionada cuando estén disponibles.
- RF-6: [Ubicuo] EL SISTEMA mostrará tokens de entrada, salida y caché cuando estén disponibles.
- RF-7: [Ubicuo] EL SISTEMA mostrará el contexto utilizado, la capacidad del modelo y el porcentaje cuando puedan calcularse.
- RF-8: [Ubicuo] EL SISTEMA mostrará el costo reportado cuando esté disponible.
- RF-9: [Evento] CUANDO OpenCode no esté disponible, EL SISTEMA conservará las últimas estadísticas conocidas y las marcará como históricas.
- RF-10: [Error] SI una métrica no está disponible, ENTONCES EL SISTEMA mostrará un estado apropiado sin provocar errores.

## Requisitos no funcionales

- RNF-1: La interfaz no se bloqueará durante las consultas.
- RNF-2: Las consultas se realizarán de forma eficiente, evitando procesos redundantes.
- RNF-3: La integración no modificará datos de OpenCode.

## Casos límite

- OpenCode cerrado.
- Varias instancias simultáneas.
- Sesión sin mensajes.
- Modelo sin límite de contexto informado.
- Costo reportado igual a cero.
- Datos incompletos o versión incompatible.

## Fuera de alcance

- Modificación de sesiones.
- Alertas de consumo.
- Gráficos históricos.
- Integraciones con otras herramientas.
- Recomendaciones inteligentes.

## Criterios de finalización

- Existe una integración funcional con OpenCode.
- Se pueden consultar instancias, sesiones y métricas básicas.
- Las métricas no disponibles se representan correctamente.
- Las pruebas pertinentes se ejecutan y documentan.

## Dependencias y referencias

- `docs/constitution.md`
- `docs/architecture.md`
- `docs/research/opencode-api-summary.md`
