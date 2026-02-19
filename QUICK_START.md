# RIFT 2026 Quick Start Guide

## ⚡ 30-Second Setup

### On macOS/Linux:
```bash
cd rift-hackathon-2026
chmod +x run.sh
./run.sh
```

### On Windows:
```bash
cd rift-hackathon-2026
run.bat
```

### Manual Setup (if scripting issues):

**Terminal 1 - Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🌐 Access URLs

Once running:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc

## 📊 Testing with Sample Data

1. Download the sample CSV: `public/sample_transactions.csv`
2. Open http://localhost:5173
3. Drag and drop the CSV file onto the upload area
4. View results in the graph visualization and tables

## 🔍 What to Look For

After uploading sample data, you'll see:

### Cycles/Rings
- **Ring_1**: ACC001 → ACC002 → ACC003 → ACC001 (10k flowing)
- **Ring_2**: ACC001 → ACC004 → ACC005 → ACC002 → ACC001 (3k flowing)

### Smurfing Patterns
- **ACC001**: 7 transactions in 72 hours (5.5k splits to multiple accounts)
- **ACC002**: 7 consolidating transactions

### Shell Accounts
- **ACC002**: 5 transactions, 20k throughput (4k avg per transaction)
- **ACC008**: 1 transaction, 15k (shell characteristics)

### Risk Scores
- **ACC001**: HIGH/CRITICAL (ring involvement + smurfing)
- **ACC002**: HIGH (ring involvement + consolidation)
- **ACC006, ACC007, ACC008**: MEDIUM-HIGH (shell/pass-through)

## 🎯 Key Features to Try

1. **Graph Interaction**
   - Click nodes to see account details
   - Hover over nodes for highlights
   - Node size indicates risk level
   - Colors: Red (Critical), Orange (High), Yellow (Medium), Green (Low)

2. **Tabs**
   - Click "Cycles" to see detected rings
   - Click "Smurfing" for 72-hour pattern alerts
   - Click "Shell Accounts" for high-value, low-activity accounts

3. **Risk Breakdown**
   - View component scores for each account
   - See why each account got flagged
   - Review identified risk factors

## 📁 File Structure Quick Reference

```
rift-hackathon-2026/
├── backend/app/main.py          ← FastAPI server
├── frontend/src/App.jsx         ← React main
├── run.sh/run.bat              ← Start everything
├── README.md                    ← Full documentation
└── public/sample_transactions.csv ← Test data
```

## 🆘 Troubleshooting

### Backend won't start
- Ensure Python 3.8+ installed: `python3 --version`
- Check port 8000 not in use: `lsof -i :8000`
- Install deps: `pip install -r backend/requirements.txt`

### Frontend won't start
- Ensure Node 16+ installed: `node --version`
- Clear cache: `rm -rf frontend/node_modules`
- Reinstall: `cd frontend && npm install`

### Port conflicts
- Change backend port in `backend/app/main.py`: `--port 9000`
- Change frontend port in `frontend/vite.config.js`: `port: 5174`

### CORS errors
- Already configured for localhost
- For production, update `frontend/src/services/api.js` with correct backend URL

## 📚 Next Steps

1. Upload your own transaction data (CSV format)
2. Explore the API docs at http://localhost:8000/docs
3. Modify detection thresholds in backend code
4. Customize risk scoring weights in `backend/app/utils/scoring.py`
5. Extend with additional detection algorithms

## 💡 Example Use Cases

### Scenario 1: Simple Cycle
```csv
id,from_account,to_account,amount,timestamp
1,A,B,1000,2025-12-15T10:00:00
2,B,C,1000,2025-12-15T11:00:00
3,C,A,1000,2025-12-15T12:00:00
```
Result: Cycle detected (A→B→C→A), Risk = HIGH

### Scenario 2: Smurfing Pattern
```csv
id,from_account,to_account,amount,timestamp
1,A,B,100,2025-12-15T10:00:00
2,A,C,100,2025-12-15T10:05:00
3,A,D,100,2025-12-15T10:10:00
... (10+ times in 72 hours)
```
Result: Smurfing detected, Risk = MEDIUM-HIGH

### Scenario 3: Shell Account
```csv
id,from_account,to_account,amount,timestamp
1,A,B,50000,2025-12-15T10:00:00
2,B,C,50000,2025-12-15T11:00:00
```
Result: Shell account B (high value, low transactions), Risk = MEDIUM-HIGH

---

**For Developers**: See [README.md](../README.md) for detailed technical documentation.

**Questions?** Check the [README.md](../README.md) for comprehensive guide!
