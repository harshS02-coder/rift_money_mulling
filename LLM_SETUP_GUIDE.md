# LLM Configuration Guide for RIFT 2026

## Overview
The LLM integration adds AI-powered narrative generation, risk explanations, and investigation recommendations to RIFT 2026.

## Quick Start (No Setup Required)
All endpoints work without LLM setup. Fallback narratives are generated when LLM is unavailable.

## Enable LLM Features (Optional)

### Option 1: OpenAI (GPT-3.5/GPT-4)
```bash
# Install OpenAI package
pip install openai

# Set environment variables
export LLM_PROVIDER=openai
export LLM_API_KEY=sk-xxxx...
export LLM_MODEL=gpt-3.5-turbo  # or gpt-4
```

### Option 2: Anthropic Claude
```bash
# Install Anthropic package
pip install anthropic

# Set environment variables
export LLM_PROVIDER=claude
export LLM_API_KEY=sk-ant-xxxx...
export LLM_MODEL=claude-3-sonnet-20240229
```

### Option 3: Local Ollama (Free, Offline)
```bash
# Install Ollama from https://ollama.ai
# Download a model: ollama pull mistral
# Start Ollama: ollama serve

# Set environment variables
export LLM_PROVIDER=ollama
export LLM_MODEL=mistral  # or any other Ollama model
```

## API Endpoints

### 1. Account Risk Narrative
```
GET /api/account-narrative/{account_id}
```
Generates natural language explanation of account's risk profile.

**Response:**
```json
{
  "account_id": "ACC_123",
  "narrative": "Account ACC_123 exhibits critical characteristics of a shell account...",
  "risk_level": "CRITICAL",
  "risk_score": 87.5
}
```

### 2. Cycle Analysis
```
GET /api/cycle-analysis/{analysis_id}/{ring_index}
```
Analyzes a specific detected cycle/ring pattern.

**Response:**
```json
{
  "ring_id": "RING_xxx",
  "accounts": ["ACC_1", "ACC_2", "ACC_3"],
  "analysis": "This 3-account cycle with $500k flowing through indicates...",
  "total_amount": 500000,
  "transaction_count": 15
}
```

### 3. Investigation Summary
```
GET /api/investigation-summary/{analysis_id}
```
Executive summary of entire analysis using AI.

**Response:**
```json
{
  "analysis_id": "abc123",
  "executive_summary": "Overall Risk Level: CRITICAL. Analysis identified 5 critical-risk accounts...",
  "generated_at": "2026-02-19T10:30:00Z"
}
```

### 4. Investigation Recommendations
```
GET /api/recommendations/{account_id}
```
AI-powered recommendations for investigating an account.

**Response:**
```json
{
  "account_id": "ACC_123",
  "risk_score": 87.5,
  "risk_level": "CRITICAL",
  "risk_factors": ["high_throughput", "limited_sources", "pass_through"],
  "recommendations": [
    "1. Review all transaction details for the past 90 days",
    "2. Investigate source of funds for amounts exceeding $100k",
    "3. Cross-reference with other flagged accounts",
    ...
  ],
  "generated_at": "2026-02-19T10:30:00Z"
}
```

### 5. LLM Status
```
GET /api/llm-status
```
Check if LLM features are enabled.

**Response:**
```json
{
  "llm_enabled": true,
  "provider": "openai",
  "model": "gpt-3.5-turbo",
  "message": "LLM features enabled. Use other endpoints for narratives and recommendations."
}
```

## Configuration via .env File

Create or update `.env` in backend directory:

```
# LLM Configuration
LLM_PROVIDER=openai  # openai, claude, or ollama
LLM_API_KEY=sk-xxxxx
LLM_MODEL=gpt-3.5-turbo

# Database Config (existing)
DATABASE_URL=sqlite:///rift.db

# Server Config (existing)
DEBUG=False
LOG_LEVEL=INFO
```

## Fallback Behavior

If LLM is not configured, all endpoints return generated fallback narratives:
- Generic but meaningful risk assessments
- Structured recommendations based on risk factors
- No external API calls
- Zero latency

## Cost Estimation

### OpenAI
- GPT-3.5-turbo: ~$0.002 per narrative (typical)
- GPT-4: ~$0.03 per narrative
- Recommended: Use GPT-3.5 for cost efficiency

### Claude
- ~$0.003 per 1K input tokens, ~$0.015 per 1K output tokens
- Similar cost to GPT-3.5

### Ollama
- **FREE** - runs locally
- No API costs
- Requires local GPU (or CPU, slower)

## Troubleshooting

**"openai package not installed"**
```bash
pip install openai
```

**"Failed to connect to Ollama"**
```bash
# Make sure Ollama is running
ollama serve

# Test the connection
curl http://localhost:11434/api/generate -d '{"model":"mistral","prompt":"test"}'
```

**LLM calls are slow**
- OpenAI/Claude: Network latency
- Ollama: CPU-bound, larger models are slower
- Solution: Use smaller models (mistral vs llama2)

**Generating generic narratives instead of LLM**
- Check: `GET /api/llm-status`
- Verify LLM_API_KEY is set
- Check provider configuration

## Performance Tips

1. **Batch requests**: Call endpoints for multiple accounts per analysis
2. **Cache results**: LLM responses don't change for same account
3. **Use ollama**: Eliminates API latency for local deployment
4. **Smaller models**: mistral/dolphin are faster than llama2

## Integration with Frontend

Call these endpoints from the frontend to display:
- Risk narratives in account detail cards
- Cycle analysis in ring investigation view
- Investigation summaries in dashboard
- Recommendations in action items/alerts

Example:
```javascript
// Get account narrative
const narrative = await fetch(`/api/account-narrative/${accountId}`).then(r => r.json())
// Display in UI
```

---

**LLM Integration Status**: Complete and Ready for Testing  
**Default Behavior**: Works without LLM (fallback mode)  
**Optional Feature**: Enhanced narratives with LLM enabled
