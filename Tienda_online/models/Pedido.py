import uuid
from datetime import datetime

from models.Producto import Producto
from models.Usuario import Cliente


class Pedido:
    """Pedido de un cliente con una lista de productos y sus cantidades."""

    def __init__(self, cliente: Cliente, lineas: list[tuple[Producto, int]]) -> None:
        self.id: str = str(uuid.uuid4())
        self.cliente: Cliente = cliente
        self.lineas: list[tuple[Producto, int]] = lineas
        self.fecha: datetime = datetime.now()

    def calcular_total(self) -> float:
        """Calcula el importe total del pedido."""
        return sum(producto.precio * cantidad for producto, cantidad in self.lineas)

    def __str__(self) -> str:
        detalle = "\n".join(
            f"   - {producto.nombre} x{cantidad} = {producto.precio * cantidad:.2f} €"
            for producto, cantidad in self.lineas
        )
        return (
            f"Pedido [{self.id[:8]}] - {self.fecha:%d/%m/%Y %H:%M:%S}\n"
            f"   Cliente: {self.cliente.nombre}\n"
            f"{detalle}\n"
            f"   Total: {self.calcular_total():.2f} €"
        )
