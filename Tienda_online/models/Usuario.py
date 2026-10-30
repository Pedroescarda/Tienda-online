import uuid


class Usuario:
    """Usuario genérico de la tienda."""

    def __init__(self, nombre: str, email: str) -> None:
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email

    def is_admin(self) -> bool:
        """Indica si el usuario es administrador."""
        return False

    def __str__(self) -> str:
        return f"[{self.id[:8]}] {self.nombre} <{self.email}>"


class Cliente(Usuario):
    """Cliente de la tienda con dirección postal."""

    def __init__(self, nombre: str, email: str, direccion: str) -> None:
        super().__init__(nombre, email)
        self.direccion: str = direccion

    def __str__(self) -> str:
        return f"{super().__str__()} | Cliente | Dirección: {self.direccion}"


class Administrador(Usuario):
    """Gestor de la tienda."""

    def is_admin(self) -> bool:
        """Indica si el usuario es administrador."""
        return True

    def __str__(self) -> str:
        return f"{super().__str__()} | Administrador"
