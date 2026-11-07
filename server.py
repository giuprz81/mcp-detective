
import json
from pathlib import Path

from mcp.server import MCPServer


# ============================================================
# 1. CONFIGURACION DEL SERVIDOR
# ============================================================

mcp = MCPServer("MCP Detective")

# Ruta absoluta al archivo casos.json, independiente
# de la carpeta desde la que se ejecute el servidor.
RUTA_CASOS = Path(__file__).resolve().parent / "casos.json"

# Almacenamiento temporal de alertas.
# Se reinicia cuando se detiene y vuelve a iniciar el servidor.
alertas_registradas = {}


# ============================================================
# 2. CARGA DE DATOS
# ============================================================

def cargar_casos() -> list[dict]:
    """Carga los casos desde el archivo casos.json."""
    with RUTA_CASOS.open("r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    return datos["casos"]


# ============================================================
# 3. FUNCIONES DE LOGICA DE NEGOCIO
# ============================================================

def obtener_lista_casos() -> list[dict]:
    """
    Devuelve el identificador, sistema y cantidad de eventos
    de cada caso, sin emitir conclusiones.
    """
    casos = cargar_casos()

    return [
        {
            "id": caso["id"],
            "system": caso["system"],
            "eventos": len(caso["eventos"])
        }
        for caso in casos
    ]


def obtener_eventos(caso_id: str) -> list[dict]:
    """
    Busca un caso por su identificador y devuelve sus eventos.
    Genera ValueError cuando el caso no existe.
    """
    casos = cargar_casos()

    for caso in casos:
        if caso["id"] == caso_id:
            return caso["eventos"]

    raise ValueError(f"El caso '{caso_id}' no existe.")



def guardar_alerta(
    caso_id: str,
    nivel: str,
    motivo: str
) -> dict:
    """
    Valida y registra una alerta en memoria.
    Solo permite una alerta por caso durante el proceso.
    """

    # Validar que el caso exista.
    casos = cargar_casos()
    ids_existentes = {caso["id"] for caso in casos}

    if caso_id not in ids_existentes:
        raise ValueError(f"El caso '{caso_id}' no existe.")

    # Validar el nivel de alerta.
    niveles_permitidos = {"bajo", "medio", "alto"}

    if not isinstance(nivel, str) or nivel not in niveles_permitidos:
        raise ValueError(
            "Nivel inválido. Los niveles permitidos son: "
            "bajo, medio y alto."
        )

    # Validar el motivo.
    if not isinstance(motivo, str) or not motivo.strip():
        raise ValueError("El motivo de la alerta no puede estar vacío.")

    # Evitar alertas duplicadas.
    if caso_id in alertas_registradas:
        raise ValueError(
            f"Ya existe una alerta registrada para el caso '{caso_id}'."
        )

    # Crear y almacenar la alerta.
    alerta = {
        "caso_id": caso_id,
        "nivel": nivel,
        "motivo": motivo.strip(),
        "estado": "registrada"
    }

    alertas_registradas[caso_id] = alerta

    return alerta



# ============================================================
# 4. REGISTRO DE HERRAMIENTAS MCP
# ============================================================

@mcp.tool()
def listar_casos() -> list[dict]:
    """
    Lista los casos disponibles en el sistema Centinela.

    Devuelve el identificador, el sistema asociado y la
    cantidad de eventos registrados para cada caso.
    No realiza análisis ni emite conclusiones.
    """
    return obtener_lista_casos()


@mcp.tool()
def consultar_eventos(caso_id: str) -> list[dict]:
    """
    Consulta los eventos asociados a un caso específico.

    Parámetro:
        caso_id: identificador del incidente que se desea consultar.

    Devuelve los registros exactos del caso.
    Si el identificador no existe, genera un error explícito.
    """
    return obtener_eventos(caso_id)


@mcp.tool()
def registrar_alerta(
    caso_id: str,
    nivel: str,
    motivo: str
) -> dict:
    """
    Registra una alerta para un caso existente.

    Parámetros:
        caso_id: identificador del incidente.
        nivel: nivel de alerta (bajo, medio o alto).
        motivo: justificación de la alerta.

    Solo permite una alerta por caso durante el proceso
    actual del servidor.
    """
    return guardar_alerta(caso_id, nivel, motivo)


# ============================================================
# 5. INICIO DEL SERVIDOR MCP
# ============================================================

if __name__ == "__main__":
    mcp.run(transport="stdio")
