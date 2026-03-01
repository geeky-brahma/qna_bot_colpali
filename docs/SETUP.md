# Local Development Setup

## Prerequisites

- Python 3.10+ (for backends)
- Node.js 18+ (for frontend)
- Git
- Docker (optional, for containerization)

## 1. Clone and Navigate

```bash
cd rag-production
```

## 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Edit .env.local
# NEXTAUTH_SECRET can be generated with:
openssl rand -base64 32

# Google OAuth:
# 1. Go to https://console.cloud.google.com/
# 2. Create OAuth 2.0 credentials
# 3. Add http://localhost:3000 to authorized origins
# 4. Add http://localhost:3000/api/auth/callback/google to redirect URIs

# Development server
npm run dev
# Visit http://localhost:3000
```

**Frontend Stack:**
- Next.js 14 with App Router
- React 18 with TypeScript
- NextAuth for authentication
- Tailwind CSS for styling
- Axios for API calls

## 3. API Backend Setup

```bash
cd api-backend

# Create virtual environment
python -m venv venv

# Activate
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with:
# - PINECONE_API_KEY (get from https://app.pinecone.io/)
# - INFERENCE_FUNCTION_URL (local: http://localhost:8080)

# For local Pinecone development (optional):
# You can skip this and mock responses

# Run development server
python main.py
# API will be at http://localhost:8000
# Docs at http://localhost:8000/docs
```

**Backend Stack:**
- FastAPI with Uvicorn
- Pinecone for vector caching
- Async/await for concurrency
- Pydantic for validation

## 4. GCP Inference Function Setup (Local Testing)

```bash
cd inference-backend

# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Google Functions Framework
pip install functions-framework

# Create .env file
cp .env.example .env

# For local testing without GCP:
# You'll need to mock GCS and run simplified version

# Run locally with Functions Framework
functions-framework --target colpali_query --debug --port 8080
# Function will be at http://localhost:8080/
```

## 5. End-to-End Testing Locally

```bash
# Terminal 1 - Inference Function
cd inference-backend
source venv/bin/activate
functions-framework --target colpali_query --debug --port 8080

# Terminal 2 - API Backend
cd api-backend
source venv/bin/activate
python main.py

# Terminal 3 - Frontend
cd frontend
npm run dev

# Terminal 4 - Test
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is photosynthesis?",
    "subject": "Science",
    "userEmail": "dev@test.com"
  }'
```

## Development Workflow

### Making Changes

**Frontend:**
```bash
# Hot reload on save
npm run dev

# Build for production
npm run build
npm start
```

**API Backend:**
```bash
# Auto-reload with --reload flag
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Inference Function:**
```bash
# Auto-reload with --debug flag
functions-framework --target colpali_query --debug --port 8080
```

### Testing

**Frontend:**
```bash
# Add tests in __tests__ directories
npm test
```

**Backend:**
```bash
# API tests
pytest api-backend/tests/

# Inference tests
pytest inference-backend/tests/
```

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :<port>
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :<port>
kill -9 <PID>
```

### Pinecone Connection Issues
- Verify API key in .env
- Check internet connection
- Ensure index name matches

### Model Loading Issues (Inference)
```bash
# Download models manually
python -c "from transformers import AutoModel; AutoModel.from_pretrained('vidore/colpali-v1.3')"
```

### NextAuth Issues
- Ensure NEXTAUTH_SECRET is set and >= 32 chars
- Check Google OAuth credentials
- Clear browser cookies

### GCS/GCP Issues (Local)
- Install GCP CLI: `gcloud init`
- Authenticate: `gcloud auth application-default login`
- Create test bucket for development

## Database/Cache Setup

### Using Pinecone Free Tier
1. Go to https://app.pinecone.io/
2. Create account
3. Create index:
   - Name: `rag-queries`
   - Dimension: `768`
   - Metric: `cosine`
   - Serverless (optional)
4. Copy API key to .env

### Mocking Cache for Development
In `api-backend/cache.py`, you can mock Pinecone:

```python
# For testing without real Pinecone
class MockCache:
    def __init__(self):
        self.storage = {}
    
    async def get_similar_query(self, embedding, subject, threshold=0.95):
        # Return None to always bypass cache
        return None
    
    async def store_result(self, **kwargs):
        # Store in memory
        pass
```

## Environment Variables

### Frontend (.env.local)
```
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<generated-secret>
GOOGLE_CLIENT_ID=<your-client-id>
GOOGLE_CLIENT_SECRET=<your-client-secret>
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### API Backend (.env)
```
PINECONE_API_KEY=<your-key>
PINECONE_INDEX_NAME=rag-queries
INFERENCE_FUNCTION_URL=http://localhost:8080
DEBUG=True
```

### Inference Backend (.env)
```
GCP_PROJECT_ID=test-project
GCP_BUCKET_NAME=test-bucket
```

## Database Initialization

For first-time setup with real data:

```bash
# Create Pinecone index
pinecone-cli create rag-queries --dimension 768

# Upload PDFs to your storage
# Place sample PDFs in documents/ folder:
# - documents/mathematics.pdf
# - documents/science.pdf
# - documents/history.pdf
# - documents/literature.pdf
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: your feature description"

# Push and create PR
git push origin feature/your-feature
```

## VS Code Extensions (Recommended)

- Python (Microsoft)
- Pylance (Microsoft)
- ESLint (Microsoft)
- Prettier (Code Formatter)
- Thunder Client (API testing)
- REST Client (API testing)

## Performance Tips

1. **GPU Usage**: Inference function uses GPU if available (much faster)
2. **Model Caching**: Models load once and reuse
3. **Query Batching**: Process multiple queries efficiently
4. **Vector Cache**: Pinecone caches embeddings for 24 hours

## Next Steps

1. Set up local environment (10-15 mins)
2. Run all three services locally
3. Test end-to-end flow through web UI
4. Prepare for GCP deployment
5. Configure CI/CD pipeline

---

Need help? See ARCHITECTURE.md and DEPLOYMENT.md
