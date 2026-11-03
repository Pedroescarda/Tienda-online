from fastapi.testclient import TestClient

from main import app

cliente = TestClient(app)


def crear_cliente(email: str) -> dict:
    respuesta = cliente.post(
        "/usuarios",
        json={"nombre": "Ana", "email": email, "tipo": "cliente", "direccion": "Calle Mayor 1"},
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def crear_producto(stock: int = 5) -> dict:
    respuesta = cliente.post(
        "/productos",
        json={"tipo": "electronico", "nombre": "Portátil", "precio": 900.0, "stock": stock, "meses_garantia": 24},
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def test_raiz_responde_ok():
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"


def test_listar_productos_de_ejemplo():
    respuesta = cliente.get("/productos")
    assert respuesta.status_code == 200
    assert len(respuesta.json()) >= 3


def test_crear_pedido_descuenta_stock():
    usuario = crear_cliente("pedido@test.com")
    producto = crear_producto(stock=5)
    respuesta = cliente.post(
        "/pedidos",
        json={"cliente_id": usuario["id"], "items": [{"producto_id": producto["id"], "cantidad": 2}]},
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["total"] == 1800.0
    assert cliente.get(f"/productos/{producto['id']}").json()["stock"] == 3
    pedidos = cliente.get(f"/usuarios/{usuario['id']}/pedidos").json()
    assert len(pedidos) == 1


def test_pedido_sin_stock_devuelve_409():
    usuario = crear_cliente("stock@test.com")
    producto = crear_producto(stock=1)
    respuesta = cliente.post(
        "/pedidos",
        json={"cliente_id": usuario["id"], "items": [{"producto_id": producto["id"], "cantidad": 5}]},
    )
    assert respuesta.status_code == 409


def test_email_duplicado_devuelve_409():
    crear_cliente("duplicado@test.com")
    respuesta = cliente.post(
        "/usuarios",
        json={"nombre": "Otra", "email": "duplicado@test.com", "tipo": "cliente", "direccion": "Calle 2"},
    )
    assert respuesta.status_code == 409


def test_usuario_inexistente_devuelve_404():
    assert cliente.get("/usuarios/no-existe").status_code == 404
