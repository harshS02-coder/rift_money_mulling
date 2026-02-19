# RIFT 2026 Project Directory Structure

```
rift-hackathon-2026/
│
├── 📄 README.md                           # Main documentation (300+ lines)
├── 📄 QUICK_START.md                      # 30-second setup guide
├── 📄 COMPLETION_SUMMARY.md               # This project summary
├── 📄 PROJECT_INFO.txt                    # Project metadata
├── 🚀 run.sh                              # Linux/macOS startup script
├── 🚀 run.bat                             # Windows startup script
├── 📋 .gitignore                          # Git ignore patterns
│
│
├── 📦 backend/
│   │
│   ├── 📋 requirements.txt                # Python dependencies (10 packages)
│   ├── 🔑 .env                            # Environment variables
│   │
│   ├── 📂 app/
│   │   ├── __init__.py
│   │   ├── 🎯 main.py                     # FastAPI app - 6 endpoints, CORS, routes
│   │   │
│   │   ├── 📂 engine/                     # CORE DETECTION ENGINE
│   │   │   ├── __init__.py
│   │   │   ├── 🧮 graph_builder.py        # NetworkX graph construction
│   │   │   │   - build_graph()
│   │   │   │   - get_account_stats()
│   │   │   │   - get_neighbors()
│   │   │   │
│   │   │   ├── 🔄 cycle_detector.py       # DFS cycle detection (3-5 length)
│   │   │   │   - find_all_cycles()
│   │   │   │   - get_cycle_metrics()
│   │   │   │   - get_cycle_participation()
│   │   │   │
│   │   │   ├── 💰 smurf_detector.py       # 72-hour window analysis
│   │   │   │   - detect_smurfing_accounts()
│   │   │   │   - detect_concentration_patterns()
│   │   │   │   - get_accounts_by_fan_activity()
│   │   │   │
│   │   │   └── 🏚️ shell_detector.py       # Low-transaction detection
│   │   │       - detect_shell_accounts()
│   │   │       - detect_pass_through_accounts()
│   │   │       - detect_low_activity_high_value()
│   │   │
│   │   ├── 📂 schemas/                    # Pydantic validation schemas
│   │   │   ├── __init__.py
│   │   │   ├── 📨 transaction.py          # Transaction & TransactionRequest models
│   │   │   └── 📤 results.py              # Ring, Alert, Score, AnalysisResults models
│   │   │
│   │   └── 📂 utils/
│   │       ├── __init__.py
│   │       └── 📊 scoring.py              # Risk scoring (0-100, weighted)
│   │           - calculate_account_score()
│   │           - score_ring_participation()
│   │           - score_smurfing_behavior()
│   │           - score_shell_account()
│   │
│   └── 📂 tests/                          # Unit tests directory (empty, ready for tests)
│
│
├── 📦 frontend/
│   │
│   ├── 📋 package.json                    # npm dependencies & scripts
│   ├── 🏗️ vite.config.js                  # Vite build configuration
│   ├── 📄 index.html                      # React entry point
│   │
│   ├── 📂 src/
│   │   ├── 🎯 App.jsx                     # Main layout & orchestration
│   │   ├── 📄 main.jsx                    # React initialization
│   │   ├── 🎨 App.css                     # Main styles
│   │   ├── 🎨 index.css                   # Global styles + CSS variables
│   │   │
│   │   ├── 📂 components/                 # React components
│   │   │   ├── 📤 FileUpload.jsx          # Drag-drop CSV upload
│   │   │   │   └── 🎨 FileUpload.css
│   │   │   │
│   │   │   ├── 📊 GraphView.jsx           # D3.js force-directed graph
│   │   │   │   └── 🎨 GraphView.css
│   │   │   │
│   │   │   ├── 📋 RingTable.jsx           # Tabbed results tables
│   │   │   │   └── 🎨 RingTable.css      # (Cycles/Smurfing/Shells)
│   │   │   │
│   │   │   └── ℹ️ AccountInfo.jsx          # Account details panel
│   │   │       └── 🎨 AccountInfo.css
│   │   │
│   │   ├── 📂 services/
│   │   │   └── 🔗 api.js                  # Axios API client
│   │   │       - analyzeTransactions()
│   │   │       - uploadCSV()
│   │   │       - getAnalysis()
│   │   │       - getAccountDetails()
│   │   │
│   │   ├── 📂 hooks/                      # Custom React hooks (empty, ready for use)
│   │   │
│   │   └── 📂 styles/                     # Component-specific styles
│   │       ├── FileUpload.css
│   │       ├── GraphView.css
│   │       ├── RingTable.css
│   │       └── AccountInfo.css
│   │
│   ├── 📂 public/
│   │   └── 📊 sample_transactions.csv     # Test data (25 transactions)
│   │       - Ring: A→B→C→A
│   │       - Smurfing: 7 txns in 72h
│   │       - Shell: High value, low txns
│   │
│   └── 📂 node_modules/                   # npm dependencies (installed on npm install)
│
│
├── 📂 docs/                               # Documentation directory
│   └── 📄 README.md                       # Docs index
│
└── 📂 public/
    └── 📊 sample_transactions.csv         # CSV sample data
```

