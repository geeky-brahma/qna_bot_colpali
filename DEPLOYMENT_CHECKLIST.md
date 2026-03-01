# Pre-Deployment Checklist

## ✅ Backend Configuration

- [ ] GCP project created
- [ ] GCP APIs enabled:
  - [ ] Cloud Functions
  - [ ] Cloud Run
  - [ ] Cloud Storage
  - [ ] Cloud Build
  - [ ] Artifact Registry

- [ ] Service account created with roles:
  - [ ] Storage Object Admin
  - [ ] Cloud Functions Invoker

- [ ] Cloud Storage bucket created (`rag-documents`)
  - [ ] Sample PDFs uploaded:
    - [ ] documents/mathematics.pdf
    - [ ] documents/science.pdf
    - [ ] documents/history.pdf
    - [ ] documents/literature.pdf

## ✅ Cache Setup

- [ ] Pinecone account created
- [ ] Index created:
  - [ ] Name: `rag-queries`
  - [ ] Dimension: `768`
  - [ ] Metric: `cosine`
  - [ ] Serverless (GCP)
- [ ] API key secured in secret manager

## ✅ Authentication

- [ ] Google OAuth 2.0 credentials created
- [ ] Client ID obtained
- [ ] Client Secret obtained
- [ ] Authorized redirect URIs configured:
  - [ ] http://localhost:3000/api/auth/callback/google (dev)
  - [ ] https://your-domain.web.app/api/auth/callback/google (prod)
- [ ] Authorized JavaScript origins configured:
  - [ ] http://localhost:3000 (dev)
  - [ ] https://your-domain.web.app (prod)

## ✅ Inference Backend (Cloud Function)

- [ ] `inference-backend/main.py` complete
- [ ] `inference-backend/pdf_handler.py` complete
- [ ] `requirements.txt` with all dependencies
- [ ] `.env` configured with:
  - [ ] GCP_PROJECT_ID
  - [ ] GCP_BUCKET_NAME
- [ ] Local testing passed:
  - [ ] Health check endpoint works
  - [ ] Function accepts valid requests
  - [ ] PDF download from GCS works
  - [ ] Model inference works (or mocked)
- [ ] Dockerfile ready (if using Cloud Run)
- [ ] Deployed to GCP:
  - [ ] Function deployable
  - [ ] Environment variables set
  - [ ] Service account permissions configured
  - [ ] Function trigger URL obtained

## ✅ API Backend (Cloud Run)

- [ ] `api-backend/main.py` complete
- [ ] `api-backend/routes.py` complete
- [ ] `api-backend/cache.py` complete
- [ ] `api-backend/inference.py` complete
- [ ] `requirements.txt` updated
- [ ] `.env` configured:
  - [ ] PINECONE_API_KEY
  - [ ] INFERENCE_FUNCTION_URL
  - [ ] Cache settings tuned
- [ ] Dockerfile created
- [ ] Local testing passed:
  - [ ] Health check works
  - [ ] Query endpoint responds
  - [ ] Pinecone connection works
  - [ ] Inference function calls succeed
- [ ] Docker image builds successfully
- [ ] Deployed to Cloud Run:
  - [ ] Image built and pushed to GCR
  - [ ] Service deployed
  - [ ] Scaling configured
  - [ ] Environment variables set
  - [ ] Service URL obtained

## ✅ Frontend

- [ ] All components created
- [ ] Pages implemented:
  - [ ] index.tsx (login)
  - [ ] chat.tsx (subject selection + chat)
  - [ ] _app.tsx (session provider)
- [ ] API client (lib/api.ts) configured
- [ ] Styling with Tailwind CSS
- [ ] NextAuth configuration
- [ ] package.json dependencies correct
- [ ] `.env.local` example created
- [ ] Local testing passed:
  - [ ] Google OAuth login works
  - [ ] Subject selection works
  - [ ] Chat interface renders
  - [ ] API calls work
  - [ ] Messages display correctly
- [ ] Build successful: `npm run build`
- [ ] Deployed (Vercel/Firebase):
  - [ ] Repository connected
  - [ ] Environment variables configured
  - [ ] Build and deploy successful
  - [ ] URL obtained

## ✅ End-to-End Integration

- [ ] All services running locally
- [ ] Complete flow tested:
  - [ ] Login with Google
  - [ ] Select subject
  - [ ] Ask question
  - [ ] Receive answer
  - [ ] Source pages displayed
- [ ] Response times acceptable (<10s)
- [ ] Error handling tested:
  - [ ] Network timeout
  - [ ] Invalid inputs
  - [ ] Service down scenarios
- [ ] Logging verified in all services

## ✅ Security Review

- [ ] No hardcoded API keys
- [ ] All secrets in environment variables
- [ ] CORS configured appropriately
- [ ] HTTPS enforced (production)
- [ ] OAuth secrets secured
- [ ] Rate limiting considered
- [ ] Input validation in place
- [ ] Error messages don't leak info

## ✅ Monitoring & Logging

- [ ] Cloud Logging configured
- [ ] Log names defined:
  - [ ] `rag-api`
  - [ ] `rag-inference`
- [ ] Alerts configured:
  - [ ] Error rate > 5%
  - [ ] Latency > 30 seconds
  - [ ] Service unavailable
- [ ] Dashboards created for:
  - [ ] Response times
  - [ ] Cache hit rate
  - [ ] Error rates
  - [ ] Concurrent users

## ✅ Performance Testing

- [ ] Load test run (50-100 concurrent)
- [ ] Response times acceptable
- [ ] Cache hit rate > 40%
- [ ] No memory leaks detected
- [ ] Scaling tested

## ✅ Documentation

- [ ] README.md complete
- [ ] ARCHITECTURE.md documented
- [ ] DEPLOYMENT.md with all steps
- [ ] API.md with examples
- [ ] SETUP.md for developers
- [ ] Environment file examples provided
- [ ] Troubleshooting guide written

## ✅ Cost Analysis

- [ ] GCP pricing estimated
- [ ] Pinecone pricing estimated
- [ ] Frontend hosting cost estimated
- [ ] Total monthly cost within budget
- [ ] Auto-scaling policies configured

## ✅ Handoff & Maintenance

- [ ] Runbook created for daily ops
- [ ] Escalation procedures defined
- [ ] Backup/recovery procedure documented
- [ ] Team trained on deployment
- [ ] Access controls configured
- [ ] Monitoring tools accessible

## ✅ Post-Deployment

- [ ] Monitor for 48 hours
- [ ] Collect metrics baseline
- [ ] User feedback gathered
- [ ] Issues logged and prioritized
- [ ] Performance optimizations planned
- [ ] Scale-up plan ready if needed

---

## Notes

Track any issues or deviations in the sections below:

### Known Issues
- [ ] None yet

### Deviations from Plan
- [ ] None yet

### Optimizations for Next Phase
- [ ] Implement streaming responses
- [ ] Add chat history
- [ ] Multi-document support
- [ ] Fine-tuned model deployment

---

**Approval Sign-Off:**
- [ ] Backend Lead: _____________ Date: _______
- [ ] Frontend Lead: _____________ Date: _______
- [ ] DevOps/Infra: _____________ Date: _______
- [ ] Project Manager: ___________ Date: _______
