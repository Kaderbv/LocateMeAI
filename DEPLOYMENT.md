# LocateMeAI - AWS EC2 Deployment Guide

This guide walks you through deploying the LocateMeAI application to an AWS EC2 instance using Docker.

## Prerequisites

- AWS Account with EC2 access
- SSH key pair for EC2 instance
- Docker and Docker Compose knowledge

## 1. Launch EC2 Instance

### Instance Specifications
- **AMI**: Ubuntu Server 22.04 LTS
- **Instance Type**: t3.large or larger (recommended for ML workloads)
  - Minimum: t3.medium (2 vCPUs, 4GB RAM)
  - Recommended: t3.large (2 vCPUs, 8GB RAM) or g4dn.xlarge (for GPU support)
- **Storage**: 30GB+ EBS volume
- **Security Group Rules**:
  - SSH (22) - Your IP only
  - HTTP (80) - Anywhere (0.0.0.0/0)
  - Custom TCP (8000) - Anywhere (for backend API)
  - Custom TCP (8501) - Anywhere (for frontend UI)
  - Custom TCP (11434) - Localhost only (for Ollama)

## 2. Connect to EC2 Instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

## 3. Install Docker and Docker Compose

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

## 4. Install Ollama (for LLM support)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama

# Pull the llava model
ollama pull llava

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

## 5. Deploy Application

### Option A: Deploy from Git Repository

```bash
# Clone repository
git clone https://github.com/Kaderbv/LocateMeAI.git
cd LocateMeAI

# Build and start containers
docker compose up -d --build

# View logs
docker compose logs -f
```

### Option B: Deploy from Local Files

```bash
# From your local machine, copy files to EC2
scp -i your-key.pem -r LocateMeAI ubuntu@your-ec2-public-ip:~/

# On EC2 instance
cd LocateMeAI
docker compose up -d --build
```

## 6. Verify Deployment

```bash
# Check container status
docker compose ps

# Check backend health
curl http://localhost:8000/

# Check logs
docker compose logs backend
docker compose logs frontend
```

## 7. Access Application

- **Frontend (Streamlit)**: http://your-ec2-public-ip:8501
- **Backend API**: http://your-ec2-public-ip:8000
- **API Docs**: http://your-ec2-public-ip:8000/docs

## 8. Optional: Setup Nginx Reverse Proxy

For production, use Nginx as a reverse proxy:

```bash
# Install Nginx
sudo apt-get install -y nginx

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/locatemeai <<EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or EC2 IP

    # Frontend
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/locatemeai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 9. Management Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Restart services
docker compose restart

# View logs
docker compose logs -f [service_name]

# Update application
git pull origin main
docker compose down
docker compose up -d --build

# Clean up old images
docker system prune -a
```

## 10. Monitoring and Maintenance

```bash
# Monitor resource usage
docker stats

# Check disk space
df -h

# View application logs
docker compose logs --tail=100 -f

# Restart specific service
docker compose restart backend
```

## 11. Troubleshooting

### Backend not starting
```bash
docker compose logs backend
# Check if port 8000 is available
sudo netstat -tulpn | grep 8000
```

### Frontend can't connect to backend
- Ensure both containers are on the same network
- Check backend health: `curl http://localhost:8000/`
- Verify environment variables in docker-compose.yml

### Ollama connection issues
```bash
# Check Ollama status
sudo systemctl status ollama
# Restart Ollama
sudo systemctl restart ollama
# Test connection
curl http://localhost:11434/api/tags
```

### Out of memory
- Upgrade to larger instance type
- Add swap space:
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 12. Security Best Practices

1. **Restrict Security Group**: Only allow necessary ports
2. **Use HTTPS**: Install SSL certificate with Let's Encrypt
3. **Regular Updates**: Keep system and containers updated
4. **Firewall**: Configure UFW firewall
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```
5. **Environment Variables**: Store sensitive data in .env files (not in git)

## 13. Cost Optimization

- Use Auto Scaling for variable load
- Stop instances when not in use
- Use Spot Instances for development
- Monitor with AWS CloudWatch
- Set up billing alerts

## 14. Backup Strategy

```bash
# Backup uploads and outputs directories
tar -czf backup-$(date +%Y%m%d).tar.gz backend/uploads backend/outputs

# Copy to S3
aws s3 cp backup-*.tar.gz s3://your-backup-bucket/
```

## Support

For issues, please check:
- Container logs: `docker compose logs`
- System logs: `journalctl -u docker`
- GitHub issues: https://github.com/Kaderbv/LocateMeAI/issues
