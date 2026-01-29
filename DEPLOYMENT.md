# LocateMeAI - AWS EC2 Deployment Guide

This guide walks you through deploying the LocateMeAI application to an AWS EC2 instance using Docker.

> **Note:** For automated CI/CD deployments using GitHub Actions, see [CI-CD-GUIDE.md](CI-CD-GUIDE.md).

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

or

```config ssh host via VSCode
Host your-ec2-public-ip
  HostName your-ec2-public-ip
  IdentityFile C:\Users\your-key.pem
  User ubuntu
```

## 3. Install Docker and Docker Compose

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies for Python packages
sudo apt-get install -y portaudio19-dev python3-pyaudio

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

### Option A: Automated CI/CD Deployment (Recommended)

For automated deployments with GitHub Actions:
1. See [CI-CD-GUIDE.md](CI-CD-GUIDE.md) for complete setup instructions
2. Configure GitHub Secrets (EC2 credentials, SSH keys)
3. Push to `main` branch or trigger manual deployment from GitHub Actions UI
4. Pipeline automatically runs tests, builds, and deploys to EC2

Benefits:
- Automated testing and building
- Zero-downtime deployments
- Automatic rollback on failures
- Slack notifications (optional)

For detailed CI/CD setup, troubleshooting, and best practices, refer to [CI-CD-GUIDE.md](CI-CD-GUIDE.md).

### Option B: Deploy from Git Repository

```bash
# Clone repository
git clone https://github.com/Kaderbv/LocateMeAI.git
cd LocateMeAI

# Build and start containers
docker compose up -d --build

# View logs
docker compose logs -f
```

### Option C: Deploy from Local Files

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

### Manual Deployment

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

### CI/CD Deployment

For automated deployments:
```bash
# Deploy via GitHub Actions
# 1. Push changes to main branch, or
# 2. Trigger manual workflow from GitHub Actions UI

# View deployment status
# Check GitHub Actions tab in your repository

# Rollback procedures
# See CI-CD-GUIDE.md for automated and manual rollback options
```

For more details on CI/CD workflows, rollback procedures, and deployment verification, see [CI-CD-GUIDE.md](CI-CD-GUIDE.md).

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

