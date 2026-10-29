# ADR-001 — Stack principal: Python + PySide6

## Estado

Aprobado.

## Contexto

DevPulse necesita una interfaz ligera de escritorio, compatible con Windows, con soporte para ventanas flotantes, bandeja del sistema, transparencia y actualizaciones locales eficientes.

Alternativas consideradas:

- Python + PySide6.
- Electron + React + TypeScript.
- Tauri + tecnologías web.

## Decisión

Utilizar Python + PySide6 para la primera versión.

## Justificación

- Menor consumo de recursos que Electron para un widget de monitorización.
- Buen soporte para ventanas flotantes, siempre visible, bandeja del sistema, transparencia y atajos.
- Empaquetado viable con PyInstaller y un instalador para Windows.
- Facilita la integración local con procesos, SQLite y la API HTTP de OpenCode.
- Permite desarrollar en macOS y compilar/probar en Windows mediante CI.
- Tauri queda descartado por ahora por falta de toolchain Rust y mayor complejidad inicial.

## Consecuencias

- PySide6 deberá instalarse y verificarse antes de iniciar la Fase 1.
- El empaquetado para Windows deberá probarse en un entorno Windows o CI.
- La UI no tendrá la misma flexibilidad que una aplicación web, pero se considera suficiente para un widget minimalista.
