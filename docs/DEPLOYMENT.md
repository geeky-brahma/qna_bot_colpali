# Deployment Guide

## Prerequisites

- GCP account with billing enabled
- Google OAuth credentials (see setup below)
- Pinecone account
- Local environment: Node.js 18+, Python 3.10+, Git

## 1. GCP Project Setup

```bash
# Create a new GCP project
gcloud projects create rag-production --name="RAG Production"
gcloud config set project rag-production

# Enable required APIs
gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  storage-api.googleapis.com \
  artifactregistry.googleapis.com \
  compute.googleapis.com

# Create service account
gcloud iam service-accounts create rag-backend \
  --display-name="RAG Backend Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding rag-production \
  --member="serviceAccount:rag-backend@rag-production.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

gcloud projects add-iam-policy-binding rag-production \
  --member="serviceAccount:rag-backend@rag-production.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.invoker"
```

## 2. Cloud Storage Setup

```bash
# Create bucket for PDFs
gsutil mb gs://rag-documents

# Upload sample PDFs
gsutil cp documents/mathematics.pdf gs://rag-documents/documents/
gsutil cp documents/science.pdf gs://rag-documents/documents/
gsutil cp documents/history.pdf gs://rag-documents/documents/
gsutil cp documents/literature.pdf gs://rag-documents/documents/

# Set appropriate permissions
gsutil iam ch serviceAccount:rag-backend@rag-production.iam.gserviceaccount.com:objectViewer gs://rag-documents
```

## 3. Pinecone Setup

```bash
# Create Pinecone project (via dashboard)
# https://app.pinecone.io/

# Create index
pinecone-cli create rag-queries --dimension 768 --metric cosine --serverless gcp

# Note your API key and environment
# Set in .env files:
# PINECONE_API_KEY=<your-api-key>
# PINECONE_ENVIRONMENT=us-west1-gcp
```

## 4. Deploy GCP Cloud Function (Inference Backend)

```bash
cd inference-backend

# Create .env file
cp .env.example .env
# Edit .env with your GCP project ID and bucket name

# Deploy function
gcloud functions deploy colpali_query \
  --runtime python312 \
  --trigger-http \
  --allow-unauthenticated \
  --memory 4GB \
  --timeout 300s \
  --region us-central1 \
  --source . \
  --entry-point colpali_query \
  --service-account rag-backend@rag-production.iam.gserviceaccount.com

# Get function URL
gcloud functions describe colpali_query --region us-central1
# Note the trigger URL
```

## 5. Deploy API Backend to Cloud Run

```bash
cd api-backend

# Create .env file
cp .env.example .env
# Edit .env with:
# - PINECONE_API_KEY
# - INFERENCE_FUNCTION_URL (from step 4)
# - INFERENCE_FUNCTION_KEY (if protected)

# Build Docker image
docker build -t api-backend:latest .

# Tag for GCR
docker tag api-backend:latest gcr.io/rag-production/api-backend:latest

# Push to Google Container Registry
docker push gcr.io/rag-production/api-backend:latest

# Deploy to Cloud Run
gcloud run deploy rag-api \
  --image gcr.io/rag-production/api-backend:latest \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 120 \
  --allow-unauthenticated

# Get service URL
gcloud run services describe rag-api --region us-central1 --format='value(status.url)'
```

### Create Dockerfile for API Backend

```dockerfile
# api-backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 6. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to: APIs & Services → Credentials
3. Click: Create Credentials → OAuth 2.0 Client ID
4. Application type: Web application
5. Authorized JavaScript origins:
   - `http://localhost:3000` (dev)
   - `https://your-domain.web.app` (production)
6. Authorized redirect URIs:
   - `http://localhost:3000/api/auth/callback/google`
   - `https://your-domain.web.app/api/auth/callback/google`
7. Copy Client ID and Secret

## 7. Deploy Frontend

### Option A: Vercel (Recommended)

```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard:
# NEXTAUTH_URL=https://your-domain.web.app
# NEXTAUTH_SECRET=<generate-with: openssl rand -base64 32>
# GOOGLE_CLIENT_ID=<from-step-6>
# GOOGLE_CLIENT_SECRET=<from-step-6>
# NEXT_PUBLIC_API_URL=<from-step-5>
```

### Option B: Firebase Hosting

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Build
cd frontend
npm run build

# Deploy
firebase deploy
```

## 8. Configuration Summary

### Frontend (.env.local)
```
NEXTAUTH_URL=https://your-domain.web.app
NEXTAUTH_SECRET=<random-32-char-secret>
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
NEXT_PUBLIC_API_URL=https://rag-api-xxx.a.run.app
```

### API Backend (.env)
```
PINECONE_API_KEY=<your-pinecone-api-key>
PINECONE_INDEX_NAME=rag-queries
INFERENCE_FUNCTION_URL=https://us-central1-rag-production.cloudfunctions.net/colpali_query
DEBUG=False
```

### GCP Cloud Function (app.yaml)
```
runtime: python312
entrypoint: colpali_query
env: cloud_function
secretEnvironmentVariables:
  - name: GCP_PROJECT_ID
    key: gcp-project-id
  - name: GCP_BUCKET_NAME
    key: rag-documents
```

## 9. Testing

### Health Checks

```bash
# API health
curl https://rag-api-xxx.a.run.app/health

# Function health
curl -X GET https://us-central1-rag-production.cloudfunctions.net/health
```

### Load Test

```bash
# Using Apache Bench
ab -n 100 -c 10 \
  -H "Content-Type: application/json" \
  -p query.json \
  https://rag-api-xxx.a.run.app/api/query

# query.json
{
  "query": "What is photosynthesis?",
  "subject": "Science",
  "userEmail": "test@example.com"
}
```

## 10. Monitoring & Logging

### Cloud Logging
```bash
# View API logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=rag-api"

# View function logs
gcloud functions logs read colpali_query --limit 50
```

### Set up Alerts
- Go to Cloud Monitoring
- Create alert policies for:
  - Cloud Function error rate > 5%
  - Cloud Run latency > 15s
  - Pinecone connection errors

## 11. Cost Optimization

- **GCP Cloud Functions**: ~$0.40/million invocations + compute time
- **Cloud Run**: ~$0.00001667/vCPU-second (2 vCPU active time)
- **Pinecone**: Starter at ~$0.04/pod month
- **Cloud Storage**: ~$0.020/GB stored

Estimated cost for 100-200 users/day: ~$50-100/month

## Troubleshooting

### Cold Start Latency
- Use Cloud Function warming (scheduled function)
- Pre-load models in global scope

### Memory Issues
- Scale up Cloud Function memory (4GB recommended)
- Use model quantization if available

### Cache Misses
- Lower `similarity_threshold` in API config
- Monitor cache statistics in Pinecone dashboard

## Rollback Plan

```bash
# Rollback API
gcloud run deploy rag-api --image gcr.io/rag-production/api-backend:previous-tag

# Rollback function
gcloud functions deploy colpali_query --source gs://backup-bucket/previous-source
```

---

**Next Steps**: Monitor performance, collect metrics, and optimize based on real usage patterns.