> **CI/CD Troubleshooting:** For pipeline failures, deployment timeouts, and GitHub Actions issues, see the [Troubleshooting section in CI-CD-GUIDE.md](CI-CD-GUIDE.md#troubleshooting).

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

### Automated Cost Optimization

Run the cost optimization script:
```bash
chmod +x scripts/cost-optimization.sh
sudo ./scripts/cost-optimization.sh
```

### Cost-Saving Strategies

#### 1. Right-Sizing Instances
**Current Recommendations**:
- **Development/Testing**: t3.medium or t3a.medium Spot Instances (up to 90% savings)
- **Production**: t3.large with Auto Scaling
- **ML-Heavy Workloads**: Consider g4dn.xlarge with Spot for batch processing

**Monthly Cost Comparison** (us-east-1 region):
| Instance Type | On-Demand | 1-Year Reserved | Spot |
|--------------|-----------|-----------------|------|
| t3.medium    | $30.37    | $18.98 (37% off) | ~$9.11 (70% off) |
| t3.large     | $60.74    | $37.96 (37% off) | ~$18.22 (70% off) |
| g4dn.xlarge  | $394.62   | $236.77 (40% off) | ~$118.39 (70% off) |

#### 2. Stop Instances When Not in Use
```bash
# Stop instance (keep EBS volumes, only pay for storage)
aws ec2 stop-instances --instance-ids i-xxxxx

# Start when needed
aws ec2 start-instances --instance-ids i-xxxxx

# Automate with Lambda function for scheduled start/stop
```

**Savings**: If running 8 hours/day, 5 days/week = **~70% cost reduction**

#### 3. Use Spot Instances for Development
```bash
# Request Spot Instance
aws ec2 request-spot-instances \
    --spot-price "0.05" \
    --instance-count 1 \
    --type "one-time" \
    --launch-specification file://specification.json

# Set up Spot Instance with persistent storage
# Attach EBS volume on instance startup
```

**Savings**: Up to **90% off On-Demand pricing**

#### 4. Storage Optimization

**EBS Volume Optimization**:
```bash
# Check volume usage
df -h

# Resize if needed (can only increase)
aws ec2 modify-volume --volume-id vol-xxxxx --size 40

# Switch to gp3 (cheaper than gp2)
aws ec2 modify-volume --volume-id vol-xxxxx --volume-type gp3
```

**S3 for Media Storage**:
```bash
# Install AWS CLI
sudo apt-get install awscli

# Sync uploads to S3
aws s3 sync ./backend/uploads s3://locatemeai-uploads/

# Update backend to use S3
# Modify backend/app/config.py to use boto3
```

**Storage Cost Comparison**:
- EBS gp3: $0.08/GB/month
- S3 Standard: $0.023/GB/month (65% cheaper)
- S3 Intelligent-Tiering: Automatic cost optimization

#### 5. Network Cost Optimization
- Use VPC endpoints for AWS services (free)
- Enable VPC Flow Logs only when debugging
- Use CloudFront for static content delivery
- Keep inter-service communication within same AZ

#### 6. Monitoring Cost Management

**Set Up Billing Alerts**:
```bash
# Create SNS topic for billing alerts
aws sns create-topic --name billing-alerts

# Subscribe email
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:ACCOUNT-ID:billing-alerts \
    --protocol email \
    --notification-endpoint your-email@example.com

# Create billing alarm
aws cloudwatch put-metric-alarm \
    --alarm-name monthly-bill-exceeds-50 \
    --alarm-description "Alert when bill exceeds $50" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --statistic Maximum \
    --period 21600 \
    --evaluation-periods 1 \
    --threshold 50 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=Currency,Value=USD
```

**Use AWS Cost Explorer**:
- Enable Cost Explorer in AWS Console
- Set up daily cost reports
- Create custom cost allocation tags
- Use Reserved Instance recommendations

#### 7. Container Image Optimization

Reduce storage and data transfer costs:
```dockerfile
# Use multi-stage builds
FROM python:3.11-slim as builder
# Build steps...

FROM python:3.11-slim
# Only copy necessary files
COPY --from=builder /app /app
```

```bash
# Clean up Docker resources regularly
docker system prune -af --volumes
docker image prune -af --filter "until=48h"
```

#### 8. Auto Scaling Configuration

Set up Auto Scaling to match demand:
```bash
# Create launch template
aws ec2 create-launch-template \
    --launch-template-name locatemeai-template \
    --version-description "Version 1" \
    --launch-template-data file://template-data.json

# Create Auto Scaling group
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name locatemeai-asg \
    --launch-template LaunchTemplateName=locatemeai-template \
    --min-size 1 \
    --max-size 3 \
    --desired-capacity 1 \
    --target-group-arns arn:aws:elasticloadbalancing:... \
    --health-check-type ELB \
    --health-check-grace-period 300
```

#### 9. CloudWatch Optimization

**Reduce CloudWatch Costs**:
```bash
# Use metric filters instead of detailed monitoring
# Standard monitoring (5-min): Free
# Detailed monitoring (1-min): $2.10/instance/month

# Set shorter log retention
aws logs put-retention-policy \
    --log-group-name /locatemeai/application \
    --retention-in-days 7  # Instead of default infinite
```

**CloudWatch Cost Breakdown**:
- Metrics: $0.30/metric/month (first 10k free)
- Logs: $0.50/GB ingested, $0.03/GB stored
- Alarms: $0.10/alarm/month (first 10 free)

**Recommendation**: Use Prometheus for detailed metrics, CloudWatch for critical alarms only.

#### 10. Reserved Instances & Savings Plans

For predictable workloads:

**Reserved Instances**:
- 1-year term: ~37% savings
- 3-year term: ~60% savings
- Payment options: All Upfront (highest discount), Partial, No Upfront

**Compute Savings Plans**:
- More flexible than RIs
- 1-year: ~30% savings
- 3-year: ~50% savings

```bash
# Check RI recommendations
aws ce get-reservation-purchase-recommendation \
    --service "Amazon EC2" \
    --lookback-period-in-days THIRTY_DAYS
```

### Cost Monitoring Dashboard

Monthly estimated costs for LocateMeAI:

**Minimum Configuration** (t3.medium, development):
- EC2: $30/month (On-Demand) or $9/month (Spot)
- EBS: $8/month (100GB gp3)
- Data Transfer: $5/month (modest usage)
- **Total: ~$43/month or $22/month (Spot)**

**Production Configuration** (t3.large, Auto Scaling):
- EC2: $60/month (On-Demand) or $38/month (Reserved)
- EBS: $12/month (150GB gp3)
- ALB: $16.20/month
- S3: $5/month (storage + requests)
- CloudWatch: $10/month
- Data Transfer: $15/month
- **Total: ~$118/month or $96/month (Reserved)**

**GPU Configuration** (g4dn.xlarge, ML workloads):
- EC2: $395/month (On-Demand) or $237/month (Reserved) or $118/month (Spot)
- **Recommendation**: Use Spot for batch processing

### Quick Wins Checklist

- [ ] Switch EBS from gp2 to gp3 (immediate 20% savings)
- [ ] Set up auto-shutdown for development instances (70% savings)
- [ ] Enable S3 lifecycle policies for old uploads
- [ ] Set CloudWatch log retention to 7 days
- [ ] Use Spot Instances for non-production
- [ ] Set up billing alerts
- [ ] Review and delete unused EBS snapshots
- [ ] Enable AWS Compute Optimizer recommendations
- [ ] Use t3a instances (AMD) for 10% additional savings
- [ ] Compress Docker images

### Monthly Cost Review Checklist

Use this checklist for monthly cost reviews:
- [ ] Review AWS Cost Explorer
- [ ] Check for idle resources
- [ ] Verify Auto Scaling effectiveness
- [ ] Review CloudWatch log usage
- [ ] Check for unattached EBS volumes
- [ ] Review Reserved Instance utilization
- [ ] Analyze data transfer patterns
- [ ] Check for oversized instances
- [ ] Review S3 storage classes
- [ ] Update cost allocation tags

## 14. Backup Strategy

```bash
# Backup uploads and outputs directories
tar -czf backup-$(date +%Y%m%d).tar.gz backend/uploads backend/outputs

# Copy to S3
aws s3 cp backup-*.tar.gz s3://your-backup-bucket/
```

## 15. Related Documentation

- **[CI-CD-GUIDE.md](CI-CD-GUIDE.md)** - Complete CI/CD pipeline setup, automated deployments, rollback procedures
- **[README.md](README.md)** - Project overview and local development setup
- **[docker-compose.yml](docker-compose.yml)** - Service configuration and orchestration

## Support

For issues, please check:
- Container logs: `docker compose logs`
- System logs: `journalctl -u docker`
- GitHub issues: https://github.com/Kaderbv/LocateMeAI/issues
