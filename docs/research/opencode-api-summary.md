# Resumen de API de OpenCode

Fuente: instancia local verificada de OpenCode v2.1.2.

## Endpoints usados

- `GET /api/info`
- `GET /api/session/active`
- `GET /api/session`
- `GET /api/session/{id}`
- `GET /api/session/{id}/context`
- `GET /api/session/{id}/message`
- `GET /api/model`
- `GET /api/project`
- `GET /api/experimental/session/stats`
- `GET /api/event`
- `GET /api/location`

## Campos clave

- Sesión: `id`, `projectID`, `agent`, `model`, `cost`, `tokens`, `time`, `title`, `location`.
- Tokens: `input`, `output`, `reasoning`, `cache.read`, `cache.write`.
- Modelo: `id`, `providerID`, `name`, `limit.context`, `limit.output`, `cost`, `status`.
- Sesión activa: mapa `ses_* -> { type: "running" }`.

## Limitaciones

- La cuota restante del servicio no está disponible.
- El contexto actual debe calcularse desde mensajes.
- La detección de múltiples instancias no se ha verificado completamente.
- La API puede cambiar entre versiones.
