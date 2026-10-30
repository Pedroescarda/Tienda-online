# Imagen ligera de Python
FROM python:3.12-slim

# Evita ficheros .pyc y fuerza salida sin buffer en consola
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copia el código de la aplicación
COPY Tienda_online/ /app/

# Ejecuta la aplicación con un usuario sin privilegios
RUN useradd --create-home appuser
USER appuser

CMD ["python", "main.py"]