## 📊 Component Breakdown

### Backend - 4 Detection Engines
```
1. Graph Builder
   ↓ (Creates NetworkX DiGraph)
   
2. Cycle Detector
   ↓ (Finds rings 3-5 length via DFS)
   
3. Smurfing Detector
   ↓ (72-hour window analysis, fan-in/out)
   
4. Shell Detector  
   ↓ (Low-activity, high-value accounts)
   
   ↓ (All feed into)
   
5. Risk Scorer
   ↓ (Multi-factor scoring)
   
6. FastAPI Server
   ↓ (REST endpoints)
```

### Frontend - 4 Main Components
```
1. FileUpload
   ↓ (CSV drag-drop)
   
2. GraphView (D3)
   ↓ (Visualization)
   
3. RingTable
   ↓ (Results tabs)
   
4. AccountInfo
   ↓ (Details panel)
   
   ↓ (All in)
   
5. App.jsx
   ↓ (Main orchestration)
```

## 📊 Statistics

| Category | Count |
|----------|-------|
| Python Files | 11 |
| React/JSX Files | 5 |
| CSS Files | 7 |
| Config Files | 5 |
| Documentation | 5 |
| Scripts | 2 |
| Data Files | 1 |
| **Total** | **~50 files** |

## 🎯 File Purposes

### Critical Files
- `backend/app/main.py` - Server entry point
- `frontend/src/App.jsx` - UI entry point
- `backend/app/engine/*.py` - Detection algorithms
- `backend/app/utils/scoring.py` - Risk calculation

### Configuration
- `backend/requirements.txt` - Backend dependencies
- `frontend/package.json` - Frontend dependencies
- `vite.config.js` - Build configuration
- `.env` - Environment variables

### Startup
- `run.sh` - macOS/Linux launcher
- `run.bat` - Windows launcher

### Documentation
- `README.md` - Main guide
- `QUICK_START.md` - Setup guide
- `COMPLETION_SUMMARY.md` - Project summary

### Data
- `public/sample_transactions.csv` - Test CSV

## 🚀 How It All Works

```
User uploads CSV
    ↓
Frontend: FileUpload catches file
    ↓
Frontend: Sends to /api/upload-csv
    ↓
Backend: Parses CSV → creates Transactions
    ↓
Backend: GraphBuilder creates directed graph
    ↓
Backend: CycleDetector finds rings (DFS)
    ↓
Backend: SmurfDetector finds 72-hr patterns
    ↓
Backend: ShellDetector finds low-txn accounts
    ↓
Backend: SuspicionScorer ranks accounts (0-100)
    ↓
Backend: Returns AnalysisResults JSON
    ↓
Frontend: Receives results
    ↓
Frontend: GraphView renders D3 visualization
    ↓
Frontend: RingTable shows tabs (Cycles/Smurf/Shells)
    ↓
Frontend: AccountInfo shows details on click
    ↓
User sees comprehensive Money Muling analysis 🎯
```

## 📁 Size Summary

```
Backend code:     ~1,500 lines of Python
Frontend code:    ~1,200 lines of JSX/CSS
Config files:     ~200 lines
Documentation:    ~1,000 lines
Total code:       ~3,900 lines
```

---

**Built for RIFT 2026 Hackathon - Money Muling Detection**
