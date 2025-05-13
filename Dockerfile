
# Usa una imagen base ligera de Python
FROM python:3.9-slim

# --- 1. Instala dependencias del sistema ---
RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*


# --- 2. Instala Tailscale ---
RUN curl -fsSL https://tailscale.com/install.sh | sh

# --- 3. Configura el entorno ---
WORKDIR /app

# Copia los requirements e instala dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- 4. Copia los archivos de la app ---
COPY . .


# --- 6. Variables de entorno ---
ENV DB_HOST=""
ENV DB_PORT="5432"
ENV DB_NAME=""
ENV DB_USER=""
ENV DB_PASSWORD=""
ENV TAILSCALE_AUTHKEY=""

