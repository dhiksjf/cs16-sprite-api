# Deployment Guide

Complete guide for deploying the CS 1.6 Sprite Generator API to various platforms.

## Table of Contents
- [Render.com](#rendercom)
- [Railway.app](#railwayapp)
- [Fly.io](#flyio)
- [Heroku](#heroku)
- [AWS (Elastic Beanstalk)](#aws-elastic-beanstalk)
- [Google Cloud Run](#google-cloud-run)
- [Digital Ocean App Platform](#digital-ocean-app-platform)

---

## Render.com

**Best for:** Simple deployment with persistent storage

### Steps:

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_REPO_URL
   git push -u origin main
   ```

2. **Create New Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure Service**
   - **Name**: `cs16-sprite-api`
   - **Environment**: `Docker`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Plan**: Free (or paid for better performance)

4. **Add Persistent Disk** (Optional but recommended)
   - Click "Add Disk"
   - **Name**: `sprite-outputs`
   - **Mount Path**: `/app/outputs`
   - **Size**: 1 GB (or more)

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)

6. **Get Your URL**
   - Your API will be at: `https://your-service-name.onrender.com`

### Alternative: Using render.yaml

Just push the included `render.yaml` file and Render will auto-configure:

```bash
git push origin main
```

---

## Railway.app

**Best for:** Quick deployment with auto-scaling

### Steps:

1. **Install Railway CLI** (optional)
   ```bash
   npm i -g @railway/cli
   ```

2. **Login**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   railway init
   ```

4. **Deploy**
   ```bash
   railway up
   ```

### Alternative: GitHub Integration

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Dockerfile and deploys

### Add Environment Variables (if needed)

```bash
railway variables set PORT=8000
```

### Get Your URL

```bash
railway domain
```

Or add a custom domain in the dashboard.

---

## Fly.io

**Best for:** Global edge deployment

### Steps:

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Launch App**
   ```bash
   fly launch
   ```
   
   Answer prompts:
   - **App name**: `cs16-sprite-api` (or your choice)
   - **Region**: Choose closest to users
   - **Setup Postgres**: No
   - **Deploy now**: Yes

4. **Add Persistent Volume** (optional)
   ```bash
   fly volumes create sprite_data --size 1 --region REGION
   ```

5. **Update fly.toml** to mount volume:
   ```toml
   [mounts]
     source = "sprite_data"
     destination = "/app/outputs"
   ```

6. **Deploy**
   ```bash
   fly deploy
   ```

7. **Get Your URL**
   ```bash
   fly info
   ```

---

## Heroku

**Best for:** Traditional PaaS deployment

### Steps:

1. **Install Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login**
   ```bash
   heroku login
   ```

3. **Create App**
   ```bash
   heroku create cs16-sprite-api
   ```

4. **Set Stack to Container**
   ```bash
   heroku stack:set container -a cs16-sprite-api
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **Scale Dyno**
   ```bash
   heroku ps:scale web=1
   ```

7. **Get URL**
   ```bash
   heroku open
   ```

### Note on Storage

Heroku has ephemeral storage. For persistent sprites, consider:
- AWS S3 integration
- External storage service
- Database storage for small files

---

## AWS (Elastic Beanstalk)

**Best for:** Enterprise deployment with AWS integration

### Steps:

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize**
   ```bash
   eb init -p docker cs16-sprite-api
   ```

3. **Create Environment**
   ```bash
   eb create cs16-sprite-env
   ```

4. **Deploy**
   ```bash
   eb deploy
   ```

5. **Open**
   ```bash
   eb open
   ```

### Add S3 for Storage

1. Create S3 bucket
2. Update code to use boto3 for file storage
3. Add IAM role with S3 access

---

## Google Cloud Run

**Best for:** Serverless container deployment

### Steps:

1. **Install gcloud CLI**
   Follow: https://cloud.google.com/sdk/docs/install

2. **Authenticate**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Build Container**
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/sprite-api
   ```

4. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy sprite-api \
     --image gcr.io/YOUR_PROJECT_ID/sprite-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8000
   ```

5. **Get URL**
   - Displayed after deployment
   - Or check: `gcloud run services describe sprite-api`

### Add Cloud Storage

1. Create Cloud Storage bucket
2. Update code to use `google-cloud-storage`
3. Set up service account with Storage permissions

---

## Digital Ocean App Platform

**Best for:** Simple Docker deployment with DO integration

### Steps:

1. **Create App** via web interface
   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - Click "Create App"

2. **Select Source**
   - Choose GitHub repository
   - Select branch: `main`

3. **Configure App**
   - **Type**: Web Service
   - **Dockerfile**: Auto-detected
   - **Port**: 8000
   - **Plan**: Basic ($5/mo) or Professional

4. **Add Environment Variables** (optional)
   ```
   PORT=8000
   ```

5. **Deploy**
   - Click "Create Resources"
   - Wait for deployment

6. **Get URL**
   - Shown in dashboard
   - Format: `https://sprite-api-xxxxx.ondigitalocean.app`

### Add Spaces for Storage

1. Create DO Space (S3-compatible)
2. Update code to use boto3 with Spaces endpoint
3. Configure access keys

---

## Environment Variables

Common environment variables for all platforms:

```bash
# Server
PORT=8000
HOST=0.0.0.0

# Directories (adjust based on platform)
OUTPUT_DIR=/app/outputs
TEMP_DIR=/app/temp

# Optional: Enable debug mode
DEBUG=false
```

---

## Performance Tips

### 1. Resource Allocation
- **RAM**: Minimum 512MB, recommended 1GB+
- **CPU**: 1 vCPU minimum, 2+ for video processing
- **Disk**: 1GB+ for persistent storage

### 2. Optimization
- Use persistent storage for outputs
- Implement automatic cleanup of old files
- Add rate limiting for production
- Enable GZIP compression
- Use CDN for sprite downloads

### 3. Scaling
- Horizontal: Add more instances for load balancing
- Vertical: Increase RAM/CPU for video processing
- Queue: Add job queue (Redis/Celery) for heavy tasks

---

## Monitoring

### Health Checks
All platforms support health checks at:
```
GET /health
```

### Logs
View logs on each platform:

**Render**: Dashboard → Logs
**Railway**: `railway logs`
**Fly.io**: `fly logs`
**Heroku**: `heroku logs --tail`

### Metrics
Monitor:
- Response times
- Error rates
- Memory usage
- Disk usage
- Request count

---

## Security

### 1. Rate Limiting
Add to production:
```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
```

### 2. File Size Limits
Configure in code:
```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

### 3. CORS
Already configured, but restrict origins in production:
```python
allow_origins=["https://yourdomain.com"]
```

### 4. API Keys (optional)
Add authentication for production use

---

## Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Ensure all dependencies in requirements.txt
- Verify Python version compatibility

### Out of Memory
- Increase instance size
- Optimize image processing
- Add video frame limits

### Slow Performance
- Use faster instance tier
- Add caching
- Optimize image operations
- Limit video FPS/frames

---

## Cost Estimates

### Free Tiers
- **Render**: 750 hours/month free
- **Railway**: $5 credit/month
- **Fly.io**: Limited free tier
- **Heroku**: 550 dyno hours/month (with credit card)

### Paid (Monthly)
- **Render**: $7+ (Starter)
- **Railway**: Pay-as-you-go (~$5-20)
- **Fly.io**: ~$5-15
- **Heroku**: $7+ (Hobby)
- **DO App Platform**: $5+ (Basic)
- **Cloud Run**: Pay per request (~$5-20)

---

## Next Steps

After deployment:
1. Test all endpoints
2. Monitor performance
3. Set up error tracking (Sentry)
4. Configure backups
5. Add custom domain
6. Implement authentication (if needed)
7. Set up CI/CD pipeline
8. Add monitoring/alerting
