# Deployment Notes

## Local Stack

Use Docker Compose for the first integrated environment:

```bash
docker compose up --build
```

This brings up:

- backend API on `8000`
- AI service on `8100`
- dashboard on `5173`
- PostgreSQL on `5432`
- Redis on `6379`
- MQTT broker on `1883`

## Production Direction

- run backend and AI services behind a reverse proxy
- terminate TLS before public traffic reaches application containers
- use managed PostgreSQL where possible
- put MQTT behind authentication and network segmentation
- serve the dashboard through a hardened frontend hosting layer

