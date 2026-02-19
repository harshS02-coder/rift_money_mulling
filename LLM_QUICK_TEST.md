# Quick Start: Test LLM Features in Fallback Mode

Get up and running with LLM features immediately - no API keys required!

---

## Step 1: Upload Some Data

First, upload a CSV file with transaction data (use one of the test files):

```bash
curl -X POST "http://localhost:8000/api/upload-csv" \
  -F "file=@suspicious_10_transactions.csv"
```

Response will include:
```json
{
  "analysis_id": "12345abc...",
  "total_accounts": 10,
  "critical_accounts": ["ACC_1", "ACC_2"],
  ...
}
```

Save the `analysis_id` for next steps.

---

## Step 2: Test Account Narrative

Get AI-generated explanation for a flagged account:

```bash
curl "http://localhost:8000/api/account-narrative/ACC_1"
```

**Example Response (Fallback Mode):**
```json
{
  "account_id": "ACC_1",
  "narrative": "Account ACC_1 exhibits critical characteristics of a shell account, with very high-value throughput relative to transaction count and limited unique connections. Immediate investigation recommended.",
  "risk_level": "CRITICAL",
  "risk_score": 85.3
}
```

---

## Step 3: Test Investigation Recommendations

Get actionable next steps:

```bash
curl "http://localhost:8000/api/recommendations/ACC_1"
```

**Example Response (Fallback Mode):**
```json
{
  "account_id": "ACC_1",
  "risk_score": 85.3,
  "risk_level": "CRITICAL",
  "risk_factors": ["high_shell_score", "limited_sources"],
  "recommendations": [
    "Review all transaction details for the past 90 days",
    "Analyze source of funds for large transactions",
    "Investigate account beneficiary and ownership",
    "Cross-reference with other flagged accounts for connections",
    "Check for suspicious timing patterns"
  ],
  "generated_at": "2026-02-19T10:30:00Z"
}
```

---

## Step 4: Test Investigation Summary

Get executive brief of entire analysis:

```bash
curl "http://localhost:8000/api/investigation-summary/12345abc"
```

(Replace with your `analysis_id` from Step 1)

**Example Response (Fallback Mode):**
```json
{
  "analysis_id": "12345abc",
  "executive_summary": "Overall Risk Level: CRITICAL. Analysis identified 2 critical-risk accounts and 3 high-risk accounts. 1 suspicious cycle detected. Prioritize investigation of critical accounts first.",
  "generated_at": "2026-02-19T10:30:00Z"
}
```

---

## Step 5: Test LLM Status

Check if LLM is configured (should show as disabled in fallback mode):

```bash
curl "http://localhost:8000/api/llm-status"
```

**Response (No LLM Configured):**
```json
{
  "llm_enabled": false,
  "provider": "openai",
  "model": "gpt-3.5-turbo",
  "message": "LLM features disabled. Set LLM_API_KEY environment variable to enable."
}
```

---

## All Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/account-narrative/{account_id}` | GET | Account risk narrative |
| `/api/cycle-analysis/{analysis_id}/{ring_index}` | GET | Cycle analysis |
| `/api/investigation-summary/{analysis_id}` | GET | Executive summary |
| `/api/recommendations/{account_id}` | GET | Investigation guide |
| `/api/llm-status` | GET | Check LLM status |

---

## Testing Script

Save this as `test_llm.sh`:

```bash
#!/bin/bash

# Upload test data
echo "📤 Uploading test data..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/upload-csv" \
  -F "file=@suspicious_10_transactions.csv")

ANALYSIS_ID=$(echo $RESPONSE | grep -o '"analysis_id":"[^"]*' | cut -d'"' -f4)
echo "✅ Analysis ID: $ANALYSIS_ID"

# Get a critical account
CRITICAL=$(echo $RESPONSE | grep -o '"critical_accounts":\[\("[^"]*"\)' | grep -o '"[^"]*"' | head -1 | tr -d '"')
echo "✅ Critical Account: $CRITICAL"

echo ""
echo "========== LLM STATUS =========="
curl -s "http://localhost:8000/api/llm-status" | python -m json.tool

echo ""
echo "========== ACCOUNT NARRATIVE =========="
curl -s "http://localhost:8000/api/account-narrative/$CRITICAL" | python -m json.tool

echo ""
echo "========== RECOMMENDATIONS =========="
curl -s "http://localhost:8000/api/recommendations/$CRITICAL" | python -m json.tool

echo ""
echo "========== INVESTIGATION SUMMARY =========="
curl -s "http://localhost:8000/api/investigation-summary/$ANALYSIS_ID" | python -m json.tool

echo ""
echo "✅ All tests completed!"
```

Run it:
```bash
chmod +x test_llm.sh
./test_llm.sh
```

---

## What's Happening?

In **Fallback Mode** (no LLM configured):
- ✅ All endpoints work
- ✅ Meaningful responses generated
- ✅ No external API calls
- ✅ Zero latency
- ⚠️ Less detailed than with LLM

The system generates:
- Risk tier-based narratives (CRITICAL → HIGH → MEDIUM → LOW)
- Pattern-based recommendations
- Volume-and-pattern-based summaries

---

## Enable Real LLM (Optional)

After testing fallback mode, optionally enable real AI:

### OpenAI (Recommended)
```bash
export LLM_PROVIDER=openai
export LLM_API_KEY=sk-xxx...
export LLM_MODEL=gpt-3.5-turbo

# Restart backend
pkill -f "uvicorn"
cd backend && ./venv/bin/uvicorn app.main:app --reload
```

### Ollama (Free, Local)
```bash
# Install from https://ollama.ai
ollama pull mistral
ollama serve

# In another terminal
export LLM_PROVIDER=ollama
export LLM_MODEL=mistral

# Restart backend
```

Run `./test_llm.sh` again to see AI-generated narratives!

---

## Comparison: Fallback vs LLM

### Account Narrative

**Fallback:**
> Account ACC_1 exhibits critical characteristics of a shell account, with very high-value throughput relative to transaction count and limited unique connections. Immediate investigation recommended.

**With LLM (OpenAI):**
> Account ACC_1 demonstrates critical money laundering risk through classic shell account indicators: $847,500 processed in just 2 transactions by a single source, indicating rapid pass-through activity. The account lacks normal business patterns—no diversified trading relationships or operational consistency. This profile matches high-risk money mule operations. Urgent financial crimes investigation required.

---

## Cost

- **Fallback Mode**: $0 (no external calls)
- **Ollama**: $0 (local, free)
- **OpenAI**: ~$0.002 per call (~$1/500 calls)
- **Claude**: ~$0.003 per call (~$1.50/500 calls)

For most use cases, fallback mode is perfectly adequate!

---

## Next Steps

1. ✅ Test with fallback mode (this guide)
2. 🔄 Integrate into frontend (optional)
3. 🚀 Deploy with optional LLM (optional)
4. 📊 Monitor and refine (optional)

The system is **production-ready** with or without LLM enabled!
