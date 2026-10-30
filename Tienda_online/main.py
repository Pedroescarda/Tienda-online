from models.Producto import ProductoElectronico, ProductoRopa
from Services.Tienda_service import TiendaService


def mostrar_productos(tienda: TiendaService) -> None:
    """Imprime el inventario de la tienda."""
    for producto in tienda.listar_productos():
        print(f"  {producto}")


def main() -> None:
    """Punto de entrada para probar la tienda online."""
    tienda = TiendaService()

    ana = tienda.registrar_usuario("cliente", "Ana López", "ana@email.com", "Calle Mayor 1, Madrid")
    luis = tienda.registrar_usuario("cliente", "Luis García", "luis@email.com", "Av. Diagonal 20, Barcelona")
    marta = tienda.registrar_usuario("cliente", "Marta Ruiz", "marta@email.com", "Calle Sierpes 5, Sevilla")
    admin = tienda.registrar_usuario("administrador", "Admin", "admin@tienda.com")

    print("=== USUARIOS ===")
    for usuario in tienda.usuarios.values():
        print(f"  {usuario} | is_admin: {usuario.is_admin()}")

    portatil = tienda.anadir_producto(ProductoElectronico("Portátil", 899.99, 10, 24))
    auriculares = tienda.anadir_producto(ProductoElectronico("Auriculares", 59.90, 25, 12))
    movil = tienda.anadir_producto(ProductoElectronico("Móvil", 499.00, 15, 24))
    camiseta = tienda.anadir_producto(ProductoRopa("Camiseta", 19.95, 50, "M", "Azul"))
    pantalon = tienda.anadir_producto(ProductoRopa("Pantalón vaquero", 39.99, 30, "42", "Negro"))

    print("\n=== INVENTARIO INICIAL ===")
    mostrar_productos(tienda)

    print("\n=== PEDIDOS ===")
    pedido1 = tienda.realizar_pedido(ana.id, [(portatil.id, 1), (auriculares.id, 2)])
    print(pedido1)
    pedido2 = tienda.realizar_pedido(luis.id, [(camiseta.id, 3), (pantalon.id, 2), (movil.id, 1)])
    print(pedido2)
    pedido3 = tienda.realizar_pedido(marta.id, [(auriculares.id, 1), (camiseta.id, 2)])
    print(pedido3)
    pedido4 = tienda.realizar_pedido(ana.id, [(pantalon.id, 1), (movil.id, 1)])
    print(pedido4)

    print("\n=== PRUEBAS DE ERRORES ===")
    try:
        tienda.realizar_pedido(luis.id, [(portatil.id, 100)])
    except ValueError as error:
        print(f"  Error: {error}")
    try:
        tienda.realizar_pedido("id-inexistente", [(portatil.id, 1)])
    except ValueError as error:
        print(f"  Error: {error}")
    try:
        tienda.realizar_pedido(admin.id, [(portatil.id, 1)])
    except ValueError as error:
        print(f"  Error: {error}")

    print(f"\n=== HISTÓRICO DE PEDIDOS DE {ana.nombre.upper()} ===")
    for pedido in tienda.listar_pedidos_usuario(ana.id):
        print(pedido)

    print("\n=== INVENTARIO ACTUALIZADO ===")
    mostrar_productos(tienda)

    print("\n=== ELIMINAR PRODUCTO ===")
    print(f"  Eliminado '{pantalon.nombre}': {tienda.eliminar_producto(pantalon.id)}")
    mostrar_productos(tienda)


if __name__ == "__main__":
    main()
