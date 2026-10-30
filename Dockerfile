# 1. Imagen base ligera de Python
FROM python:3.12-slim

# Sin ficheros .pyc, salida sin buffer y pip sin caché
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TIENDA_NOMBRE="Tienda Online"

WORKDIR /app

# Usuario sin privilegios para ejecutar la aplicación
RUN useradd --create-home --uid 1000 appuser

# 2. Copia primero las dependencias para aprovechar la caché de capas
COPY requirements.txt .

# 3. Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia el código fuente
COPY src/ ./src/

# 5. Permisos: el usuario appuser es dueño del código y puede ejecutarlo
RUN chown -R appuser:appuser /app && chmod -R u+rx /app/src

USER appuser

# 6. Comando de inicio
CMD ["python", "src/main.py"]
