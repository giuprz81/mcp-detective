# MCP Detective – Deber 5

## 1. Arquitectura de la solución MCP

La solución implementada utiliza una arquitectura en la que intervienen cuatro componentes principales:

### 1.1. LLM (Large Language Model)

Es el modelo de lenguaje que interpreta las instrucciones del usuario, analiza la información obtenida mediante las herramientas MCP y genera respuestas en lenguaje natural.

En este proyecto se utilizó Claude Code con el modelo Claude Haiku 5.5.

El LLM no accede directamente a la información interna del servidor. Solicita la ejecución de herramientas para obtener los datos necesarios.

### 1.2. Harness / Host

Es el entorno que administra la interacción entre el usuario, el modelo de lenguaje y las herramientas disponibles.

En este proyecto, Claude Code actúa como entorno host. Se encarga de gestionar la sesión, presentar las respuestas y coordinar las solicitudes de herramientas MCP.

### 1.3. Cliente MCP

Es el componente que permite al host comunicarse con los servidores MCP mediante el protocolo Model Context Protocol.

En este proyecto, Claude Code incorpora el cliente MCP y establece la comunicación con el servidor `mcp-detective` mediante transporte STDIO.

### 1.4. Servidor MCP

Es el componente desarrollado en Python que expone las herramientas y ejecuta la lógica de negocio.

El servidor implementado proporciona tres herramientas:

- `listar_casos`: devuelve los incidentes registrados y su cantidad de eventos.
- `consultar_eventos`: permite consultar los eventos correspondientes a un incidente.
- `registrar_alerta`: valida y registra una alerta en memoria.

## 2. ¿Quién ejecuta realmente el código Python?

El código Python es ejecutado por el proceso del servidor MCP, no por el modelo de lenguaje.

Cuando Claude Code necesita consultar información o registrar una alerta, solicita la ejecución de una herramienta mediante el cliente MCP.

El cliente transmite la solicitud al servidor, que ejecuta la función Python correspondiente y devuelve el resultado.

El LLM interpreta posteriormente la respuesta y la presenta al usuario.

Por tanto, el modelo de lenguaje decide cuándo necesita una herramienta, pero la ejecución real y las validaciones corresponden al servidor MCP.

## 3. Análisis del incidente INC-003

El incidente INC-003 afecta al sistema `panel_administracion` y contiene cinco eventos relacionados con intentos de autenticación de la cuenta `admin`.

Los registros muestran:

- Cuatro intentos de inicio de sesión fallidos entre las 03:00 y las 03:03 del 15 de octubre de 2026.
- Los cuatro intentos proceden de la dirección IP `192.0.2.50`.
- A las 03:04 se registra un inicio de sesión exitoso desde la misma dirección IP.

Esta secuencia justifica registrar una alerta de nivel alto porque existe una sucesión de intentos fallidos seguida de un acceso exitoso a una cuenta administrativa.

Sin embargo, los registros disponibles no permiten confirmar que se haya producido una intrusión. Tampoco identifican a la persona que realizó el acceso ni las acciones ejecutadas posteriormente.

Por este motivo, la alerta tiene como finalidad solicitar una investigación adicional y no declarar una vulneración confirmada.

La alerta se registró correctamente mediante la herramienta `registrar_alerta`, con los siguientes datos:

- Caso: INC-003.
- Nivel: alto.
- Estado: registrada.

## 4. Validación y seguridad de las herramientas

Las validaciones de los datos deben ejecutarse en el servidor MCP y no depender exclusivamente del modelo de lenguaje.

El LLM puede interpretar instrucciones o generar parámetros incorrectos. Por esta razón, el servidor implementa controles que garantizan la integridad de las operaciones.

### 4.1. Caso inexistente

Al consultar el identificador `INC-999`, la herramienta `consultar_eventos` devuelve un error porque el caso no existe.

La herramienta no debe devolver una lista vacía ni inventar eventos.

En la prueba realizada con Claude Code, el agente informó que el caso no existía y no presentó información ficticia.

### 4.2. Nivel de alerta inválido

La herramienta `registrar_alerta` únicamente admite los niveles:

