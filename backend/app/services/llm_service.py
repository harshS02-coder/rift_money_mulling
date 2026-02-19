"""
LLM Integration Service
Provides AI-powered narrative generation, risk analysis explanations,
and investigation recommendations.

Supports multiple LLM providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic Claude
- Local models via Ollama
"""
import os
from typing import Optional, Dict, List
import httpx
import json
from datetime import datetime


class LLMService:
    """Service for LLM-powered analysis and narratives"""

    def __init__(self):
        self.provider = os.getenv('LLM_PROVIDER', 'openai')  # openai, claude, ollama
        self.api_key = os.getenv('LLM_API_KEY', '')
        self.model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        self.enabled = bool(self.api_key) or self.provider == 'ollama'

    def generate_account_narrative(self, account_id: str, risk_profile: Dict) -> str:
        """
        Generate a natural language narrative explaining an account's risk profile.
        
        Args:
            account_id: Account identifier
            risk_profile: Risk profile dict with scores and factors
            
        Returns:
            Natural language explanation of the account's risk
        """
        if not self.enabled:
            return self._generate_fallback_narrative(account_id, risk_profile)

        prompt = self._create_account_narrative_prompt(account_id, risk_profile)
        
        try:
            if self.provider == 'openai':
                return self._call_openai(prompt)
            elif self.provider == 'claude':
                return self._call_claude(prompt)
            elif self.provider == 'ollama':
                return self._call_ollama(prompt)
        except Exception as e:
            print(f"LLM call failed: {e}, using fallback")
            return self._generate_fallback_narrative(account_id, risk_profile)

    def generate_cycle_analysis(self, cycle: List[str], cycle_metrics: Dict) -> str:
        """Generate analysis of a detected cycle"""
        if not self.enabled:
            return self._generate_fallback_cycle_analysis(cycle, cycle_metrics)

        prompt = self._create_cycle_analysis_prompt(cycle, cycle_metrics)
        
        try:
            if self.provider == 'openai':
                return self._call_openai(prompt)
            elif self.provider == 'claude':
                return self._call_claude(prompt)
            elif self.provider == 'ollama':
                return self._call_ollama(prompt)
        except Exception as e:
            print(f"LLM call failed: {e}, using fallback")
            return self._generate_fallback_cycle_analysis(cycle, cycle_metrics)

    def generate_investigation_summary(self, analysis_results: Dict) -> str:
        """Generate comprehensive investigation summary"""
        if not self.enabled:
            return self._generate_fallback_investigation_summary(analysis_results)

        prompt = self._create_investigation_summary_prompt(analysis_results)
        
        try:
            if self.provider == 'openai':
                return self._call_openai(prompt, max_tokens=1000)
            elif self.provider == 'claude':
                return self._call_claude(prompt)
            elif self.provider == 'ollama':
                return self._call_ollama(prompt)
        except Exception as e:
            print(f"LLM call failed: {e}, using fallback")
            return self._generate_fallback_investigation_summary(analysis_results)

    def generate_risk_recommendations(self, account_id: str, risk_factors: List[str]) -> List[str]:
        """Generate investigation recommendations based on risk factors"""
        if not self.enabled:
            return self._generate_fallback_recommendations(risk_factors)

        prompt = self._create_recommendations_prompt(account_id, risk_factors)
        
        try:
            if self.provider == 'openai':
                response = self._call_openai(prompt, max_tokens=500)
            elif self.provider == 'claude':
                response = self._call_claude(prompt)
            elif self.provider == 'ollama':
                response = self._call_ollama(prompt)
            
            # Parse recommendations (should be numbered list)
            return [line.strip() for line in response.split('\n') if line.strip()]
        except Exception as e:
            print(f"LLM call failed: {e}, using fallback")
            return self._generate_fallback_recommendations(risk_factors)

    # ========== LLM PROVIDER CALLS ==========

    def _call_openai(self, prompt: str, max_tokens: int = 500) -> str:
        """Call OpenAI API (GPT-3.5 or GPT-4)"""
        try:
            import openai
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial crime analyst specializing in money laundering detection. Provide clear, concise, and actionable analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            return response['choices'][0]['message']['content'].strip()
        except ImportError:
            raise Exception("openai package not installed. Install with: pip install openai")

    def _call_claude(self, prompt: str) -> str:
        """Call Anthropic Claude API"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            message = client.messages.create(
                model=self.model,
                max_tokens=500,
                system="You are a financial crime analyst specializing in money laundering detection. Provide clear, concise, and actionable analysis.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text.strip()
        except ImportError:
            raise Exception("anthropic package not installed. Install with: pip install anthropic")

    def _call_ollama(self, prompt: str) -> str:
        """Call local Ollama instance"""
        try:
            response = httpx.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                return response.json()['response'].strip()
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to connect to Ollama: {e}")

    # ========== PROMPT TEMPLATES ==========

    def _create_account_narrative_prompt(self, account_id: str, risk_profile: Dict) -> str:
        """Create prompt for account risk narrative"""
        shell_score = risk_profile.get('shell_score', 0)
        pass_through_score = risk_profile.get('pass_through_score', 0)
        connection_score = risk_profile.get('connection_score', 0)
        dormancy_score = risk_profile.get('dormancy_score', 0)
        directionality_score = risk_profile.get('directionality_score', 0)
        
        return f"""
Analyze the following financial account for money laundering risks:

