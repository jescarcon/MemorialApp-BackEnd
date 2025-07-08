FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias de compilación y librerías de MySQL
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Dependencias
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Código
COPY . .

EXPOSE 8000

CMD ["gunicorn", "CoreApp.wsgi:application", "--bind", "0.0.0.0:8000"]