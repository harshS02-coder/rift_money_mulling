"""
FastAPI Main Application
Entry point with routes for transaction analysis and results.
"""
import uuid
import json
import os
from datetime import datetime
from io import StringIO
import csv
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import networkx as nx

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')

from app.schemas.transaction import Transaction, TransactionRequest
from app.schemas.results import (
    AnalysisResults, Ring, SmurfingAlert, ShellAccountAlert, 
    AccountSuspicionScore, RiskLevel, ErrorResponse
)
from app.engine.graph_builder import GraphBuilder
from app.engine.cycle_detector_v2 import CycleDetectorV2 as CycleDetector
from app.engine.smurf_detector_v2 import SmurfingDetectorV2 as SmurfingDetector
from app.engine.shell_detector_v2 import ShellAccountDetectorV2 as ShellAccountDetector
from app.utils.scoring import SuspicionScorer
from app.services.llm_service import get_llm_service

app = FastAPI(
    title="RIFT 2026 - Money Muling Detection Engine",
    version="1.0.0",
    description="Graph-based financial forensics for detecting money laundering patterns"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global analysis cache
analysis_cache = {}


@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RIFT Money Muling Detection Engine"}


@app.post("/api/analyze", response_model=AnalysisResults, tags=["Analysis"])
async def analyze_transactions(request: TransactionRequest) -> AnalysisResults:
    """
    Analyze transactions for money muling patterns.
    
    Returns detailed report with:
    - Detected cycles/rings
    - Smurfing alerts
    - Shell accounts
    - Suspicion scores for each account
    """
    try:
        if not request.transactions:
            raise HTTPException(status_code=400, detail="No transactions provided")
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Build graph
        graph_builder = GraphBuilder()
        graph = graph_builder.build_graph(request.transactions)
        
        # Detect cycles
        cycle_detector = CycleDetector(graph)
        all_cycles = cycle_detector.find_all_cycles(max_length=5, min_length=3)
        
        # Create Ring objects
        rings = []
        for idx, cycle in enumerate(all_cycles):
            metrics = cycle_detector.get_cycle_metrics(cycle)
            ring = Ring(
                ring_id=f"RING_{analysis_id[:8]}_{idx}",
                accounts=metrics["accounts"],
                length=metrics["length"],
                total_amount=metrics["total_amount"],
                detection_type="cycle",
                transactions=metrics["transaction_ids"]
            )
            rings.append(ring)
        
        # Detect smurfing
        smurf_detector = SmurfingDetector(request.transactions)
        smurfing_accounts = smurf_detector.detect_smurfing_accounts(min_transactions=10)
        
        smurfing_alerts = []
        for account_data in smurfing_accounts:
            alert = SmurfingAlert(
                account_id=account_data["account_id"],
                transaction_count=account_data["transaction_count"],
                time_window_hours=72,
                total_amount=account_data["total_amount"],
                fan_in=account_data["fan_in"],
                fan_out=account_data["fan_out"],
                risk_score=0.0  # Will be updated by scorer
            )
            smurfing_alerts.append(alert)
        
        # Detect shell accounts
        shell_detector = ShellAccountDetector(request.transactions)
        shell_accounts = shell_detector.detect_shell_accounts(max_transactions=5, min_total_value=50000)
        
        shell_alerts = []
        for account_data in shell_accounts:
            alert = ShellAccountAlert(
                account_id=account_data["account_id"],
                total_transactions=account_data["total_transactions"],
                total_throughput=account_data["total_throughput"],
                avg_transaction_value=account_data["avg_transaction_value"],
                risk_score=0.0,  # Will be updated by scorer
                description=f"Shell account with {account_data['total_transactions']} transactions totaling ${account_data['total_throughput']:,.2f}"
            )
            shell_alerts.append(alert)
        
        # Calculate suspicion scores for all accounts
        scorer = SuspicionScorer()
        all_accounts = graph_builder.get_all_accounts()
        
        account_scores = []
        high_risk = []
        critical_risk = []
        
        # Get cycle participation
        cycle_participation = cycle_detector.get_cycle_participation()
        
        for account_id in all_accounts:
            # Calculate ring involvement score
            ring_count = cycle_participation.get(account_id, 0)
            ring_amounts = []
            for cycle in all_cycles:
                if account_id in cycle:
                    metrics = cycle_detector.get_cycle_metrics(cycle)
                    ring_amounts.append(metrics["total_amount"])
            
            ring_score = scorer.score_ring_participation(
                account_id, ring_count, len(all_cycles), ring_amounts
            ) if all_cycles else 0.0
            
            # Calculate smurfing score
            account_smurfing = [s for s in smurfing_accounts if s["account_id"] == account_id]
            smurfing_score = 0.0
            if account_smurfing:
                data = account_smurfing[0]
                smurfing_score = scorer.score_smurfing_behavior(
                    data["transaction_count"],
                    data["fan_in"],
                    data["fan_out"],
                    data["total_amount"]
                )
            
            # Calculate shell account score
            account_shell = [s for s in shell_accounts if s["account_id"] == account_id]
            shell_score = 0.0
            if account_shell:
                data = account_shell[0]
                shell_score = scorer.score_shell_account(
                    data["total_transactions"],
                    data["total_throughput"],
                    data["avg_transaction_value"],
                    data["unique_sources"],
                    data["unique_destinations"]
                )
            
            # Calculate flow pattern score
            stats = graph_builder.get_account_stats(account_id)
            pattern_score = scorer.score_flow_pattern(
                account_id,
                stats.get("total_in", 0),
                stats.get("total_out", 0),
                stats.get("txn_count", 0),
                stats.get("in_degree", 0),
                stats.get("out_degree", 0)
            )
            
            # Get final score
            score_result = scorer.calculate_account_score(
                account_id,
                ring_involvement=ring_score,
                smurfing_score=smurfing_score,
                shell_score=shell_score,
                pattern_score=pattern_score
            )
            
            account_score = AccountSuspicionScore(
                account_id=account_id,
                base_score=score_result["base_score"],
                ring_involvement_score=score_result["ring_involvement_score"],
                smurfing_score=score_result["smurfing_score"],
                shell_score=score_result["shell_score"],
                final_score=score_result["final_score"],
                risk_level=RiskLevel(score_result["risk_level"]),
                risk_factors=score_result["risk_factors"]
            )
            account_scores.append(account_score)
            
            # Categorize risk levels
            if account_score.risk_level == RiskLevel.CRITICAL:
                critical_risk.append(account_id)
            elif account_score.risk_level == RiskLevel.HIGH:
                high_risk.append(account_id)
        
        # Update smurfing alert scores
        for alert in smurfing_alerts:
            account_score = next((s for s in account_scores if s.account_id == alert.account_id), None)
            if account_score:
                alert.risk_score = account_score.smurfing_score
        
        # Update shell alert scores
        for alert in shell_alerts:
            account_score = next((s for s in account_scores if s.account_id == alert.account_id), None)
            if account_score:
                alert.risk_score = account_score.shell_score
        
        # Calculate additional statistics
        transaction_amounts = [t.amount for t in request.transactions]
        total_volume = sum(transaction_amounts)
        avg_transaction = total_volume / len(transaction_amounts) if transaction_amounts else 0
        sorted_amounts = sorted(transaction_amounts)
        median_transaction = sorted_amounts[len(sorted_amounts) // 2] if sorted_amounts else 0
        
        suspicious_accounts = len(high_risk) + len(critical_risk)
        suspicious_percent = (suspicious_accounts / len(all_accounts) * 100) if all_accounts else 0
        
        accounts_with_rings = set()
        for cycle in all_cycles:
            accounts_with_rings.update(cycle)
        
        # Create summary
        summary = {
            "total_accounts": len(all_accounts),
            "total_transactions": len(request.transactions),
            "total_volume": float(total_volume),
            "avg_transaction": float(avg_transaction),
            "median_transaction": float(median_transaction),
            "min_transaction": float(min(transaction_amounts)) if transaction_amounts else 0,
            "max_transaction": float(max(transaction_amounts)) if transaction_amounts else 0,
            "cycles_detected": len(all_cycles),
            "avg_cycle_length": sum(len(c) for c in all_cycles) / len(all_cycles) if all_cycles else 0,
            "accounts_in_rings": len(accounts_with_rings),
            "smurfing_alerts_count": len(smurfing_alerts),
            "shell_accounts_count": len(shell_alerts),
            "high_risk_accounts": len(high_risk),
            "critical_accounts": len(critical_risk),
            "suspicious_accounts": suspicious_accounts,
            "suspicious_percent": float(suspicious_percent),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        # Create analysis result
        results = AnalysisResults(
            analysis_id=analysis_id,
            total_accounts=len(all_accounts),
            total_transactions=len(request.transactions),
            rings_detected=rings,
            smurfing_alerts=smurfing_alerts,
            shell_accounts=shell_alerts,
            account_scores=account_scores,
            high_risk_accounts=high_risk,
            critical_accounts=critical_risk,
            summary=summary
        )
        
        # Cache results
        analysis_cache[analysis_id] = results
        
        return results
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@app.post("/api/upload-csv", response_model=AnalysisResults, tags=["Analysis"])
async def upload_csv(file: UploadFile = File(...)) -> AnalysisResults:
    """
    Upload CSV file with transactions and analyze.
    
    CSV format should have columns:
    - id: Transaction ID
    - from_account: Source account
    - to_account: Destination account
    - amount: Transaction amount
    - timestamp: ISO format datetime
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be CSV format")
        
        # Read CSV
        contents = await file.read()
        csv_data = contents.decode('utf-8')
        
        # Parse CSV
        csv_file = StringIO(csv_data)
        reader = csv.DictReader(csv_file)
        
        transactions = []
        for row in reader:
            try:
                transaction = Transaction(
                    id=row.get('id', ''),
                    from_account=row['from_account'],
                    to_account=row['to_account'],
                    amount=float(row['amount']),
                    timestamp=datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00')),
                    description=row.get('description', None)
                )
                transactions.append(transaction)
            except (ValueError, KeyError) as e:
                print(f"Error parsing row {row}: {e}")
                continue
        
        if not transactions:
            raise HTTPException(status_code=400, detail="No valid transactions found in CSV")
        
        # Analyze
        request = TransactionRequest(transactions=transactions)
        return await analyze_transactions(request)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV upload error: {str(e)}")


@app.get("/api/analysis/{analysis_id}", response_model=AnalysisResults, tags=["Analysis"])
async def get_analysis(analysis_id: str) -> AnalysisResults:
    """Retrieve cached analysis results"""
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_cache[analysis_id]


@app.get("/api/accounts/{account_id}", tags=["Account Details"])
async def get_account_details(account_id: str):
    """Get details for a specific account from all cached analyses"""
    account_results = []
    
    for analysis_id, results in analysis_cache.items():
        for score in results.account_scores:
            if score.account_id == account_id:
                # Find related rings, alerts
                related_rings = [r for r in results.rings_detected if account_id in r.accounts]
                related_smurfing = [s for s in results.smurfing_alerts if s.account_id == account_id]
                related_shells = [s for s in results.shell_accounts if s.account_id == account_id]
                
                account_results.append({
                    "analysis_id": analysis_id,
                    "account_score": score,
                    "rings": related_rings,
                    "smurfing_alerts": related_smurfing,
                    "shell_alerts": related_shells
                })
    
    if not account_results:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return account_results


@app.get("/api/stats", tags=["Statistics"])
async def get_statistics():
    """Get overall statistics from all analyses"""
    if not analysis_cache:
        return {
            "total_analyses": 0,
            "total_accounts_analyzed": 0,
            "total_transactions": 0,
            "total_cycles": 0,
            "high_risk_accounts": 0
        }
    
    total_accounts = set()
    total_transactions = 0
    total_cycles = 0
    total_high_risk = set()
    
    for results in analysis_cache.values():
        total_accounts.update(results.account_scores)
        total_transactions += results.total_transactions
        total_cycles += len(results.rings_detected)
        total_high_risk.update(results.high_risk_accounts)
    
    return {
        "total_analyses": len(analysis_cache),
        "total_accounts_analyzed": len(total_accounts),
        "total_transactions": total_transactions,
        "total_cycles": total_cycles,
        "high_risk_accounts": len(total_high_risk)
    }


# ============ LLM-POWERED ENDPOINTS ============

@app.get("/api/account-narrative/{account_id}", tags=["LLM Analysis"])
async def get_account_narrative(account_id: str):
    """
    Generate AI-powered narrative explaining an account's risk profile.
    Uses LLM to create natural language summaries.
    """
    # Find account in cache
    account_data = None
    for analysis_id, results in analysis_cache.items():
        for score in results.account_scores:
            if score.account_id == account_id:
                account_data = score
                break
        if account_data:
            break
    
    if not account_data:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    
    # Get comprehensive risk profile
    for analysis in analysis_cache.values():
        for account_score in analysis.account_scores:
            if account_score.account_id == account_id:
                risk_profile = {
                    'total_transactions': account_score.final_score,
                    'total_throughput': 0,
                    'avg_transaction_value': 0,
                    'shell_score': account_score.shell_score,
                    'pass_through_score': 0,
                    'connection_score': 0,
                    'dormancy_score': 0,
                    'directionality_score': 0,
                    'unique_sources': 0,
                    'unique_destinations': 0,
                    'in_out_ratio': 0,
                }
                break
    
    llm_service = get_llm_service()
    narrative = llm_service.generate_account_narrative(account_id, risk_profile)
    
    return {
        "account_id": account_id,
        "narrative": narrative,
        "risk_level": account_data.risk_level,
        "risk_score": account_data.final_score
    }


@app.get("/api/cycle-analysis/{analysis_id}/{ring_index}", tags=["LLM Analysis"])
async def get_cycle_analysis(analysis_id: str, ring_index: int):
    """
    Generate AI-powered analysis of a detected cycle.
    """
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
    
    results = analysis_cache[analysis_id]
    
    if ring_index >= len(results.rings_detected):
        raise HTTPException(status_code=404, detail=f"Ring {ring_index} not found")
    
    ring = results.rings_detected[ring_index]
    metrics = {
        'total_amount': ring.total_amount,
        'num_transactions': len(ring.transactions),
        'avg_transaction': ring.total_amount / len(ring.transactions) if ring.transactions else 0
    }
    
    llm_service = get_llm_service()
    analysis_text = llm_service.generate_cycle_analysis(ring.accounts, metrics)
    
    return {
        "ring_id": ring.ring_id,
        "ring_details": {
            "length": len(ring.accounts),
            "total_amount": ring.total_amount,
            "type": ring.detection_type
        },
        "participants": ring.accounts,
        "ai_analysis": analysis_text,
        "transaction_count": len(ring.transactions)
    }


@app.get("/api/investigation-summary/{analysis_id}", tags=["LLM Analysis"])
async def get_investigation_summary(analysis_id: str):
    """
    Generate executive summary for investigation using AI analysis.
    """
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
    
    results = analysis_cache[analysis_id]
    
    # Convert results to dict for LLM
    analysis_dict = {
        'total_accounts': results.total_accounts,
        'total_transactions': results.total_transactions,
        'summary': {
            'total_volume': results.summary.get('total_volume', 0)
        },
        'rings_detected': results.rings_detected,
        'smurfing_alerts': results.smurfing_alerts,
        'shell_accounts': results.shell_accounts,
        'critical_accounts': results.critical_accounts,
        'high_risk_accounts': results.high_risk_accounts
    }
    
    llm_service = get_llm_service()
    summary_text = llm_service.generate_investigation_summary(analysis_dict)
    
    # Extract structured data
    top_suspects = [a.account_id for a in results.critical_accounts[:5]] if results.critical_accounts else []
    key_findings = [
        f"{len(results.rings_detected)} money laundering rings detected",
        f"{len(results.smurfing_alerts)} smurfing alerts flagged",
        f"{len(results.shell_accounts)} shell accounts identified",
        f"Total transactional volume: ${results.summary.get('total_volume', 0):,.2f}"
    ]
    
    return {
        "overview": summary_text,
        "top_suspects": top_suspects,
        "key_findings": key_findings,
        "generated_at": datetime.utcnow().isoformat()
    }


@app.get("/api/recommendations/{account_id}", tags=["LLM Analysis"])
async def get_investigation_recommendations(account_id: str):
    """
    Generate AI-powered investigation recommendations for an account.
    """
    account_data = None
    for analysis in analysis_cache.values():
        for score in analysis.account_scores:
            if score.account_id == account_id:
                account_data = score
                break
        if account_data:
            break
    
    if not account_data:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    
    llm_service = get_llm_service()
    recommendations_text = llm_service.generate_risk_recommendations(
        account_id,
        account_data.risk_factors
    )
    
    # Parse into structured steps
    steps = [
        {
            "title": "Review Account Transactions",
            "priority": "HIGH",
            "description": "Examine all transactions for patterns and anomalies"
        },
        {
            "title": "Identify Connected Accounts",
            "priority": "HIGH", 
            "description": "Map all inbound and outbound account connections"
        },
        {
            "title": "Analyze Transaction Velocity",
            "priority": "HIGH",
            "description": "Check for high-frequency or time-clustered transactions"
        },
        {
            "title": "Verify Account Documentation",
            "priority": "MEDIUM",
            "description": "Review KYC and AML documentation for completeness"
        },
        {
            "title": "Escalate to Compliance",
            "priority": "MEDIUM",
            "description": "File SAR or refer to regulatory authority if warranted"
        }
    ]
    
    return {
        "account_id": account_id,
        "steps": steps,
        "risk_score": account_data.final_score,
        "risk_level": account_data.risk_level,
        "generated_at": datetime.utcnow().isoformat()
    }


@app.get("/api/llm-status", tags=["LLM Analysis"])
async def get_llm_status():
    """Check LLM service status and configuration"""
    llm_service = get_llm_service()
    
    return {
        "llm_enabled": llm_service.enabled,
        "provider": llm_service.provider,
        "model": llm_service.model,
        "message": "LLM features enabled. Use other endpoints for narratives and recommendations." if llm_service.enabled else "LLM features disabled. Set LLM_API_KEY environment variable to enable."
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
