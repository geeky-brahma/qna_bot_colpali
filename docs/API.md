# API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: `https://rag-api-xxx.a.run.app`

## Endpoints

### POST /api/query

Main query endpoint with intelligent caching.

**Request:**
```json
{
  "query": "What is photosynthesis?",
  "subject": "Science",
  "userEmail": "user@example.com"
}
```

**Response:**
```json
{
  "answer": "Photosynthesis is a process in plants where...",
  "sourcePages": [12, 15, 23],
  "cached": false,
  "responseTime": 6.234
}
```

**Parameters:**
- `query` (string, required): The user's question (1-1000 chars)
- `subject` (string, required): One of: "Mathematics", "Science", "History", "Literature"
- `userEmail` (string, required): User's email for audit logging

**Response Fields:**
- `answer` (string): The generated answer
- `sourcePages` (array): Page numbers where information was found
- `cached` (boolean): Whether result was from cache
- `responseTime` (number): Time in seconds

**Status Codes:**
- `200`: Success
- `400`: Validation error (missing/invalid fields)
- `500`: Server error

### GET /health

System health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "pinecone_connected": true
}
```

**Status:**
- "healthy": All systems operational
- "degraded": Cache unavailable, inference working
- "unhealthy": Major system failures

## Error Handling

All errors return JSON with error details:

```json
{
  "detail": "Query is required"
}
```

**Common errors:**
- `{"detail": "Query is required"}` - Missing query field
- `{"detail": "Invalid subject"}` - Subject not in allowed list
- `{"detail": "Request to inference backend timed out"}` - Inference taking too long
- `{"detail": "Cache connection failed"}` - Pinecone unavailable

## Rate Limiting

- 100 requests/minute per IP (recommended for free tier)
- Production: Configure based on tier/usage

## Authentication

Currently: No authentication required (public API)

**Future**: Add API key authentication:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://rag-api-xxx.a.run.app/api/query
```

## Cache Behavior

### Cache Hit (Response Time: ~1.2s)
- Similar previous query found
- Returns cached answer immediately
- `cached: true` in response

### Cache Miss (Response Time: ~6-10s)
- New or unique query
- Calls inference backend
- Result cached for future queries
- `cached: false` in response

### Cache Configuration
- TTL: 24 hours
- Similarity threshold: 0.95 (0-1 scale)
- Index: 768-dimensional (ColPali embedding size)

## Example Usage

### Python
```python
import requests

payload = {
    "query": "Who discovered gravity?",
    "subject": "History",
    "userEmail": "student@school.com"
}

response = requests.post(
    "https://rag-api-xxx.a.run.app/api/query",
    json=payload,
    timeout=60
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Source Pages: {result['sourcePages']}")
print(f"From Cache: {result['cached']}")
```

### JavaScript/Fetch
```javascript
const payload = {
  query: "What is calculus?",
  subject: "Mathematics",
  userEmail: "user@example.com"
};

const response = await fetch("https://rag-api-xxx.a.run.app/api/query", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
});

const result = await response.json();
console.log(result.answer);
```

### cURL
```bash
curl -X POST https://rag-api-xxx.a.run.app/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain photosynthesis",
    "subject": "Science",
    "userEmail": "user@example.com"
  }'
```

## Monitoring

### Metrics to Track
- Response time (target: 5-10s)
- Cache hit rate (target: 40-60%)
- Error rate (target: <1%)
- Concurrent users
- Daily active users

### Logging
All queries logged with:
- Timestamp
- Query text
- Subject
- Response time
- Cache status
- Any errors

Access logs in Cloud Logging dashboard.

## Performance Guidelines

- Average response: 6-7 seconds
- P95 response: <15 seconds
- P99 response: <30 seconds

If exceeding:
1. Check Pinecone status
2. Verify GCP function resources (4GB RAM minimum)
3. Check network latency
4. Review concurrent user load

## Support

- Issues: GitHub Issues
- Docs: See `/docs` directory
- Email: support@example.com
