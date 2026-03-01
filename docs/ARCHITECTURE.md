# RAG Production Architecture

## Overview

This is a production-grade Retrieval-Augmented Generation (RAG) system using ColPali for document embedding and Flan-T5 for answer generation.

### Architecture

```
┌─────────────────────────────────────┐
│   FRONTEND (React + Next.js)        │
│  • Google OAuth Authentication      │
│  • Subject Selection (4 subjects)   │
│  • Chat Interface                   │
└─────────────┬───────────────────────┘
              │ HTTP/REST
              ▼
┌─────────────────────────────────────┐
│   API BACKEND (FastAPI)             │
│  • Request validation               │
│  • Pinecone Vector Cache            │
│  • Query deduplication              │
│  • Orchestration                    │
└─────────────┬───────────────────────┘
              │ Async HTTP
              ▼
┌─────────────────────────────────────┐
│  GCP CLOUD FUNCTION (Inference)     │
│  • ColPali Query Embedding          │
│  • PDF Document Retrieval           │
│  • Flan-T5 Answer Generation        │
│  • GCS Document Storage             │
└─────────────────────────────────────┘
```

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **API Backend**: FastAPI, Uvicorn, Pinecone Vector DB
- **Inference**: GCP Cloud Functions, ColPali v1.3, Flan-T5-small
- **Document Storage**: Google Cloud Storage
- **Authentication**: NextAuth + Google OAuth 2.0
- **Cache**: Pinecone (vector similarity search)

## Features

✅ Google OAuth single sign-in  
✅ 4 subject selection (Mathematics, Science, History, Literature)  
✅ Vector database caching for query deduplication  
✅ 5-10 second response time target  
✅ Serverless inference scaling  
✅ Production-ready error handling  
✅ Comprehensive logging  

## Project Structure

```
rag-production/
├── frontend/                 # React + Next.js
│   ├── pages/
│   │   ├── _app.tsx
│   │   ├── index.tsx        # Login page
│   │   └── chat.tsx         # Chat interface
│   ├── components/
│   │   └── ChatInterface.tsx
│   ├── lib/
│   │   └── api.ts           # API client
│   ├── styles/
│   │   └── globals.css
│   ├── package.json
│   └── tsconfig.json
│
├── api-backend/             # FastAPI
│   ├── main.py              # FastAPI app
│   ├── routes.py            # Query endpoint
│   ├── models.py            # Pydantic models
│   ├── config.py            # Configuration
│   ├── cache.py             # Pinecone integration
│   ├── inference.py         # GCP Function client
│   └── requirements.txt
│
├── inference-backend/       # GCP Cloud Function
│   ├── main.py              # Cloud Function handler
│   ├── pdf_handler.py       # PDF utilities
│   ├── app.yaml             # GCP config
│   └── requirements.txt
│
└── docs/
    ├── DEPLOYMENT.md        # Deployment guide
    ├── ARCHITECTURE.md      # This file
    ├── API.md
    └── SETUP.md
```

## Response Time Breakdown (Target: 5-10s)

- Frontend to API: ~200ms
- Cache lookup (Pinecone): ~500ms (if hit: return here)
- API to GCP Function: ~500ms
- GCP Function:
  - Download PDF from GCS: ~1s
  - ColPali embedding: ~2s
  - Page retrieval: ~500ms
  - Flan-T5 generation: ~2s
  - Total: ~5.5s
- Total: ~6.7s (cache miss) / ~1.2s (cache hit)

## Deployment Checklist

- [ ] Set up GCP project
- [ ] Create Cloud Storage bucket for PDFs
- [ ] Deploy Pinecone vector database
- [ ] Deploy API Backend to Cloud Run
- [ ] Deploy GCP Cloud Function
- [ ] Set up Google OAuth credentials
- [ ] Deploy frontend to Vercel/Firebase Hosting
- [ ] Configure environment variables
- [ ] Load test (100-200 users/day)
- [ ] Set up monitoring and logging
- [ ] Create backup strategy

See `DEPLOYMENT.md` for detailed steps.
