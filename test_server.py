
import pytest

import server


@pytest.fixture(autouse=True)
def limpiar_alertas():
    """
    Limpia el almacenamiento de alertas antes y después
    de cada prueba para evitar interferencias.
    """
    server.alertas_registradas.clear()
    yield
    server.alertas_registradas.clear()


def test_listar_casos():
    """Comprueba que existan los tres casos y sus cantidades."""
    casos = server.obtener_lista_casos()

    assert len(casos) == 3

    assert casos == [
        {
            "id": "INC-001",
            "system": "portal_acceso",
            "eventos": 2
        },
        {
            "id": "INC-002",
            "system": "portal_acceso",
            "eventos": 6
        },
        {
            "id": "INC-003",
            "system": "panel_administracion",
            "eventos": 5
        }
    ]


def test_consultar_eventos_inc002():
    """Comprueba los seis intentos fallidos de INC-002."""
    eventos = server.obtener_eventos("INC-002")

    assert len(eventos) == 6
    assert all(evento["user"] == "admin" for evento in eventos)
    assert all(
        evento["ip"] == "203.0.113.25"
        for evento in eventos
    )
    assert all(
        evento["event"] == "LOGIN_FAILED"
        for evento in eventos
    )


def test_caso_inexistente():
    """Comprueba que un caso inexistente genere ValueError."""
    with pytest.raises(ValueError, match="no existe"):
        server.obtener_eventos("INC-999")


def test_registrar_alerta_valida():
    """Comprueba que se pueda registrar una alerta válida."""
    alerta = server.guardar_alerta(
        "INC-003",
        "alto",
        "Cuatro fallos y un acceso exitoso desde la misma IP; requiere investigación"
    )

    assert alerta == {
        "caso_id": "INC-003",
        "nivel": "alto",
        "motivo": (
            "Cuatro fallos y un acceso exitoso desde la misma IP; "
            "requiere investigación"
        ),
        "estado": "registrada"
    }

    assert "INC-003" in server.alertas_registradas


def test_rechazar_alerta_duplicada():
    """Comprueba que no se registren dos alertas para el mismo caso."""
    server.guardar_alerta(
        "INC-003",
        "alto",
        "Primera alerta de prueba"
    )

    with pytest.raises(ValueError, match="Ya existe una alerta"):
        server.guardar_alerta(
            "INC-003",
            "medio",
            "Segunda alerta de prueba"
        )


def test_rechazar_nivel_invalido():
    """Comprueba que solo se acepten los niveles permitidos."""
    with pytest.raises(ValueError, match="Nivel inválido"):
        server.guardar_alerta(
            "INC-002",
            "critico",
            "Nivel no permitido"
        )


def test_rechazar_motivo_vacio():
    """Comprueba que no se acepte un motivo compuesto por espacios."""
    with pytest.raises(ValueError, match="no puede estar vacío"):
        server.guardar_alerta(
            "INC-002",
            "medio",
            "   "
        )
