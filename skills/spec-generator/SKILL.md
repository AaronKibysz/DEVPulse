# Spec Generator Skill — DevPulse

Esta skill se activa cuando el usuario solicita crear, redactar, definir, aclarar o revisar una especificación funcional de DevPulse.

## Propósito

Convertir ideas vagas en requisitos verificables y acordados antes de diseñar o implementar una solución.

Las especificaciones deben describir el comportamiento esperado de DevPulse, sus condiciones y sus resultados observables, sin prescribir innecesariamente la implementación técnica.

## Proceso de creación

1. **Leer el contexto:** consultar `docs/constitution.md`, `AGENTS.md`, `MEMORY.md`, las especificaciones relacionadas y las decisiones documentadas que correspondan.
2. **Identificar decisiones sin resolver:** detectar dudas que puedan afectar el comportamiento, el alcance, los casos límite o los criterios de aceptación.
3. **Entrevistar al usuario:** formular una pregunta por vez y esperar la respuesta antes de continuar. Limitar la entrevista a seis preguntas, salvo que el usuario solicite continuar.
4. **Priorizar preguntas:** centrarse en decisiones funcionales relevantes. No preguntar por cuestiones ya resueltas ni por detalles que puedan resolverse con valores predeterminados seguros y compatibles con las decisiones aprobadas.
5. **No proponer soluciones técnicas:** preguntar qué debe hacer el sistema y por qué, no qué clases, bibliotecas, archivos o algoritmos utilizar.
6. **Asignar identificador:** utilizar el siguiente número libre de tres dígitos para generar identificadores como `Spec 001`, `Spec 002` y `Spec 003`. Revisar los archivos existentes para evitar duplicados.
7. **Redactar la especificación:** utilizar la plantilla `skills/spec-generator/spec-template.md`.
8. **Marcar dudas abiertas:** utilizar el formato `[NECESITA ACLARACIÓN: pregunta concreta]` cuando una cuestión relevante siga sin resolverse.
9. **Presentar y solicitar aprobación:** mostrar al usuario la especificación completa y esperar su aprobación explícita antes de considerarla aprobada.
10. **No implementar:** no generar el plan de implementación ni escribir código para la funcionalidad hasta recibir la aprobación explícita de la especificación.

La aprobación de una especificación no implica automáticamente la autorización para realizar acciones externas, operaciones destructivas o cambios de alcance no acordados.

## Revisión de especificaciones existentes

Cuando el usuario solicite revisar una especificación, presentar los hallazgos en cuatro bloques:

1. Ambigüedades.
2. Contradicciones entre requisitos.
3. Casos límite no cubiertos.
4. Conflictos con la constitución del proyecto.

No modificar la especificación ni proponer correcciones hasta que el usuario las solicite.

Si se detecta un conflicto con una decisión técnica documentada, distinguir entre un conflicto funcional y una cuestión de implementación. No convertir automáticamente una preferencia técnica en un requisito funcional.

## Reglas de redacción

- La especificación describe qué debe hacer el sistema y por qué, no cómo implementarlo.
- No incluir clases, nombres de archivos de implementación, arquitectura, esquemas de datos, algoritmos ni firmas de funciones.
- Incluir siempre una sección «Fuera de alcance».
- Cada requisito debe describir un comportamiento verificable.
- Separar los comportamientos independientes en requisitos distintos.
- Evitar adjetivos no medibles, como «rápido», «intuitivo» o «robusto», salvo que se definan mediante criterios verificables.
- Utilizar notación EARS para los criterios de aceptación.
- Numerar los requisitos funcionales como `RF-1`, `RF-2`, etc.
- Numerar los requisitos no funcionales como `RNF-1`, `RNF-2`, etc.
- Mantener el idioma indicado por la constitución: español para las especificaciones y documentación funcional; inglés para el código y los identificadores técnicos.
- No inventar decisiones, límites, cifras ni requisitos para completar la plantilla.
- No confundir una propuesta, una duda abierta y un requisito aprobado.
- No duplicar requisitos que ya estén definidos en especificaciones aplicables. Cuando corresponda, referenciarlos.
- Mantener las especificaciones acotadas a una funcionalidad coherente y evitar agrupar funcionalidades independientes en un único documento.

## Patrones EARS

| Patrón | Forma |
|---|---|
| Ubicuo | EL SISTEMA hará... |
| Evento | CUANDO ocurra X, EL SISTEMA hará Y. |
| Estado | MIENTRAS se cumpla X, EL SISTEMA hará Y. |
| Opcional | DONDE exista X, EL SISTEMA hará Y. |
| Error | SI se cumple X, ENTONCES EL SISTEMA hará Y. |

No forzar los cinco patrones si alguno no corresponde a la funcionalidad.

## Consideraciones específicas de DevPulse

Las especificaciones relacionadas con la monitorización de OpenCode deben contemplar, cuando corresponda:

- Qué información debe ver el usuario.
- En qué condiciones se considera que existe una sesión activa.
- Cómo se comporta el sistema cuando hay varias instancias o sesiones.
- Qué ocurre cuando OpenCode está cerrado.
- Cómo se comunica que una métrica no está disponible.
- Cómo se distingue la información real de los valores calculados o estimados.
- Qué ocurre ante errores de conexión, datos incompletos o versiones incompatibles.
- Qué información debe conservarse entre ejecuciones.
- Qué opciones de configuración debe poder controlar el usuario.
- Qué condiciones de privacidad y consentimiento afectan al comportamiento visible.
- Qué sucede cuando la fuente de información deja de responder.

Estas consideraciones son orientativas. Solo deben incorporarse a una especificación cuando sean relevantes para la funcionalidad concreta.

## Aprobación y persistencia

Antes de recibir aprobación explícita:

- Presentar la especificación completa al usuario.
- No marcarla como aprobada.
- No iniciar su implementación.
- No iniciar el desarrollo de tareas derivadas de ella.

Tras la aprobación:

- Guardar la especificación en `docs/specs/` con un nombre descriptivo y su identificador.
- Registrar su estado de aprobación.
- Actualizar los índices o referencias correspondientes.
- Permitir que el plan técnico la utilice como fuente autorizada.
