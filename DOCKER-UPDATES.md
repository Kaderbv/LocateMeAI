# Docker Configuration Updates for Fine-tuning Feature

## Changes Made

### 1. Backend Dockerfile
- **Added directory creation** for fine-tuning support:
  - `finetune_temp/` - Temporary storage during training
  - `runs/finetune/` - Persistent storage for trained models

### 2. Backend requirements.txt
- **Added PyYAML** - Required for creating YOLO dataset configuration files

### 3. docker-compose.yml
- **Added persistent volumes**:
  - `backend-models` - Stores fine-tuned YOLO models
  - `backend-data` - Stores active model configuration
  - `./backend/runs` - Mount for training results and model weights
- **Added volume comments** for clarity

### 4. Backend .dockerignore
- **Added exclusions**:
  - `finetune_temp/*` - Temporary training files
  - `active_model.txt` - Runtime configuration file

## Volume Structure

```
backend service:
├── ./backend/uploads       → /app/uploads         (bind mount - temporary)
├── ./backend/outputs       → /app/outputs         (bind mount - processed videos)
├── ./backend/runs          → /app/runs            (bind mount - training results)
├── backend-models          → /app/models          (volume - future use)
└── backend-data            → /app/data            (volume - stores active_model.txt)
```

**Active Model Configuration:**
- The `active_model.txt` file is stored in `/app/data/`
- This volume ensures the active model selection persists across container restarts
- Without this volume, you'd need to re-select your model after every restart

## Why These Changes?

### Persistent Storage
Fine-tuned models need to persist across container restarts. Using Docker volumes ensures:
- Models aren't lost when containers are recreated
- Training results are preserved
- Active model selection persists

### Build Optimization
.dockerignore exclusions prevent unnecessary files from being copied into the image:
- Reduces build time
- Smaller image size
- Avoids copying temporary training data

## Deployment Notes

### First Time Setup
When deploying with fine-tuning for the first time:

```bash
# Rebuild containers with new dependencies
docker-compose build

# Start services
docker-compose up -d
```

### Volume Management

**List volumes:**
```bash
docker volume ls
```

**Inspect a volume:**
```bash
docker volume inspect locatemeai_backend-models
```

**Backup trained models:**
```bash
docker run --rm -v locatemeai_backend-models:/source -v $(pwd):/backup alpine tar czf /backup/models-backup.tar.gz -C /source .
```

**Restore trained models:**
```bash
docker run --rm -v locatemeai_backend-models:/target -v $(pwd):/backup alpine tar xzf /backup/models-backup.tar.gz -C /target
```

### Cleanup

**Remove all data (including trained models):**
```bash
docker-compose down -v
```

**Remove only containers (keep models):**
```bash
docker-compose down
```

## Testing Docker Configuration

After updating, test the fine-tuning feature:

1. **Verify volumes are created:**
   ```bash
   docker-compose up -d
   docker volume ls | grep backend
   ```

2. **Check directory creation:**
   ```bash
   docker exec locatemeai-backend ls -la /app/
   ```
   Should show: `finetune_temp`, `runs`, `models`, `data`

3. **Test fine-tuning:**
   - Upload sample dataset
   - Train a model
   - Verify model persists after restart:
     ```bash
     docker-compose restart backend
     ```

4. **Check logs:**
   ```bash
   docker-compose logs backend | tail -50
   ```

## Environment Variables

No new environment variables required. Existing variables still apply:
- `OLLAMA_HOST`
- `OLLAMA_MODEL_NAME`
- `DEFAULT_YOLO_MODEL`

## Resource Considerations

### CPU Training
Current setup uses CPU-only PyTorch for compatibility. Training times:
- 5 images, 10 epochs: ~2-5 minutes
- 50 images, 50 epochs: ~15-30 minutes

### Memory Requirements
Recommended Docker resources:
- **Memory**: 4GB minimum, 8GB recommended
- **CPU**: 2 cores minimum, 4+ recommended
- **Disk**: 10GB for base + 5GB per trained model

Adjust in Docker Desktop → Settings → Resources

### GPU Support (Optional)

To enable GPU training, modify `backend/requirements.txt`:

```diff
- torch --index-url https://download.pytorch.org/whl/cpu
+ torch --index-url https://download.pytorch.org/whl/cu118
```

And add to `docker-compose.yml`:

```yaml
backend:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

## Troubleshooting

### Issue: Models not persisting
**Solution**: Check volume mounts:
```bash
docker inspect locatemeai-backend | grep -A 10 Mounts
```

### Issue: Permission errors
**Solution**: Fix container permissions:
```bash
docker exec -u root locatemeai-backend chown -R $(id -u):$(id -g) /app/runs /app/models /app/data
```

### Issue: Out of disk space
**Solution**: Clean old training runs:
```bash
docker exec locatemeai-backend rm -rf /app/runs/finetune/old_experiment_*
```

### Issue: Build fails
**Solution**: Clear cache and rebuild:
```bash
docker-compose build --no-cache backend
```

## Migration from Previous Version

If upgrading from a version without fine-tuning:

1. **Pull latest code:**
   ```bash
   git pull origin main
   ```

2. **Rebuild containers:**
   ```bash
   docker-compose build
   ```

3. **Create volumes:**
   ```bash
   docker volume create locatemeai_backend-models
   docker volume create locatemeai_backend-data
   ```

4. **Restart services:**
   ```bash
   docker-compose up -d
   ```

5. **Verify:**
   ```bash
   docker-compose ps
   docker logs locatemeai-backend
   ```

## Production Considerations

For production deployments:

1. **Use external volume drivers** for better backup/restore:
   ```yaml
   volumes:
     backend-models:
       driver: local
       driver_opts:
         type: nfs
         o: addr=10.0.0.1,rw
         device: ":/path/to/models"
   ```

2. **Set resource limits**:
   ```yaml
   backend:
     deploy:
       resources:
         limits:
           cpus: '4'
           memory: 8G
   ```

3. **Regular backups** of model volumes

4. **Monitor disk usage** for training runs

---

**Updated**: February 6, 2026  
**Docker Compose Version**: 3.8  
**Tested with**: Docker Engine 24.0+, Docker Compose 2.20+