Account ID: {account_id}
Total Transactions: {risk_profile.get('total_transactions', 0)}
Total Throughput: ${risk_profile.get('total_throughput', 0):,.2f}
Average Transaction Value: ${risk_profile.get('avg_transaction_value', 0):,.2f}

Risk Factors (0-100 scale):
- Shell Account Score: {shell_score}
- Pass-Through Score: {pass_through_score}
- Connection Pattern Score: {connection_score}
- Dormancy Score: {dormancy_score}
- Flow Direction Score: {directionality_score}

Unique Sources: {risk_profile.get('unique_sources', 0)}
Unique Destinations: {risk_profile.get('unique_destinations', 0)}
In/Out Ratio: {risk_profile.get('in_out_ratio', 0):.2f}

Provide a brief (2-3 sentences) professional assessment of this account's money laundering risk, focusing on the most significant risk factors.
"""

    def _create_cycle_analysis_prompt(self, cycle: List[str], metrics: Dict) -> str:
        """Create prompt for cycle analysis"""
        return f"""
Analyze the following financial cycle detected in transaction data:

Accounts in Cycle: {' -> '.join(cycle)} -> (back to start)
Cycle Length: {len(cycle)} accounts
Total Amount: ${metrics.get('total_amount', 0):,.2f}
Number of Transactions: {metrics.get('num_transactions', 0)}
Average Transaction Value: ${metrics.get('avg_transaction', 0):,.2f}

This represents a circular flow of money through {len(cycle)} accounts, indicating potential money laundering through circular transactions.

Provide a brief (2-3 sentences) analysis of why this cycle pattern is suspicious and what it might indicate.
"""

    def _create_investigation_summary_prompt(self, analysis_results: Dict) -> str:
        """Create prompt for investigation summary"""
        return f"""
Provide an executive summary for a financial investigation with the following findings:

Accounts Analyzed: {analysis_results.get('total_accounts', 0)}
Total Transactions: {analysis_results.get('total_transactions', 0)}
Total Transaction Volume: ${analysis_results.get('summary', {}).get('total_volume', 0):,.2f}

Patterns Detected:
- Cycles/Rings: {len(analysis_results.get('rings_detected', []))}
- Smurfing Alerts: {len(analysis_results.get('smurfing_alerts', []))}
- Shell Accounts: {len(analysis_results.get('shell_accounts', []))}
- Critical Risk Accounts: {len(analysis_results.get('critical_accounts', []))}
- High Risk Accounts: {len(analysis_results.get('high_risk_accounts', []))}

Generate a concise (4-5 sentences) executive summary highlighting:
1. Overall risk level (Low/Medium/High/Critical)
2. Most significant patterns detected
3. Recommended immediate actions
4. Key accounts requiring investigation priority
"""

    def _create_recommendations_prompt(self, account_id: str, risk_factors: List[str]) -> str:
        """Create prompt for investigation recommendations"""
        factors_text = "\n".join([f"- {rf}" for rf in risk_factors])
        
        return f"""
Based on the following risk factors detected for account {account_id}:

{factors_text}

Generate 5-7 specific, actionable investigation recommendations for financial examiners.
Format as a numbered list.
"""

    # ========== FALLBACK NARRATIVES (NO LLM) ==========

    def _generate_fallback_narrative(self, account_id: str, risk_profile: Dict) -> str:
        """Generate narrative without LLM"""
        shell_score = risk_profile.get('shell_score', 0)
        
        if shell_score >= 80:
            return f"Account {account_id} exhibits critical characteristics of a shell account, with very high-value throughput relative to transaction count and limited unique connections. Immediate investigation recommended."
        elif shell_score >= 60:
            return f"Account {account_id} shows significant shell account characteristics including high average transaction values and limited connection patterns. Close monitoring recommended."
        elif shell_score >= 40:
            return f"Account {account_id} displays potential shell account indicators but may have legitimate explanations. Further investigation advised."
        else:
            return f"Account {account_id} has lower risk indicators but should remain under observation as part of broader analysis."

    def _generate_fallback_cycle_analysis(self, cycle: List[str], metrics: Dict) -> str:
        """Generate cycle analysis without LLM"""
        total = metrics.get('total_amount', 0)
        txn_count = metrics.get('num_transactions', 0)
        
        return f"Detected {len(cycle)}-account cycle with ${total:,.0f} flowing through {txn_count} transactions. This circular pattern is indicative of money laundering through structured rings."

    def _generate_fallback_investigation_summary(self, analysis_results: Dict) -> str:
        """Generate investigation summary without LLM"""
        critical_count = len(analysis_results.get('critical_accounts', []))
        high_count = len(analysis_results.get('high_risk_accounts', []))
        
        if critical_count > 0:
            severity = "CRITICAL"
        elif high_count > 0:
            severity = "HIGH"
        else:
            severity = "MEDIUM"
        
        return f"Overall Risk Level: {severity}. Analysis identified {critical_count} critical-risk accounts, {high_count} high-risk accounts, and {len(analysis_results.get('rings_detected', []))} suspicious cycles. Prioritize investigation of critical accounts first."

    def _generate_fallback_recommendations(self, risk_factors: List[str]) -> List[str]:
        """Generate recommendations without LLM"""
        recommendations = [
            "Review all transaction details for the past 90 days",
            "Analyze source of funds for large transactions",
            "Investigate account beneficiary and ownership",
            "Cross-reference with other flagged accounts for connections",
            "Check for suspicious timing patterns"
        ]
        return recommendations


# Singleton instance
_llm_service = None

def get_llm_service() -> LLMService:
    """Get or create LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
