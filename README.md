# Tienda Online

**Autor:** Pedro Escarda Marescot  
**Asignatura:** Arquitectura del Software

## Descripción

API REST en Python (FastAPI) de una tienda online desarrollada en la Práctica 2. Gestiona **productos**, **usuarios** y **pedidos** mediante una capa de servicios (`TiendaService`):

- Registrar usuarios (clientes y administradores) y consultarlos.
- Crear, listar, consultar y eliminar productos (genéricos, electrónica y ropa).
- Realizar pedidos comprobando que el cliente existe y que hay stock suficiente.
- Consultar el histórico de pedidos de un cliente.

Los datos se guardan en memoria y al arrancar se cargan unos productos y un cliente de ejemplo. La aplicación está contenerizada con Docker.

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
│   ├── schemas.py             # Modelos Pydantic de entrada y salida
│   └── main.py                # API FastAPI (punto de entrada)
├── tests/                     # Pruebas unitarias y de la API (pytest)
├── Dockerfile
├── .dockerignore
├── requirements.txt           # Dependencias de ejecución (versiones fijadas)
└── requirements-dev.txt       # Dependencias de desarrollo (pytest, httpx)
```

## Ejecución en local (sin Docker)

Requiere Python 3.10 o superior.

```bash
pip install -r requirements.txt
cd src
python main.py
```

La API queda en http://localhost:8000 y la documentación interactiva en http://localhost:8000/docs.

Pruebas:

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
# Ejecución básica: publica el puerto 8000 del contenedor en el 8000 del equipo
docker run --rm -p 8000:8000 tienda-online:1.0.0

# En segundo plano, con nombre y un nombre de tienda personalizado
docker run -d --name tienda -p 8000:8000 -e TIENDA_NOMBRE="Tienda de Pedro" tienda-online:1.0.0
docker logs tienda      # ver las peticiones recibidas
docker stop tienda && docker rm tienda

# En otro puerto del equipo (por ejemplo, 8080)
docker run --rm -p 8080:8000 tienda-online:1.0.0
```

### Variables de entorno

| Variable        | Descripción                                               | Valor por defecto |
|-----------------|-----------------------------------------------------------|-------------------|
| `TIENDA_NOMBRE` | Nombre de la tienda (se devuelve en `GET /` y en `/docs`) | `Tienda Online`   |

### Salida esperada

Al arrancar, el contenedor muestra el log de uvicorn:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Endpoints para probar

| Método y ruta                    | Descripción                          | Respuesta |
|----------------------------------|--------------------------------------|-----------|
| `GET /`                          | Estado de la API                     | 200 `{"tienda": "Tienda Online", "estado": "ok", "docs": "/docs"}` |
| `GET /docs`                      | Documentación interactiva (Swagger)  | 200 |
| `GET /productos`                 | Lista de productos                   | 200 + 3 productos de ejemplo |
| `POST /productos`                | Crear producto                       | 201 |
| `GET /usuarios`                  | Lista de usuarios                    | 200 + cliente de ejemplo |
| `POST /usuarios`                 | Crear usuario                        | 201 (409 si el email ya existe) |
| `POST /pedidos`                  | Crear pedido                         | 201 (409 si no hay stock) |
| `GET /usuarios/{id}/pedidos`     | Pedidos de un cliente                | 200 |
| `DELETE /productos/{id}`         | Eliminar producto                    | 204 |

### Pasos de prueba

Con el contenedor en marcha (`docker run --rm -p 8000:8000 tienda-online:1.0.0`):

1. Abrir http://localhost:8000/docs en el navegador: aparece Swagger con todos los endpoints.
2. `curl http://localhost:8000/` devuelve `"estado": "ok"`.
3. `curl http://localhost:8000/productos` devuelve los 3 productos de ejemplo.
4. Crear un pedido (sustituye los ids por los de `GET /usuarios` y `GET /productos`):
   ```bash
   curl -X POST http://localhost:8000/pedidos -H "Content-Type: application/json" \
        -d '{"cliente_id": "<id-cliente>", "items": [{"producto_id": "<id-producto>", "cantidad": 1}]}'
   ```
   Devuelve 201 con el total del pedido y el stock del producto baja en 1.
5. `docker run --rm -e TIENDA_NOMBRE="Prueba" -p 8000:8000 tienda-online:1.0.0` → `GET /` devuelve `"tienda": "Prueba"`.
6. `docker run --rm tienda-online:1.0.0 whoami` devuelve `appuser`: el contenedor no se ejecuta como root.
7. `docker ps` muestra el contenedor como `healthy` (el `HEALTHCHECK` consulta `GET /` cada 30 s).

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
docker run --rm -p 8000:8000 pedroescarda/tienda-online:1.0.0
```

## Flujo de trabajo con Git

- `main`: rama principal y estable, protegida; los cambios entran mediante Pull Request.
- `feature/<nombre>`: una rama por funcionalidad (por ejemplo, `feature/docker`).
- Flujo de Docker: **build → run → test → push**.
