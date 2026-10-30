# Tienda Online

**Autor:** Pedro Escarda Marescot  
**Asignatura:** Arquitectura del Software

## Descripción

Aplicación Python que modela los elementos básicos de una tienda online: **productos**, **usuarios** y **pedidos**. Está diseñada con programación orientada a objetos y una capa de servicios (`TiendaService`) que centraliza las operaciones de la tienda:

- Registrar usuarios (clientes y administradores).
- Añadir, eliminar y listar productos del inventario (electrónica y ropa).
- Realizar pedidos comprobando que el cliente existe y que hay stock suficiente.
- Consultar el histórico de pedidos de un cliente ordenado por fecha.

La aplicación se ejecuta en consola y está contenerizada con Docker.

## Estructura

```
.
├── src/
│   ├── models/
│   │   ├── Producto.py        # Producto, ProductoElectronico, ProductoRopa
│   │   ├── Usuario.py         # Usuario, Cliente, Administrador
│   │   └── Pedido.py          # Pedido
│   ├── Services/
│   │   └── Tienda_service.py  # TiendaService
│   └── main.py                # Punto de entrada
├── tests/                     # Pruebas unitarias (pytest)
├── Dockerfile
├── .dockerignore
├── requirements.txt           # Dependencias de ejecución (versiones fijadas)
└── requirements-dev.txt       # Dependencias de desarrollo (pytest)
```

## Ejecución en local

Requiere Python 3.10 o superior. La aplicación solo usa la biblioteca estándar.

```bash
pip install -r requirements.txt
python src/main.py
```

Pruebas unitarias:

```bash
pip install -r requirements-dev.txt
pytest
```

## Docker

### Construir la imagen

```bash
docker build -t tienda-online:1.0.0 -t tienda-online:latest .
```

### Ejecutar el contenedor

```bash
# Ejecución básica (el contenedor se elimina al terminar)
docker run --rm tienda-online:1.0.0

# Con un nombre de tienda personalizado
docker run --rm -e TIENDA_NOMBRE="Tienda de Pedro" tienda-online:1.0.0

# Con nombre de contenedor, para consultar después sus logs
docker run --name tienda tienda-online:1.0.0
docker logs tienda
docker rm tienda
```

### Variables de entorno

| Variable        | Descripción                                    | Valor por defecto |
|-----------------|------------------------------------------------|-------------------|
| `TIENDA_NOMBRE` | Nombre de la tienda mostrado en la cabecera    | `Tienda Online`   |

### Salida esperada

El contenedor ejecuta `src/main.py`, imprime la simulación completa y termina con código 0. Los identificadores y las fechas cambian en cada ejecución:

```
##### Tienda Online #####

=== USUARIOS ===
  [1a2b3c4d] Ana López <ana@email.com> | Cliente | Dirección: Calle Mayor 1, Madrid | is_admin: False
  ...
  [9f8e7d6c] Admin <admin@tienda.com> | Administrador | is_admin: True

=== INVENTARIO INICIAL ===
  [....] Portátil - 899.99 € (stock: 10) | Garantía: 24 meses
  ...

=== PEDIDOS ===
Pedido [....] - 30/10/2026 18:30:00
   Cliente: Ana López
   - Portátil x1 = 899.99 €
   - Auriculares x2 = 119.80 €
   Total: 1019.79 €
...

=== PRUEBAS DE ERRORES ===
  Error: Stock insuficiente de 'Portátil' (disponible: 9)
  Error: El usuario id-inexistente no existe
  Error: El usuario Admin no es un cliente
...
=== ELIMINAR PRODUCTO ===
  Eliminado 'Pantalón vaquero': True
```

### Pasos de prueba

1. `docker build -t tienda-online:1.0.0 .` termina sin errores.
2. `docker run --rm tienda-online:1.0.0` muestra las secciones USUARIOS, INVENTARIO, PEDIDOS, PRUEBAS DE ERRORES, HISTÓRICO y ELIMINAR PRODUCTO.
3. `docker run --rm -e TIENDA_NOMBRE="Prueba" tienda-online:1.0.0` muestra `##### Prueba #####` en la primera línea.
4. `docker run --rm tienda-online:1.0.0 whoami` devuelve `appuser`: el contenedor no se ejecuta como root.
5. `docker images tienda-online` muestra una imagen ligera (basada en `python:3.12-slim`).

### Publicar la imagen en Docker Hub (push)

```bash
docker login
docker tag tienda-online:1.0.0 pedroescarda/tienda-online:1.0.0
docker tag tienda-online:1.0.0 pedroescarda/tienda-online:latest
docker push pedroescarda/tienda-online:1.0.0
docker push pedroescarda/tienda-online:latest
```

### Descargar y ejecutar la imagen publicada (pull)

```bash
docker pull pedroescarda/tienda-online:1.0.0
docker run --rm pedroescarda/tienda-online:1.0.0
```

## Flujo de trabajo con Git

- `main`: rama principal y estable, protegida; los cambios entran mediante Pull Request.
- `feature/<nombre>`: una rama por funcionalidad (por ejemplo, `feature/docker`).
- Flujo de Docker: **build → run → test → push**.
