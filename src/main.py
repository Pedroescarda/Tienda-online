import os
from collections import Counter

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware

from models.Pedido import Pedido
from models.Producto import Producto, ProductoElectronico, ProductoRopa
from models.Usuario import Cliente, Usuario
from schemas import (
    PedidoCreate,
    PedidoItemRead,
    PedidoRead,
    ProductoCreate,
    ProductoRead,
    UsuarioCreate,
    UsuarioRead,
)
from Services.Tienda_service import TiendaService

# Nombre de la tienda configurable con la variable de entorno TIENDA_NOMBRE
NOMBRE_TIENDA = os.getenv("TIENDA_NOMBRE", "Tienda Online")

app = FastAPI(title=f"{NOMBRE_TIENDA} API")

# Permite que el frontend (servido desde otro origen, p. ej. http://localhost:5500
# o abierto como fichero) haga peticiones HTTP a la API desde el navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

tienda = TiendaService()

# Datos de ejemplo: como todo se guarda en memoria, se cargan al arrancar el servidor
# para que la tienda no aparezca vacía.
tienda.anadir_producto(ProductoElectronico("Cascos", 60.0, 15, 6))
tienda.anadir_producto(ProductoRopa("Sudadera", 80.0, 9, "M", "Negro"))
tienda.anadir_producto(Producto("Taza de cerámica", 8.5, 25))
tienda.registrar_usuario("cliente", "Cliente de prueba", "cliente@prueba.com", "Calle Mayor 1, Madrid")


def usuario_a_schema(usuario: Usuario) -> UsuarioRead:
    return UsuarioRead(id=usuario.id, nombre=usuario.nombre, email=usuario.email, es_admin=usuario.is_admin())


def producto_a_schema(producto: Producto) -> ProductoRead:
    if isinstance(producto, ProductoElectronico):
        return ProductoRead(
            id=producto.id,
            tipo="electronico",
            nombre=producto.nombre,
            precio=producto.precio,
            stock=producto.stock,
            meses_garantia=producto.garantia_meses,
        )
    if isinstance(producto, ProductoRopa):
        return ProductoRead(
            id=producto.id,
            tipo="ropa",
            nombre=producto.nombre,
            precio=producto.precio,
            stock=producto.stock,
            talla=producto.talla,
            color=producto.color,
        )
    return ProductoRead(
        id=producto.id,
        tipo="generico",
        nombre=producto.nombre,
        precio=producto.precio,
        stock=producto.stock,
    )


def pedido_a_schema(pedido: Pedido) -> PedidoRead:
    return PedidoRead(
        id=pedido.id,
        fecha=pedido.fecha,
        cliente_id=pedido.cliente.id,
        cliente_nombre=pedido.cliente.nombre,
        total=round(pedido.calcular_total(), 2),
        items=[
            PedidoItemRead(
                producto_id=producto.id,
                nombre=producto.nombre,
                precio_unitario=producto.precio,
                cantidad=cantidad,
                subtotal=round(producto.precio * cantidad, 2),
            )
            for producto, cantidad in pedido.lineas
        ],
    )


def obtener_usuario_o_404(usuario_id: str) -> Usuario:
    usuario = tienda.obtener_usuario(usuario_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El usuario {usuario_id} no existe")
    return usuario


def obtener_producto_o_404(producto_id: str) -> Producto:
    producto = tienda.obtener_producto(producto_id)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El producto {producto_id} no existe")
    return producto


@app.get("/")
def raiz() -> dict:
    """Comprobación rápida de que la API está en marcha."""
    return {"tienda": NOMBRE_TIENDA, "estado": "ok", "docs": "/docs"}


@app.post("/usuarios", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCreate) -> UsuarioRead:
    if any(u.email.lower() == datos.email.lower() for u in tienda.listar_usuarios()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Ya existe un usuario con el email {datos.email}")
    try:
        usuario = tienda.registrar_usuario(datos.tipo, datos.nombre, datos.email, datos.direccion or "")
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return usuario_a_schema(usuario)


@app.get("/usuarios", response_model=list[UsuarioRead])
def listar_usuarios() -> list[UsuarioRead]:
    return [usuario_a_schema(u) for u in tienda.listar_usuarios()]


@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(usuario_id: str) -> UsuarioRead:
    return usuario_a_schema(obtener_usuario_o_404(usuario_id))


@app.post("/productos", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate) -> ProductoRead:
    if datos.tipo == "electronico":
        producto: Producto = ProductoElectronico(datos.nombre, datos.precio, datos.stock, datos.meses_garantia)
    elif datos.tipo == "ropa":
        producto = ProductoRopa(datos.nombre, datos.precio, datos.stock, datos.talla, datos.color)
    else:
        producto = Producto(datos.nombre, datos.precio, datos.stock)
    return producto_a_schema(tienda.anadir_producto(producto))


@app.get("/productos", response_model=list[ProductoRead])
def listar_productos() -> list[ProductoRead]:
    return [producto_a_schema(p) for p in tienda.listar_productos()]


@app.get("/productos/{producto_id}", response_model=ProductoRead)
def obtener_producto(producto_id: str) -> ProductoRead:
    return producto_a_schema(obtener_producto_o_404(producto_id))


@app.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: str) -> Response:
    if not tienda.eliminar_producto(producto_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El producto {producto_id} no existe")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/pedidos", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
def crear_pedido(datos: PedidoCreate) -> PedidoRead:
    cliente = obtener_usuario_o_404(datos.cliente_id)
    if not isinstance(cliente, Cliente):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El usuario {cliente.nombre} no es un cliente")

    cantidades: Counter[str] = Counter()
    for item in datos.items:
        cantidades[item.producto_id] += item.cantidad
    for producto_id, cantidad in cantidades.items():
        producto = obtener_producto_o_404(producto_id)
        if not producto.hay_stock(cantidad):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Stock insuficiente de '{producto.nombre}' (disponible: {producto.stock})",
            )

    try:
        pedido = tienda.realizar_pedido(cliente.id, [(i.producto_id, i.cantidad) for i in datos.items])
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return pedido_a_schema(pedido)


@app.get("/usuarios/{cliente_id}/pedidos", response_model=list[PedidoRead])
def listar_pedidos_cliente(cliente_id: str) -> list[PedidoRead]:
    cliente = obtener_usuario_o_404(cliente_id)
    if not isinstance(cliente, Cliente):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El usuario {cliente.nombre} no es un cliente")
    return [pedido_a_schema(p) for p in tienda.listar_pedidos_usuario(cliente_id)]


if __name__ == "__main__":
    from pathlib import Path

    import uvicorn

    # host="0.0.0.0" hace que el servidor acepte conexiones de otros equipos de la red,
    # no solo de localhost (127.0.0.1).
    print("Documentación local:  http://127.0.0.1:8000/docs")
    print("Desde otro equipo:    http://<IP-de-este-equipo>:8000/docs")
    uvicorn.run("main:app", app_dir=str(Path(__file__).parent), host="0.0.0.0", port=8000, reload=True)
