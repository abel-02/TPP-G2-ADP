#!/bin/sh

# 1. Iniciar el daemon de Tailscale en modo ephemeral (óptimo para contenedores)
tailscaled --state=mem: --socket=/var/run/tailscale/tailscaled.sock &

# 2. Esperar a que el daemon esté listo (más robusto que solo 'sleep 2')
while [ ! -S /var/run/tailscale/tailscaled.sock ]; do
    sleep 1
done

# 3. Autenticar con Tailscale (usando clave de API)
tailscale up \
  --authkey=${TAILSCALE_AUTHKEY} \
  --hostname=railway-app \
  --accept-routes=true \
  --advertise-exit-node=false

# 4. Verificar conexión y mostrar estado
tailscale status
tailscale ping ${DB_HOST}  # Verifica que puedes alcanzar la IP de tu DB

python main.py