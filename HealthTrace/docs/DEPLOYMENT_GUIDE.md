# HealthTrace - Deployment Guide

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **Memory**: Minimum 8GB RAM (16GB recommended for production)
- **Storage**: Minimum 50GB free space (SSD recommended)
- **CPU**: 4+ cores recommended
- **Network**: Stable internet connection for external data sources

### Software Dependencies
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: For repository cloning
- **OpenSSL**: For SSL certificate generation

## Quick Start (Development)

### 1. Clone Repository
```bash
git clone <repository-url>
cd HealthTrace
```

### 2. Environment Configuration
Create environment files:

#### Backend Environment (.env)
```bash
# Create backend/.env file
cat > backend/.env << EOF
DATABASE_URL=postgresql://healthtrace:healthtrace_password@database:5432/healthtrace
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
REDIS_URL=redis://redis:6379
SECRET_KEY=your-development-secret-key-change-in-production
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
ISPRA_API_BASE_URL=https://indicatoriambientali.isprambiente.it/api
ARPA_CAMPANIA_API_BASE_URL=https://dati.arpacampania.it/api
ISTAT_API_BASE_URL=https://www.istat.it/api
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=104857600
MODELS_DIR=/app/models
EOF
```

#### Frontend Environment
```bash
# Create frontend/.env file
cat > frontend/.env << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_MAP_TILES_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
EOF
```

### 3. Start Services
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Initialize Database
```bash
# Run database migrations
docker-compose exec backend python -c "from app.core.database import init_db; init_db()"

# Create admin user
docker-compose exec backend python scripts/create_admin.py
```

### 5. Access Services
- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432 (healthtrace/healthtrace_password)

## Production Deployment

### 1. Server Preparation

#### Update System
```bash
sudo apt update && sudo apt upgrade -y
```

#### Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

### 2. SSL Configuration

#### Generate SSL Certificates
```bash
# Create SSL directory
mkdir -p deployment/ssl

# Option 1: Self-signed certificate (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout deployment/ssl/private.key \
    -out deployment/ssl/certificate.crt \
    -subj "/C=IT/ST=Campania/L=Naples/O=HealthTrace/CN=healthtrace.local"

# Option 2: Let's Encrypt (production)
# Install certbot first
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --standalone -d your-domain.com
# Copy certificates to deployment/ssl/
```

### 3. Production Environment Configuration

#### Update docker-compose.prod.yml
```yaml
version: '3.8'

services:
  database:
    image: timescale/timescaledb:latest-pg14
    environment:
      POSTGRES_DB: healthtrace
      POSTGRES_USER: healthtrace
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./deployment/backup:/backup
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://healthtrace:${DB_PASSWORD}@database:5432/healthtrace
      SECRET_KEY: ${SECRET_KEY}
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      REDIS_URL: redis://redis:6379
    depends_on:
      - database
      - kafka
      - redis
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    build: ./frontend
    environment:
      REACT_APP_API_URL: https://your-domain.com
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployment/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./deployment/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
```

#### Production Environment Variables
```bash
# Create .env.prod file
cat > .env.prod << EOF
DB_PASSWORD=your-secure-database-password
SECRET_KEY=your-very-secure-secret-key-at-least-32-characters
DOMAIN=your-domain.com
EMAIL=admin@your-domain.com
EOF
```

### 4. Nginx Configuration

#### Create nginx.prod.conf
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/certificate.crt;
        ssl_certificate_key /etc/nginx/ssl/private.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        
        # Security headers
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # API routes
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # File upload size limit
        client_max_body_size 100M;
    }
}
```

### 5. Database Initialization Script
```sql
-- deployment/init-db.sql
-- Create extensions
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create user roles
CREATE TYPE user_role AS ENUM ('mmg', 'pls', 'uosd', 'uoc_epidemiology', 'admin');
CREATE TYPE gender AS ENUM ('male', 'female', 'other');
CREATE TYPE patient_status AS ENUM ('active', 'recovered', 'deceased');

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE healthtrace TO healthtrace;
```

### 6. Backup Configuration

#### Create Backup Script
```bash
#!/bin/bash
# deployment/backup.sh

