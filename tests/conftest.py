# tests/conftest.py
from __future__ import annotations

import pytest

from graphtec.core.device import GraphtecDevice

# Ajusta estas rutas a donde los tengas en tu carpeta tests/
from tests.mocks.mock_connection import MockConnection
from tests.mocks.responses import build_responses


@pytest.fixture
def responses() -> dict[str, bytes]:
    """
    Diccionario comando -> bytes que devuelve el mock.
    Centralízalo en tests/mocks/responses.py.
    """
    return build_responses()


@pytest.fixture
def conn(responses: dict[str, bytes]) -> MockConnection:
    """
    Conexión mock ya abierta (como haría GraphtecConnection.open()).
    """
    c = MockConnection(responses=responses, strict=True)
    c.open()
    return c


@pytest.fixture
def device(conn: MockConnection) -> GraphtecDevice:
    """
    Dispositivo con todos los módulos inicializados sobre la MockConnection.
    """
    return GraphtecDevice(conn)


@pytest.fixture
def graphtec(monkeypatch, conn: MockConnection):
    """
    Fachada pública Graphtec pero forzando que use MockConnection.
    Útil para tests de integración sin hardware.

    Uso:
        def test_algo(graphtec):
            graphtec.connect()
            assert graphtec.is_connected()
    """
    # Import local para que el monkeypatch afecte al módulo correcto
    import graphtec.api.public as public_mod
    from graphtec.api.public import Graphtec

    def fake_connection_factory(connection_type="usb", **kwargs):
        # Devuelve SIEMPRE el mock ya abierto
        return conn

    monkeypatch.setattr(public_mod, "GraphtecConnection", fake_connection_factory)

    g = Graphtec(connection_type="usb")
    return g
