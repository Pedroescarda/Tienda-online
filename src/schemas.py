from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=1)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    tipo: Literal["cliente", "administrador"]
    direccion: str | None = None

    @model_validator(mode="after")
    def validar_direccion(self) -> "UsuarioCreate":
        if self.tipo == "cliente" and not self.direccion:
            raise ValueError("La dirección postal es obligatoria para los clientes")
        return self


class UsuarioRead(BaseModel):
    id: str
    nombre: str
    email: str
    es_admin: bool


class ProductoCreate(BaseModel):
    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str = Field(min_length=1)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)
    meses_garantia: int | None = Field(default=None, ge=0)
    talla: str | None = None
    color: str | None = None

    @model_validator(mode="after")
    def validar_atributos(self) -> "ProductoCreate":
        if self.tipo == "electronico":
            if self.meses_garantia is None:
                raise ValueError("meses_garantia es obligatorio para productos electrónicos")
            if self.talla is not None or self.color is not None:
                raise ValueError("talla y color no aplican a productos electrónicos")
        elif self.tipo == "ropa":
            if not self.talla or not self.color:
                raise ValueError("talla y color son obligatorios para productos de ropa")
            if self.meses_garantia is not None:
                raise ValueError("meses_garantia no aplica a productos de ropa")
        elif self.meses_garantia is not None or self.talla is not None or self.color is not None:
            raise ValueError("Los productos genéricos no admiten atributos adicionales")
        return self


class ProductoRead(BaseModel):
    id: str
    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str
    precio: float
    stock: int
    meses_garantia: int | None = None
    talla: str | None = None
    color: str | None = None


class PedidoItemCreate(BaseModel):
    producto_id: str
    cantidad: int = Field(gt=0)


class PedidoCreate(BaseModel):
    cliente_id: str
    items: list[PedidoItemCreate] = Field(min_length=1)


class PedidoItemRead(BaseModel):
    producto_id: str
    nombre: str
    precio_unitario: float
    cantidad: int
    subtotal: float


class PedidoRead(BaseModel):
    id: str
    fecha: datetime
    cliente_id: str
    cliente_nombre: str
    total: float
    items: list[PedidoItemRead]
