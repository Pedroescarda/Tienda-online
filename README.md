# Tienda Online

**Autor:** Pedro Escarda Marescot
**Asignatura:** Arquitectura del Software

## Descripción

Aplicación Python que modela los elementos básicos de una tienda online: **productos**, **usuarios** y **pedidos**. Está diseñada con programación orientada a objetos y una capa de servicios (`TiendaService`) que centraliza las operaciones de la tienda:

- Registrar usuarios (clientes y administradores).
- Añadir, eliminar y listar productos del inventario (electrónica y ropa).
- Realizar pedidos comprobando que el cliente existe y que hay stock suficiente.
- Consultar el histórico de pedidos de un cliente ordenado por fecha.

Esta primera versión se ejecuta en consola, pero la arquitectura (modelos + servicios) está pensada para evolucionar hacia una API REST con FastAPI en prácticas posteriores.

## Estructura

```
src/
├── models/
│   ├── __init__.py
│   ├── Producto.py     # Producto, ProductoElectronico, ProductoRopa
│   ├── Usuario.py      # Usuario, Cliente, Administrador
│   └── Pedido.py       # Pedido
├── Services/
│   ├── __init__.py
│   └── Tienda_service.py  # TiendaService
└── main.py             # Punto de entrada y pruebas manuales
```

## Ejecución

Requiere Python 3.10 o superior (sin dependencias externas).

```bash
python src/main.py
```

## Ejecución con Docker

```bash
docker build -t tienda-online .
docker run --rm tienda-online
```

## Flujo de trabajo con Git

- `main`: rama principal y estable.
- `feature/<nombre>`: una rama por funcionalidad, que se integra en `main` mediante Pull Request.
