# Quick Reference Guide

## 🚀 Local Development Commands

### Windows
```bash
# Setup
setup.bat

# Terminal 1: Inference Function
cd inference-backend
venv\Scripts\activate.bat
functions-framework --target colpali_query --debug --port 8080

# Terminal 2: API Backend
cd api-backend
venv\Scripts\activate.bat
python main.py

# Terminal 3: Frontend
cd frontend
npm run dev
```

### macOS/Linux
```bash
# Setup
bash setup.sh

# Terminal 1: Inference Function
cd inference-backend
source venv/bin/activate
functions-framework --target colpali_query --debug --port 8080

# Terminal 2: API Backend
cd api-backend
source venv/bin/activate
python main.py

# Terminal 3: Frontend
cd frontend
npm run dev
```

## 🔧 Environment Variables

### Frontend (`frontend/.env.local`)
```
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<generate-with: openssl rand -base64 32>
GOOGLE_CLIENT_ID=<from Google OAuth>
GOOGLE_CLIENT_SECRET=<from Google OAuth>
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### API Backend (`api-backend/.env`)
```
PINECONE_API_KEY=<from Pinecone dashboard>
PINECONE_INDEX_NAME=rag-queries
INFERENCE_FUNCTION_URL=http://localhost:8080
DEBUG=True
```

### Inference Backend (`inference-backend/.env`)
```
GCP_PROJECT_ID=your-project-id
GCP_BUCKET_NAME=rag-documents
```

## 📋 Key URLs

| Service | Local | Production |
|---------|-------|-----------|
| Frontend | http://localhost:3000 | https://your-domain.web.app |
| API | http://localhost:8000 | https://rag-api-xxx.a.run.app |
| API Docs | http://localhost:8000/docs | https://rag-api-xxx.a.run.app/docs |
| Inference | http://localhost:8080 | https://us-central1-xxx.cloudfunctions.net/colpali_query |

## 🔍 Test Endpoints

### Test Frontend
```bash
curl http://localhost:3000
# Should redirect to login
```

### Test API
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query":"What is photosynthesis?",
    "subject":"Science",
    "userEmail":"test@example.com"
  }'

# Test health
curl http://localhost:8000/health
```

### Test Inference Function
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "query":"What is photosynthesis?",
    "subject":"Science"
  }'

# Test health
curl http://localhost:8080/health
```

## 📚 Documentation Map

| Document | Purpose | Time |
|----------|---------|------|
| README.md | Overview | 5 min |
| PROJECT_SUMMARY.md | This file | 5 min |
| SETUP.md | Local setup | 15 min |
| ARCHITECTURE.md | Design details | 20 min |
| API.md | API reference | 10 min |
| DEPLOYMENT.md | Production deployment | 1 hour |
| DEPLOYMENT_CHECKLIST.md | Pre-flight checklist | 2 hours |

## 🐛 Common Issues & Fixes

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :3000
kill -9 <PID>
```

### Python Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Node Modules Issues
```bash
# Remove and reinstall
rm -rf node_modules
npm install
```

### Google OAuth Not Working
1. Check Client ID/Secret in .env
2. Verify authorized URLs in Google Console
3. Ensure NEXTAUTH_SECRET is set
4. Clear browser cookies

### Pinecone Connection Error
1. Check API key in .env
2. Verify index name matches
3. Check internet connection
4. Try reducing similarity_threshold in cache.py

## 📊 Key Metrics

- **Target Response Time:** 5-10 seconds
- **Cache Hit Rate:** 40-60%
- **Error Rate:** <1%
- **Max Concurrent Users:** 100-200
- **Cost per Month:** $15-100

## 🎯 Deployment Checklist Quick Version

### Pre-Deployment (1-2 hours)
- [ ] GCP project created
- [ ] Cloud Storage bucket created with PDFs
- [ ] Pinecone index created
- [ ] Google OAuth credentials obtained

### Deployment (2-4 hours)
- [ ] Inference backend deployed to GCP Cloud Functions
- [ ] API backend deployed to Cloud Run
- [ ] Frontend deployed to Vercel
- [ ] All environment variables set
- [ ] Integration tests passed

### Post-Deployment (30 mins)
- [ ] Health checks passing
- [ ] Monitoring dashboards created
- [ ] Logs being collected
- [ ] Alerts configured

## 🔒 Security Checklist

- [ ] No API keys in code
- [ ] All secrets in environment variables
- [ ] HTTPS enabled
- [ ] CORS configured
- [ ] OAuth credentials secured
- [ ] Rate limiting enabled
- [ ] Input validation in place
- [ ] Error logging doesn't expose sensitive data

## 📱 API Response Format

**Success (200)**
```json
{
  "answer": "Photosynthesis is...",
  "sourcePages": [12, 15, 23],
  "cached": false,
  "responseTime": 6.234
}
```

**Error (400/500)**
```json
{
  "detail": "Error message here"
}
```

## 🧪 Manual Test Flow

1. Open http://localhost:3000
2. Click "Sign in with Google"
3. Complete OAuth flow
4. Select a subject (Science, Math, History, Literature)
5. Ask a question (e.g., "What is photosynthesis?")
6. Wait for response (5-10 seconds on first query, <2s on cached)
7. Check source pages displayed

## 💻 Useful Commands

```bash
# View logs
# Frontend (Vercel dashboard)
# API (Cloud Run logs UI)
gcloud logging read --limit 50

# GCP Function logs
gcloud functions logs read colpali_query

# View Pinecone stats
# Via dashboard or:
curl -H "Authorization: Bearer $PINECONE_API_KEY" \
  https://api.pinecone.io/indexes/rag-queries

# Test all services
curl http://localhost:3000/api/auth/session
curl http://localhost:8000/health
curl http://localhost:8080/health
```

## 🎓 Study Materials

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Pinecone Getting Started](https://docs.pinecone.io/guides/getting-started/quickstart)
- [GCP Cloud Functions](https://cloud.google.com/functions/docs)
- [ColPali Paper](https://arxiv.org/abs/2407.01449)

## ❓ FAQ

**Q: How do I change the 4 subjects?**  
A: Edit `frontend/pages/chat.tsx` - modify the `SUBJECTS` array and create corresponding PDFs in GCS.

**Q: Can I add chat history?**  
A: Yes, modify `ChatInterface.tsx` to persist messages to a database.

**Q: How do I use a larger model?**  
A: Change `MODEL_NAME` in `inference-backend/main.py` to `vidore/colpali-v1.3` (full model).

**Q: Can this support multiple PDFs per subject?**  
A: Yes, modify the inference function to accept multiple document selections.

**Q: What's the latency breakdown?**  
- Frontend → API: 200ms
- Cache lookup: 500ms (hit) or calls inference
- Inference: 5-6 seconds total
  - Download PDF: 1s
  - Embedding: 2s
  - Retrieval: 500ms
  - Generation: 2s

---

**Start here → Run setup.sh/setup.bat → Read README.md → Deploy!**
