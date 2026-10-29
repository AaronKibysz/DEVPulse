# Especificaciones — DevPulse

## Organización

```
docs/specs/
├── README.md
└── NNN-nombre-funcionalidad/
    ├── spec.md
    └── tasks.md
```

## Convenciones

- Cada especificación utiliza un identificador numérico de tres dígitos: `001`, `002`, etc.
- Toda funcionalidad nueva debe tener una especificación aprobada antes de implementarse.
- Las especificaciones se redactan usando `skills/spec-generator/spec-template.md`.
- Los requisitos funcionales se numeran como `RF-1`, `RF-2`, etc.
- Los requisitos no funcionales se numeran como `RNF-1`, `RNF-2`, etc.
- Los criterios de aceptación utilizan notación EARS.
- Las dudas abiertas se marcan como `[NECESITA ACLARACIÓN: pregunta concreta]`.

## Flujo de trabajo

1. El usuario propone una funcionalidad.
2. Se crea una carpeta bajo `docs/specs/` con el siguiente número libre.
3. Se redacta `spec.md`.
4. Se revisa y aprueba la especificación.
5. Se genera `tasks.md`.
6. Se implementa tarea por tarea.
7. Se actualiza la documentación y `MEMORY.md`.

## Estado actual

No hay especificaciones aprobadas todavía.
