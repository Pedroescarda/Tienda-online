import pytest

from models.Producto import ProductoElectronico, ProductoRopa
from Services.Tienda_service import TiendaService


@pytest.fixture
def tienda():
    tienda = TiendaService()
    tienda.cliente = tienda.registrar_usuario("cliente", "Ana", "ana@email.com", "Calle Mayor 1")
    tienda.admin = tienda.registrar_usuario("administrador", "Admin", "admin@tienda.com")
    tienda.portatil = tienda.anadir_producto(ProductoElectronico("Portátil", 900.0, 5, 24))
    tienda.camiseta = tienda.anadir_producto(ProductoRopa("Camiseta", 20.0, 10, "M", "Azul"))
    return tienda


def test_registrar_usuarios(tienda):
    assert len(tienda.usuarios) == 2
    assert tienda.admin.is_admin()
    assert not tienda.cliente.is_admin()


def test_tipo_usuario_no_valido(tienda):
    with pytest.raises(ValueError):
        tienda.registrar_usuario("invitado", "X", "x@email.com")


def test_realizar_pedido_descuenta_stock_y_calcula_total(tienda):
    pedido = tienda.realizar_pedido(tienda.cliente.id, [(tienda.portatil.id, 1), (tienda.camiseta.id, 3)])
    assert pedido.calcular_total() == pytest.approx(960.0)
    assert tienda.portatil.stock == 4
    assert tienda.camiseta.stock == 7


def test_pedido_sin_stock_no_modifica_inventario(tienda):
    with pytest.raises(ValueError):
        tienda.realizar_pedido(tienda.cliente.id, [(tienda.camiseta.id, 1), (tienda.portatil.id, 99)])
    assert tienda.camiseta.stock == 10
    assert tienda.portatil.stock == 5


def test_pedido_usuario_inexistente_o_admin(tienda):
    with pytest.raises(ValueError):
        tienda.realizar_pedido("no-existe", [(tienda.portatil.id, 1)])
    with pytest.raises(ValueError):
        tienda.realizar_pedido(tienda.admin.id, [(tienda.portatil.id, 1)])


def test_eliminar_producto(tienda):
    assert tienda.eliminar_producto(tienda.camiseta.id)
    assert not tienda.eliminar_producto(tienda.camiseta.id)
    assert len(tienda.listar_productos()) == 1


def test_historico_pedidos_ordenado(tienda):
    p1 = tienda.realizar_pedido(tienda.cliente.id, [(tienda.camiseta.id, 1)])
    p2 = tienda.realizar_pedido(tienda.cliente.id, [(tienda.portatil.id, 1)])
    assert tienda.listar_pedidos_usuario(tienda.cliente.id) == [p1, p2]
