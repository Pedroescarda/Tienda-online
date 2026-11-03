from models.Pedido import Pedido
from models.Producto import Producto
from models.Usuario import Administrador, Cliente, Usuario


class TiendaService:
    """Capa de servicios que gestiona usuarios, inventario y pedidos."""

    def __init__(self) -> None:
        self.usuarios: dict[str, Usuario] = {}
        self.productos: dict[str, Producto] = {}
        self.pedidos: list[Pedido] = []

    def registrar_usuario(self, tipo: str, nombre: str, email: str, direccion: str = "") -> Usuario:
        """Registra un cliente o un administrador y lo devuelve."""
        tipo = tipo.lower()
        if tipo == "cliente":
            usuario: Usuario = Cliente(nombre, email, direccion)
        elif tipo == "administrador":
            usuario = Administrador(nombre, email)
        else:
            raise ValueError(f"Tipo de usuario no válido: {tipo}")
        self.usuarios[usuario.id] = usuario
        return usuario

    def obtener_usuario(self, usuario_id: str) -> Usuario | None:
        return self.usuarios.get(usuario_id)

    def listar_usuarios(self) -> list[Usuario]:
        return list(self.usuarios.values())

    def obtener_producto(self, producto_id: str) -> Producto | None:
        return self.productos.get(producto_id)

    def anadir_producto(self, producto: Producto) -> Producto:
        """Añade un producto al inventario."""
        self.productos[producto.id] = producto
        return producto

    def eliminar_producto(self, producto_id: str) -> bool:
        """Elimina un producto del inventario por su id."""
        return self.productos.pop(producto_id, None) is not None

    def listar_productos(self) -> list[Producto]:
        """Devuelve todos los productos del inventario."""
        return list(self.productos.values())

    def realizar_pedido(self, usuario_id: str, items: list[tuple[str, int]]) -> Pedido:
        """Crea un pedido si el cliente existe y hay stock de todos los productos."""
        usuario = self.usuarios.get(usuario_id)
        if usuario is None:
            raise ValueError(f"El usuario {usuario_id} no existe")
        if not isinstance(usuario, Cliente):
            raise ValueError(f"El usuario {usuario.nombre} no es un cliente")

        lineas: list[tuple[Producto, int]] = []
        for producto_id, cantidad in items:
            producto = self.productos.get(producto_id)
            if producto is None:
                raise ValueError(f"El producto {producto_id} no existe")
            if not producto.hay_stock(cantidad):
                raise ValueError(f"Stock insuficiente de '{producto.nombre}' (disponible: {producto.stock})")
            lineas.append((producto, cantidad))

        for producto, cantidad in lineas:
            producto.actualizar_stock(-cantidad)

        pedido = Pedido(usuario, lineas)
        self.pedidos.append(pedido)
        return pedido

    def listar_pedidos_usuario(self, usuario_id: str) -> list[Pedido]:
        """Devuelve los pedidos de un usuario ordenados por fecha."""
        return sorted(
            (p for p in self.pedidos if p.cliente.id == usuario_id),
            key=lambda p: p.fecha,
        )
