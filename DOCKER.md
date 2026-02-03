# Docker Deployment Guide

This guide covers running Vouch using Docker and Docker Compose.

## Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum (for all services)
- 20GB disk space (for Ollama models)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vouch
   ```

2. **Build and start all services**
   ```bash
   make install
   ```

   Or manually:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

3. **Wait for initialization**

   The first time you run the application, Ollama needs to download the llama3.2-vision model (~4.7GB). This can take 5-15 minutes depending on your internet connection.

   Monitor progress:
   ```bash
   make logs-ollama
   # or
   docker-compose logs -f ollama-init
   ```

4. **Access the application**

   Once all services are healthy:
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Service Architecture

The Docker Compose setup includes:

| Service | Port | Purpose |
|---------|------|---------|
| vouch | 8000 | Main FastAPI application |
| mongodb | 27017 | Document database |
| elasticsearch | 9200, 9300 | Search engine |
| ollama | 11434 | AI vision model service |

## Common Commands

### Using Make (Recommended)

```bash
# View all available commands
make help

# Start services
make up

# Stop services
make down

# View logs
make logs

# Check service status
make status

# Check service health
make health

# Restart services
make restart

# Clean up everything
make clean
```

### Using Docker Compose Directly

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart a service
docker-compose restart vouch

# Rebuild and restart
docker-compose up -d --build
```

## Development Mode

For development with hot reloading:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This mounts your local source code into the container, so changes are reflected immediately.

## Volumes

Data is persisted in Docker volumes:

- `vouch-mongodb-data` - MongoDB database
- `vouch-elasticsearch-data` - Elasticsearch indices
- `vouch-ollama-data` - Ollama models (~5GB)
- `vouch-uploads-data` - Temporary uploaded files

### Backup

**Backup MongoDB:**
```bash
make backup-mongodb
# or
docker-compose exec mongodb mongodump --db=vouch --archive > backup.archive
```

**Restore MongoDB:**
```bash
make restore-mongodb FILE=backups/mongodb-backup-xxx.archive
# or
docker-compose exec -T mongodb mongorestore --db=vouch --archive < backup.archive
```

**Backup Ollama models:**
```bash
docker run --rm -v vouch-ollama-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/ollama-models.tar.gz -C /data .
```

## Troubleshooting

### Services not starting

1. **Check Docker resources:**
   ```bash
   docker system df
   docker system info
   ```

2. **Check service logs:**
   ```bash
   make logs
   # or
   docker-compose logs <service-name>
   ```

3. **Verify health status:**
   ```bash
   make health
   ```

### Ollama model not loading

The llama3.2-vision model is large (~4.7GB). If initialization fails:

1. **Check Ollama logs:**
   ```bash
   docker-compose logs ollama-init
   ```

2. **Manually pull the model:**
   ```bash
   docker-compose exec ollama ollama pull llama3.2-vision
   ```

3. **Verify model is available:**
   ```bash
   docker-compose exec ollama ollama list
   ```

### MongoDB connection issues

1. **Check MongoDB health:**
   ```bash
   docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
   ```

2. **View MongoDB logs:**
   ```bash
   docker-compose logs mongodb
   ```

### Elasticsearch connection issues

1. **Check Elasticsearch health:**
   ```bash
   curl http://localhost:9200/_cluster/health
   ```

2. **View Elasticsearch logs:**
   ```bash
   docker-compose logs elasticsearch
   ```

3. **Increase memory limits if needed** (edit docker-compose.yml):
   ```yaml
   ES_JAVA_OPTS: "-Xms1g -Xmx1g"
   ```

### Application errors

1. **Check application logs:**
   ```bash
   make logs-app
   ```

2. **Verify all services are healthy:**
   ```bash
   make health
   ```

3. **Restart the application:**
   ```bash
   docker-compose restart vouch
   ```

### Port conflicts

If ports 8000, 27017, 9200, or 11434 are already in use:

1. Edit `docker-compose.yml` and change the port mappings:
   ```yaml
   ports:
     - "8080:8000"  # Change host port
   ```

2. Update application URL accordingly

### Out of disk space

1. **Check disk usage:**
   ```bash
   docker system df -v
   ```

2. **Clean up unused resources:**
   ```bash
   make clean
   # or
   docker system prune -a --volumes
   ```

## Performance Tuning

### Elasticsearch Memory

Default: 512MB. For production, increase in `docker-compose.yml`:

```yaml
environment:
  - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
```

### MongoDB

For better performance, use a dedicated volume:

```yaml
volumes:
  - /path/to/mongodb/data:/data/db
```

### Ollama

Ollama benefits from GPU access. To use GPU:

1. Install nvidia-docker2
2. Add to ollama service:
   ```yaml
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: 1
             capabilities: [gpu]
   ```

## Production Deployment

For production use:

1. **Use environment file:**
   ```bash
   cp .env.docker .env
   # Edit .env with production values
   docker-compose --env-file .env up -d
   ```

2. **Enable authentication:**
   - Add MongoDB authentication
   - Add Elasticsearch security
   - Use reverse proxy (nginx/traefik)
   - Add HTTPS/TLS

3. **Resource limits:**
   Add resource limits in docker-compose.yml:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 4G
       reservations:
         cpus: '1'
         memory: 2G
   ```

4. **Logging:**
   Configure log rotation:
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

5. **Monitoring:**
   - Add health check endpoints
   - Use Prometheus/Grafana for metrics
   - Configure alerts

## Updating

To update to the latest version:

```bash
git pull
make update
```

Or manually:
```bash
docker-compose pull
docker-compose build --no-cache
docker-compose up -d
```

## Cleanup

**Remove all containers and volumes:**
```bash
make clean
```

**Remove everything including images:**
```bash
make clean-all
```

## Security Considerations

1. **Network Isolation:** Services communicate on isolated Docker network
2. **Non-root User:** Application runs as non-root user (uid 1000)
3. **Read-only Mounts:** Configuration files mounted read-only
4. **Resource Limits:** Set CPU and memory limits in production

## FAQ

**Q: How much disk space do I need?**
A: Minimum 20GB. Ollama models (~5GB) + Elasticsearch indices + MongoDB data.

**Q: Can I use an external MongoDB/Elasticsearch?**
A: Yes. Comment out services in docker-compose.yml and update connection URLs in .env

**Q: How do I update the Ollama model?**
A: `docker-compose exec ollama ollama pull llama3.2-vision`

**Q: Can I run this on ARM/M1 Mac?**
A: Yes. Docker images support multi-architecture (amd64, arm64).

**Q: How do I scale the application?**
A: Use `docker-compose up --scale vouch=3` and add a load balancer.

## Support

For issues:
1. Check logs: `make logs`
2. Check health: `make health`
3. Review this guide
4. Open an issue on GitHub
