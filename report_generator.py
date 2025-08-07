"""
Comprehensive Interview Report Generator
Generates detailed reports from background-processed evaluation data
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import google.generativeai as genai
import os
from background_evaluator import get_background_evaluator

class InterviewReportGenerator:
    """
    Generates comprehensive interview reports with multiple formats
    """
    
    def __init__(self, google_api_key: str = None):
        self.google_api_key = google_api_key
        if google_api_key:
            genai.configure(api_key=google_api_key)
    
    def generate_comprehensive_report(self, session_id: str) -> Dict:
        """
        Generate a comprehensive interview report
        """
        evaluator = get_background_evaluator(self.google_api_key)
        raw_report = evaluator.get_session_report(session_id)
        
        if not raw_report:
            return {"error": "Session not found or evaluation not complete"}
        
        # Basic report structure
        report = {
            "report_id": f"RPT_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "session_id": session_id,
            "generated_at": datetime.now().isoformat(),
            "candidate_info": {
                "name": raw_report["candidate_name"],
                "position": raw_report["position"]
            },
            "overall_assessment": {
                "overall_score": round(raw_report.get("overall_score", 0), 2),
                "technical_score": round(raw_report.get("technical_score", 0), 2),
                "communication_score": round(raw_report.get("communication_score", 0), 2),
                "total_questions": raw_report["total_questions"]
            },
            "detailed_analysis": self._analyze_responses(raw_report["exchanges"]),
            "recommendations": self._generate_recommendations(raw_report),
            "report_formats": {}
        }
        
        # Generate different report formats
        report["report_formats"]["executive_summary"] = self._generate_executive_summary(report)
        report["report_formats"]["detailed_feedback"] = self._generate_detailed_feedback(report)
        report["report_formats"]["hiring_recommendation"] = self._generate_hiring_recommendation(report)
        
        return report
    
    def _analyze_responses(self, exchanges: List[Dict]) -> Dict:
        """Analyze all responses for patterns and insights"""
        if not exchanges:
            return {"error": "No exchanges to analyze"}
        
        # Calculate averages
        scores = {
            "relevance": [ex.get("relevance_score", 0) for ex in exchanges if ex.get("relevance_score")],
            "clarity": [ex.get("clarity_score", 0) for ex in exchanges if ex.get("clarity_score")],
            "depth": [ex.get("depth_score", 0) for ex in exchanges if ex.get("depth_score")]
        }
        
        averages = {
            key: round(sum(values) / len(values), 2) if values else 0
            for key, values in scores.items()
        }
        
        # Identify strong and weak responses
        strong_responses = [
            ex for ex in exchanges 
            if ex.get("relevance_score", 0) >= 8 and ex.get("clarity_score", 0) >= 8
        ]
        
        weak_responses = [
            ex for ex in exchanges 
            if ex.get("relevance_score", 0) <= 5 or ex.get("clarity_score", 0) <= 5
        ]
        
        return {
            "average_scores": averages,
            "score_trends": self._calculate_score_trends(exchanges),
            "strong_responses_count": len(strong_responses),
            "weak_responses_count": len(weak_responses),
            "consistency_rating": self._calculate_consistency(scores),
            "response_length_analysis": self._analyze_response_lengths(exchanges)
        }
    
    def _calculate_score_trends(self, exchanges: List[Dict]) -> Dict:
        """Calculate if scores are improving, declining, or stable"""
        if len(exchanges) < 3:
            return {"trend": "insufficient_data"}
        
        # Get scores in chronological order
        relevance_scores = [ex.get("relevance_score", 0) for ex in exchanges[-5:]]  # Last 5
        
        # Simple trend calculation
        if len(relevance_scores) >= 3:
            early_avg = sum(relevance_scores[:2]) / 2
            late_avg = sum(relevance_scores[-2:]) / 2
            
            if late_avg > early_avg + 1:
                trend = "improving"
            elif early_avg > late_avg + 1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "early_average": round(sum(relevance_scores[:2]) / 2, 2) if len(relevance_scores) >= 2 else 0,
            "late_average": round(sum(relevance_scores[-2:]) / 2, 2) if len(relevance_scores) >= 2 else 0
        }
    
    def _calculate_consistency(self, scores: Dict) -> str:
        """Calculate how consistent the candidate's performance was"""
        all_scores = []
        for score_list in scores.values():
            all_scores.extend(score_list)
        
        if len(all_scores) < 2:
            return "insufficient_data"
        
        # Calculate standard deviation (simple approximation)
        mean = sum(all_scores) / len(all_scores)
        variance = sum((x - mean) ** 2 for x in all_scores) / len(all_scores)
        std_dev = variance ** 0.5
        
        if std_dev < 1.5:
            return "very_consistent"
        elif std_dev < 2.5:
            return "consistent"
        elif std_dev < 3.5:
            return "moderately_consistent"
        else:
            return "inconsistent"
    
    def _analyze_response_lengths(self, exchanges: List[Dict]) -> Dict:
        """Analyze response length patterns"""
        lengths = [len(ex.get("response", "")) for ex in exchanges]
        
        if not lengths:
            return {"average_length": 0, "pattern": "no_data"}
        
        avg_length = sum(lengths) / len(lengths)
        
        # Categorize response pattern
        if avg_length > 200:
            pattern = "detailed_responses"
        elif avg_length > 100:
            pattern = "balanced_responses"
        elif avg_length > 50:
            pattern = "concise_responses"
        else:
            pattern = "brief_responses"
        
        return {
            "average_length": round(avg_length, 1),
            "pattern": pattern,
            "shortest": min(lengths),
            "longest": max(lengths),
            "total_responses": len(lengths)
        }
    
    def _generate_recommendations(self, raw_report: Dict) -> Dict:
        """Generate hiring recommendations based on scores"""
        overall_score = raw_report.get("overall_score", 0)
        technical_score = raw_report.get("technical_score", 0)
        communication_score = raw_report.get("communication_score", 0)
        
        # Generate recommendation
        if overall_score >= 8:
            recommendation = "strong_hire"
            confidence = "high"
        elif overall_score >= 7:
            recommendation = "hire"
            confidence = "medium_high"
        elif overall_score >= 6:
            recommendation = "hire_with_reservations"
            confidence = "medium"
        elif overall_score >= 5:
            recommendation = "no_hire_but_close"
            confidence = "medium_low"
        else:
            recommendation = "no_hire"
            confidence = "high"
        
        # Generate specific feedback areas
        strengths = []
        concerns = []
        
        if technical_score >= 7:
            strengths.append("Strong technical competency")
        elif technical_score < 5:
            concerns.append("Technical skills need development")
        
        if communication_score >= 7:
            strengths.append("Excellent communication skills")
        elif communication_score < 5:
            concerns.append("Communication could be improved")
        
        return {
            "recommendation": recommendation,
            "confidence_level": confidence,
            "strengths": strengths,
            "areas_of_concern": concerns,
            "next_steps": self._suggest_next_steps(recommendation, overall_score)
        }
    
    def _suggest_next_steps(self, recommendation: str, score: float) -> List[str]:
        """Suggest next steps based on recommendation"""
        if recommendation == "strong_hire":
            return [
                "Move to final round interviews",
                "Check references",
                "Prepare offer package"
            ]
        elif recommendation == "hire":
            return [
                "Conduct technical deep-dive session",
                "Team fit assessment",
                "Reference checks"
            ]
        elif recommendation == "hire_with_reservations":
            return [
                "Additional technical assessment",
                "Pair programming session",
                "Meet with senior team members"
            ]
        else:
            return [
                "Thank candidate for their time",
                "Provide constructive feedback",
                "Keep for future opportunities if close"
            ]
    
    def _generate_executive_summary(self, report: Dict) -> str:
        """Generate executive summary for managers"""
        candidate_name = report["candidate_info"]["name"]
        position = report["candidate_info"]["position"]
        overall_score = report["overall_assessment"]["overall_score"]
        recommendation = report["recommendations"]["recommendation"]
        
        summary = f"""
EXECUTIVE SUMMARY - {candidate_name}

Position: {position}
Overall Score: {overall_score}/10
Recommendation: {recommendation.replace('_', ' ').title()}

Key Highlights:
• Technical Competency: {report['overall_assessment']['technical_score']}/10
• Communication Skills: {report['overall_assessment']['communication_score']}/10
• Questions Completed: {report['overall_assessment']['total_questions']}

Strengths: {', '.join(report['recommendations']['strengths']) if report['recommendations']['strengths'] else 'Standard performance'}

Areas of Concern: {', '.join(report['recommendations']['areas_of_concern']) if report['recommendations']['areas_of_concern'] else 'None identified'}

Next Steps: {'; '.join(report['recommendations']['next_steps'])}
        """.strip()
        
        return summary
    
    def _generate_detailed_feedback(self, report: Dict) -> str:
        """Generate detailed feedback for candidate development"""
        analysis = report["detailed_analysis"]
        
        feedback = f"""
DETAILED PERFORMANCE FEEDBACK

Overall Performance Analysis:
• Average Relevance Score: {analysis['average_scores']['relevance']}/10
• Average Clarity Score: {analysis['average_scores']['clarity']}/10  
• Average Depth Score: {analysis['average_scores']['depth']}/10

Performance Consistency: {analysis['consistency_rating'].replace('_', ' ').title()}
Performance Trend: {analysis['score_trends']['trend'].replace('_', ' ').title()}

Response Pattern: {analysis['response_length_analysis']['pattern'].replace('_', ' ').title()}
• Average Response Length: {analysis['response_length_analysis']['average_length']} characters
• Strong Responses: {analysis['strong_responses_count']}
• Areas for Improvement: {analysis['weak_responses_count']} responses could be enhanced

Recommendations for Growth:
{chr(10).join(['• ' + area for area in report['recommendations']['areas_of_concern']])}

Strengths to Leverage:
{chr(10).join(['• ' + strength for strength in report['recommendations']['strengths']])}
        """.strip()
        
        return feedback
    
    def _generate_hiring_recommendation(self, report: Dict) -> str:
        """Generate formal hiring recommendation"""
        candidate_name = report["candidate_info"]["name"]
        position = report["candidate_info"]["position"]
        recommendation = report["recommendations"]["recommendation"]
        confidence = report["recommendations"]["confidence_level"]
        overall_score = report["overall_assessment"]["overall_score"]
        
        formal_recommendation = f"""
FORMAL HIRING RECOMMENDATION

Candidate: {candidate_name}
Position: {position}
Interview Date: {report['generated_at'][:10]}

RECOMMENDATION: {recommendation.replace('_', ' ').upper()}
Confidence Level: {confidence.replace('_', ' ').title()}

Score Breakdown:
• Overall Assessment: {overall_score}/10
• Technical Competency: {report['overall_assessment']['technical_score']}/10
• Communication Skills: {report['overall_assessment']['communication_score']}/10

Rationale:
{self._generate_rationale(report)}

Immediate Next Steps:
{chr(10).join(['• ' + step for step in report['recommendations']['next_steps']])}

Prepared by: AI Interview System
        """.strip()
        
        return formal_recommendation
    
    def _generate_rationale(self, report: Dict) -> str:
        """Generate rationale for the hiring decision"""
        score = report["overall_assessment"]["overall_score"]
        
        if score >= 8:
            return "Candidate demonstrated exceptional competency across all evaluation areas. Strong technical skills combined with excellent communication make them an ideal fit."
        elif score >= 7:
            return "Candidate showed solid performance with notable strengths. Minor areas for development do not significantly impact overall suitability."
        elif score >= 6:
            return "Candidate meets basic requirements but has some areas requiring attention. Consider additional evaluation or specific role alignment."
        elif score >= 5:
            return "Candidate shows potential but performance gaps raise concerns about immediate readiness for this role."
        else:
            return "Candidate did not meet the minimum requirements for this position based on current evaluation criteria."

# Convenience functions for quick report access
def generate_session_report(session_id: str, google_api_key: str = None) -> Dict:
    """Quick function to generate a complete session report"""
    generator = InterviewReportGenerator(google_api_key)
    return generator.generate_comprehensive_report(session_id)

def get_executive_summary(session_id: str, google_api_key: str = None) -> str:
    """Quick function to get just the executive summary"""
    report = generate_session_report(session_id, google_api_key)
    if "error" in report:
        return f"Report not available: {report['error']}"
    return report["report_formats"]["executive_summary"]

def get_hiring_recommendation(session_id: str, google_api_key: str = None) -> str:
    """Quick function to get formal hiring recommendation"""
    report = generate_session_report(session_id, google_api_key)
    if "error" in report:
        return f"Recommendation not available: {report['error']}"
    return report["report_formats"]["hiring_recommendation"]
