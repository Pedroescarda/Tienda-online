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

# La API escucha en el puerto 8000
EXPOSE 8000

# Comprueba periódicamente que la API responde (sin instalar curl en la imagen)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/')" || exit 1

# 6. Comando de inicio: servidor uvicorn con la app FastAPI de src/main.py
CMD ["uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
