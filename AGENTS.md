# AGENTS.md — DevPulse

Guía operativa para agentes de programación que trabajen en este repositorio. Debe leerse antes de comenzar cualquier tarea y mantenerse actualizada después de cambios significativos.

## Instrucciones de Git

- No ejecutar `git add`, `git commit`, `git push`, `git pull` ni `git merge` durante las tareas de implementación ordinarias.
- Las operaciones de Git se realizarán al final de una sesión de trabajo, después de revisar los archivos modificados y obtener la confirmación del usuario.
- No modificar el historial de Git.
- No descartar cambios del usuario.
- No sobrescribir archivos existentes sin inspeccionarlos.
- Al terminar, informar de los cambios y dejar que el usuario decida si desea ejecutar operaciones de Git.

## Proyecto

Ver `README.md` para la descripción del proyecto y objetivos.

Stack principal aprobado para la primera versión: Python + PySide6. Arquitectura y decisiones en `docs/architecture.md`.

## Estructura del proyecto

La estructura definitiva se documentará a medida que se cree. No describir directorios previstos como si ya existieran.

Estado actual: el repositorio contiene la documentación inicial, la constitución, el sistema de especificaciones, el sistema de trabajo y un esqueleto mínimo de aplicación con pruebas básicas.

## Estilo

- Código e identificadores en inglés.
- Documentación del proyecto en español.
- Nombres descriptivos.
- Tipado adecuado.
- Manejo explícito de errores.
- Separación de responsabilidades.
- Pruebas automatizadas.
- Dependencias justificadas.
- Configuración externa al código cuando corresponda.

## Reglas de trabajo

- Leer `README.md`, `MEMORY.md` y `docs/constitution.md` antes de tareas relevantes, si existen.
- Consultar la especificación activa y el plan técnico cuando existan.
- No modificar funcionalidades fuera del alcance aprobado.
- No modificar decisiones arquitectónicas importantes sin explicar su impacto.
- No agregar dependencias innecesarias.
- No inventar métricas ni datos.
- No presentar estimaciones como datos oficiales.
- No afirmar que una prueba se ejecutó si no se ejecutó.
- No modificar ni eliminar datos de OpenCode.
- No recopilar código fuente o transcripciones innecesariamente.
- No almacenar credenciales en texto plano.
- No agregar integraciones sin verificar sus interfaces.
- No realizar operaciones Git sin la autorización correspondiente.
- Trabajar únicamente sobre el alcance de la tarea asignada.

## Trabajo con especificaciones

- Utilizar `skills/spec-generator/SKILL.md` como guía para crear o revisar especificaciones funcionales.
- Toda funcionalidad nueva debe pasar por especificación, aprobación, plan, implementación, pruebas y revisión.
- Las especificaciones se guardan en `docs/specs/` con un identificador numérico de tres dígitos.
- No implementar una funcionalidad sin especificación aprobada.

## Subagentes y coordinación

OpenCode proporciona los subagentes `explore` y `general`. No existen subagentes personalizados invocables denominados `plan`, `agent` o `test`.

Las responsabilidades `plan`, `agent` y `test` se documentan como roles de trabajo y se ejecutan mediante instrucciones especializadas y los subagentes disponibles, sin afirmar capacidades que el entorno no proporcione.

## Validación

Los comandos reales de instalación, desarrollo, pruebas y compilación se documentarán cuando exista el proyecto ejecutable.

No registrar comandos como verificados hasta haberlos ejecutado.

Comando verificado: `python -m pytest` (10 pruebas pasando, 1 omitida).

## Al terminar cualquier tarea

1. Ejecutar las pruebas pertinentes.
2. Revisar los archivos modificados y el diff.
3. Comprobar el cumplimiento de la especificación y la constitución.
4. Actualizar `tasks.md` y `MEMORY.md` cuando corresponda.
5. Actualizar `README.md` y `AGENTS.md` si cambió información que estos documenten.
6. Informar de los cambios, las pruebas ejecutadas, los resultados y los problemas pendientes.


## Desarrollo eficiente con agentes

Para reducir el consumo de tokens y mantener el contexto limpio:

- Usar el subagente `explore` para búsquedas acotadas.
- Usar `grep` y `glob` antes de leer archivos completos.
- Evitar pegar salidas largas; resumir resultados.
- Mantener `MEMORY.md` breve y actualizado.
- Usar referencias en lugar de duplicar contenido.
- Guardar planes largos en archivos de plan.
- Leer solo los archivos necesarios para la tarea actual.
- Usar nombres de archivo y rutas exactas.
- No repetir instrucciones ya presentes en este archivo.
- Dividir el trabajo en tareas pequeñas y verificables.