- bajo
- medio
- alto

Si se proporciona un nivel diferente, como `critico`, el servidor rechaza la operación.

### 4.3. Motivo vacío

El servidor verifica que el motivo de la alerta contenga texto válido. Una cadena compuesta únicamente por espacios debe rechazarse.

### 4.4. Alertas duplicadas

El servidor permite registrar una sola alerta por caso durante la ejecución del proceso.

Si se intenta registrar una segunda alerta para el mismo incidente, la operación se rechaza.

### 4.5. Responsabilidad de las validaciones

El servidor MCP es responsable de ejecutar las validaciones y rechazar las solicitudes que incumplan las reglas establecidas.

El modelo de lenguaje puede ayudar a interpretar los resultados, pero no constituye un mecanismo de seguridad suficiente por sí solo.

## 5. Integración con Claude Code

Para la integración se utilizó Claude Code como agente capaz de consumir las herramientas del servidor MCP.

El procedimiento realizado fue:

1. Instalar Claude Code CLI en Windows.
2. Configurar la variable de entorno `ANTHROPIC_API_KEY` para utilizar la clave API proporcionada para la práctica.
3. Abrir una sesión de Claude Code desde la carpeta del proyecto.
4. Detectar y autorizar el servidor MCP `mcp-detective`.
5. Comprobar la disponibilidad de las tres herramientas mediante el comando `/mcp`.
6. Ejecutar instrucciones en lenguaje natural para investigar los incidentes.
7. Registrar una alerta para INC-003.
8. Consultar el identificador inexistente INC-999 y comprobar la respuesta de error.

La conexión se realizó mediante transporte STDIO, utilizando la configuración del servidor definida en `.mcp.json`.

### 5.1. Investigación realizada por el agente

El agente utilizó las herramientas MCP para:

- Descubrir los tres incidentes registrados.
- Consultar los eventos de INC-001, INC-002 e INC-003.
- Presentar las evidencias y sus interpretaciones.
- Registrar una alerta de nivel alto para INC-003.
- Consultar INC-999 y comunicar que no existía.

Durante la investigación se indicó al agente que no debía abrir directamente `casos.json`, inspeccionar archivos ni inventar información.

### 5.2. Evidencias de integración

Las capturas de pantalla de las pruebas realizadas se encuentran en la carpeta `evidencias/`:

- `agente_tools.png`: investigación y consultas realizadas mediante herramientas MCP.
- `agente_alerta.png`: registro de la alerta para INC-003.
- `agente_error.png`: consulta del caso inexistente INC-999.
- `inspector_tools.png`: herramientas registradas en MCP Inspector.
- `inspector_pruebas.png`: pruebas funcionales de las herramientas.
- `inspector_memoria.png`: comprobación del comportamiento de las alertas después de reiniciar el servidor.
- `evidencia_D7.png`: validación del motivo compuesto únicamente por espacios.

## 6. Instalación y ejecución del proyecto

### 6.1. Requisitos

- Python 3.12 o superior.
- uv.
- MCP SDK.
- pytest.

### 6.2. Instalación

Desde la carpeta raíz del proyecto, ejecutar:

```powershell
uv sync
```

### 6.3. Ejecución del servidor MCP

Para iniciar el servidor mediante STDIO:

```powershell
uv run mcp run server.py
```

El servidor debe ejecutarse como proceso independiente y permanecer disponible para el cliente MCP.

### 6.4. Ejecución de las pruebas

Para ejecutar las pruebas automatizadas:

```powershell
uv run pytest -q
```

## 7. Conclusión

El proyecto MCP Detective permitió implementar y comprobar una arquitectura basada en el protocolo Model Context Protocol, integrando un modelo de lenguaje con un servidor Python que proporciona herramientas específicas.

Las pruebas permitieron verificar la consulta de incidentes, la obtención de eventos, el registro de alertas, la validación de parámetros y el control de alertas duplicadas.

La integración con Claude Code demostró cómo un agente puede utilizar herramientas externas para investigar incidentes, fundamentar sus respuestas en datos obtenidos del servidor y respetar las restricciones establecidas para la práctica.