# DevPulse

Widget de escritorio para monitorizar el uso de OpenCode Desktop y OpenCode CLI.

DevPulse muestra información relevante sobre sesiones, modelos, tokens, contexto y costos cuando los datos están disponibles, de forma discreta, configurable y segura.

## Estado actual del desarrollo

Proyecto en **Fase 1 avanzada**: existe un esqueleto mínimo de aplicación con PySide6, integración inicial con OpenCode, configuración, almacenamiento local y pruebas básicas.

No hay instalador ni ejecutable distribuible disponible todavía.

## Problema que resuelve

Durante el trabajo con asistentes de programación con IA es difícil mantener visibilidad sobre:

- La sesión activa y su proyecto.
- El modelo utilizado.
- El consumo de tokens.
- El contexto disponible y restante.
- El costo reportado.
- El estado de la conexión con la herramienta.

DevPulse busca proporcionar esa visibilidad sin interrumpir el flujo de trabajo ni modificar los datos de OpenCode.

## Objetivos

1. Crear una herramienta personal realmente útil.
2. Desarrollar un proyecto de portfolio profesional, mantenible y técnicamente sólido.
3. Establecer una base que permita distribuir públicamente la aplicación en el futuro.

## Funcionalidades previstas

- Detección de instancias compatibles de OpenCode.
- Listado y selección de sesiones.
- Identificación de la sesión activa.
- Visualización de métricas disponibles: modelo, tokens, contexto, costo.
- Distinción entre datos oficiales, calculados, estimados y no disponibles.
- Modo compacto y modo expandido.
- Ventana de configuración independiente.
- Actualización adaptativa con eventos o sondeo eficiente.
- Conservación de las últimas estadísticas conocidas cuando OpenCode no está disponible.
- Empaquetado para Windows.

## Funcionalidades implementadas

- Esqueleto mínimo de aplicación con PySide6.
- Ventana inicial funcional.
- Modelos de dominio básicos.
- Cliente de integración con OpenCode (lectura).
- Configuración y almacenamiento local (SQLite).
- Restauración de posición y tamaño.
- Conservación de datos históricos.
- Sistema de registros seguro.
- Actualización adaptativa básica.
- Fuente híbrida HTTP/CLI con fallback automático.
- Visualización avanzada con gráficos e historial temporal en memoria.
- Gráfico de torta con porcentaje numérico.
- Tema clásico/neon configurable con glow y tamaños de fuente.
- Rediseño de interfaz con cards, animaciones sutiles y accesibilidad básica.
- Pruebas básicas e integración marcada.

## Tecnologías seleccionadas

- **Lenguaje:** Python.
- **Interfaz gráfica:** PySide6.
- **Almacenamiento local:** SQLite para historial y datos persistentes; archivos locales para preferencias.
- **Integración con OpenCode:** API HTTP oficial, CLI y eventos cuando estén disponibles.
- **Pruebas:** pytest.

La decisión se documenta en `docs/decisions/ADR-001-stack-python-pyside6.md`.

## Requisitos del sistema

Pendiente de definir para la primera versión distribuible.

Entorno de desarrollo verificado:

- macOS 12.7.6.
- Python 3.13.9.
- OpenCode 2.1.2.

La plataforma objetivo inicial es Windows.

## Instalación

Pendiente. No hay instalador ni paquete disponible todavía.

## Configuración

Pendiente. La configuración se diseñará durante las fases posteriores.

## Uso

La aplicación puede ejecutarse desde el código fuente con las dependencias instaladas. Para ejecutar DevPulse sin consola:

```powershell
.\scripts\run_devpulse.ps1
```

Para monitorizar OpenCode en vivo, inicia primero el servidor local:

```powershell
.\scripts\start_opencode_server.ps1
```

La configuración de OpenCode se detecta automáticamente cuando es posible; si no, debe completarse en la pestaña de configuración.

## Comandos de desarrollo

Pendiente de verificar. Se documentarán cuando exista el proyecto ejecutable.

## Ejecución de pruebas

Verificado parcialmente. Ejecutar `pytest` desde la raíz del repositorio. Resultado actual: 31 pruebas pasando y 1 omitida.

## Compilación del instalador

Pendiente. Se evaluará PyInstaller junto con un instalador para Windows.

## Estructura del proyecto

Ver `directory-tree.txt` para la estructura actual del repositorio.

## Limitaciones conocidas

- OpenCode Desktop no está disponible en el entorno de desarrollo actual.
- La detección de múltiples instancias simultáneas no se ha verificado completamente.
- La cuota restante del servicio no está disponible en la API observada.
- PySide6 está instalado y verificado en el entorno de desarrollo.
- Tauri no es viable sin instalar Rust.

## Privacidad y seguridad

- La aplicación funcionará localmente.
- No se crearán cuentas de usuario propias en la primera versión.
- No habrá sincronización en la nube inicialmente.
- No se enviarán conversaciones ni código fuente a servicios externos.
- No se modificarán ni eliminarán datos de OpenCode.
- La primera versión se limitará a la monitorización.

## Roadmap

Ver `docs/roadmap.md`.

## Estado actual del desarrollo

Fase 0 en curso: investigación, arquitectura y documentación inicial.

## Licencia

Pendiente de decidir.
