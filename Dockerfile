# Usa una imagen base de Python
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y código
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expone el puerto para FastAPI
EXPOSE 8000

# Comando para correr FastAPI con recarga automática
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]