BACKUP_DIR="/opt/healthtrace/backups"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="healthtrace_db"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
docker exec $CONTAINER_NAME pg_dump -U healthtrace healthtrace > $BACKUP_DIR/db_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 30 days of backups
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_backup_$DATE.sql.gz"
```

#### Setup Cron Job for Daily Backups
```bash
# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/healthtrace/deployment/backup.sh >> /var/log/healthtrace_backup.log 2>&1") | crontab -
```

### 7. Monitoring Setup

#### Health Check Script
```bash
#!/bin/bash
# deployment/health-check.sh

API_URL="https://your-domain.com/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "$(date): HealthTrace API is healthy"
else
    echo "$(date): HealthTrace API is unhealthy (HTTP $RESPONSE)"
    # Send alert notification here
fi
```

#### Log Rotation
```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/healthtrace << EOF
/var/log/healthtrace/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF
```

### 8. Production Deployment Steps

```bash
# 1. Clone repository
git clone <repository-url> /opt/healthtrace
cd /opt/healthtrace

# 2. Set up environment
cp .env.prod .env
chmod 600 .env

# 3. Create necessary directories
mkdir -p deployment/ssl
mkdir -p backups
mkdir -p logs

# 4. Set up SSL certificates (Let's Encrypt example)
sudo certbot certonly --standalone -d your-domain.com
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem deployment/ssl/certificate.crt
cp /etc/letsencrypt/live/your-domain.com/privkey.pem deployment/ssl/private.key

# 5. Start services
docker-compose -f docker-compose.prod.yml up -d

# 6. Initialize database
docker-compose exec backend python -c "from app.core.database import init_db; init_db()"

# 7. Create admin user
docker-compose exec backend python scripts/create_admin.py

# 8. Set up monitoring
chmod +x deployment/health-check.sh
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/healthtrace/deployment/health-check.sh >> /var/log/healthtrace_health.log 2>&1") | crontab -

# 9. Verify deployment
curl -k https://your-domain.com/health
```

## Maintenance

### Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Run database migrations if needed
docker-compose exec backend alembic upgrade head
```

### Monitoring Commands
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check resource usage
docker stats

# Database connection test
docker-compose exec database psql -U healthtrace -d healthtrace -c "SELECT version();"
```

### Troubleshooting

#### Common Issues

**Services not starting:**
```bash
# Check logs
docker-compose logs service-name

# Check disk space
df -h

# Check memory usage
free -m
```

**Database connection issues:**
```bash
# Test database connectivity
docker-compose exec backend python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"

# Check database logs
docker-compose logs database
```

**SSL certificate issues:**
```bash
# Check certificate validity
openssl x509 -in deployment/ssl/certificate.crt -text -noout

# Renew Let's Encrypt certificate
sudo certbot renew
```

### Security Considerations

1. **Regular Updates**: Keep all components updated
2. **Strong Passwords**: Use complex passwords for all accounts
3. **SSL/TLS**: Always use HTTPS in production
4. **Firewall**: Configure proper firewall rules
5. **Backups**: Regular database and application backups
6. **Monitoring**: Set up comprehensive monitoring and alerting
7. **Access Control**: Implement proper user access controls
8. **Audit Logs**: Enable and monitor audit logs

### Performance Optimization

1. **Database Indexing**: Ensure proper database indexes
2. **Caching**: Implement Redis caching for frequently accessed data
3. **CDN**: Use CDN for static assets
4. **Compression**: Enable gzip compression in Nginx
5. **Connection Pooling**: Configure database connection pooling
6. **Resource Limits**: Set appropriate Docker resource limits

This deployment guide provides comprehensive instructions for both development and production deployments of the HealthTrace system.
