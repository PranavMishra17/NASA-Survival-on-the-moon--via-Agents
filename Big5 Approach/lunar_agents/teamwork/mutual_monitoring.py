"""
Mutual Performance Monitoring implementation for lunar survival agents.

Mutual Performance Monitoring: The ability to develop common understandings
of the team environment and apply appropriate task strategies to accurately 
monitor teammate performance.
"""

import logging
from typing import Dict, List, Any

class MutualMonitoring:
    """
    Implements mutual performance monitoring capabilities for agents.
    
    Mutual performance monitoring enables agents to keep track of each other's work,
    identify potential errors or oversights, and provide corrective feedback.
    This becomes particularly important in stressful or complex tasks.
    """
    
    def __init__(self):
        """Initialize the mutual monitoring handler."""
        self.logger = logging.getLogger("teamwork.mutual_monitoring")
        self.performance_logs = {}
        self.feedback_history = []
        self.error_detections = []
        self.logger.info("Initialized mutual performance monitoring handler")
    
    def monitor_ranking(self, agent_role: str, ranking: List[str], rationale: str) -> Dict[str, Any]:
        """
        Monitor an agent's ranking for potential issues.
        
        Args:
            agent_role: Role of the agent being monitored
            ranking: The agent's item ranking
            rationale: Justification for the ranking
            
        Returns:
            Dictionary of monitoring results and potential issues
        """
        self.logger.info(f"Monitoring ranking from {agent_role}")
        
        # Store performance data
        self.performance_logs[agent_role] = {
            "ranking": ranking,
            "rationale": rationale
        }
        
        # Check for potential issues
        issues = []
        
        # Check for missing items
        from config import LUNAR_ITEMS
        missing_items = set(LUNAR_ITEMS) - set(ranking)
        if missing_items:
            issues.append({
                "type": "missing_items",
                "description": f"Missing items in ranking: {', '.join(missing_items)}",
                "severity": "high"
            })
        
        # Check for duplicate items
        duplicates = set([item for item in ranking if ranking.count(item) > 1])
        if duplicates:
            issues.append({
                "type": "duplicate_items",
                "description": f"Duplicate items in ranking: {', '.join(duplicates)}",
                "severity": "high"
            })
        
        # Check for items with questionable rationale
        # This is a simple check - in a more sophisticated system, 
        # it would use NLP techniques to evaluate rationales
        key_survival_items = ["Oxygen tanks", "Water", "Stellar map"]
        for item in key_survival_items:
            if item in ranking and ranking.index(item) > 5:  # If ranked too low
                issues.append({
                    "type": "questionable_ranking",
                    "description": f"{item} ranked unexpectedly low at position {ranking.index(item) + 1}",
                    "severity": "medium"
                })
        
        result = {
            "agent_role": agent_role,
            "issues_detected": len(issues) > 0,
            "issues": issues
        }
        
        # Log the monitoring results
        if issues:
            self.logger.info(f"Detected {len(issues)} issues in {agent_role}'s ranking")
        else:
            self.logger.info(f"No issues detected in {agent_role}'s ranking")
        
        return result
    
    def generate_feedback(self, monitoring_result: Dict[str, Any], feedback_agent_role: str) -> str:
        """
        Generate feedback based on monitoring results.
        
        Args:
            monitoring_result: Results from monitoring an agent's ranking
            feedback_agent_role: Role of the agent providing feedback
            
        Returns:
            Feedback message to be conveyed to the monitored agent
        """
        agent_role = monitoring_result["agent_role"]
        issues = monitoring_result["issues"]
        
        if not issues:
            feedback = f"As your teammate, I've reviewed your ranking and don't see any major issues. Your approach seems sound, and I agree with your general assessment."
            self.logger.info(f"{feedback_agent_role} provided positive feedback to {agent_role}")
        else:
            feedback = f"As your teammate, I've reviewed your ranking and would like to offer some observations:\n\n"
            
            for i, issue in enumerate(issues):
                if issue["type"] == "missing_items":
                    feedback += f"{i+1}. I noticed some items may be missing from your ranking: {issue['description']}\n"
                elif issue["type"] == "duplicate_items":
                    feedback += f"{i+1}. There appear to be some duplicate entries: {issue['description']}\n"
                elif issue["type"] == "questionable_ranking":
                    feedback += f"{i+1}. I'm curious about your reasoning for {issue['description']}. Could you explain your thinking on this placement?\n"
            
            feedback += "\nPlease consider these points when refining your ranking. I appreciate your expertise and am looking forward to your perspective."
            self.logger.info(f"{feedback_agent_role} provided constructive feedback to {agent_role} on {len(issues)} issues")
        
        # Store feedback for later analysis
        self.feedback_history.append({
            "from_role": feedback_agent_role,
            "to_role": agent_role,
            "feedback": feedback,
            "issues": issues
        })
        
        return feedback
    
    def analyze_team_performance(self) -> Dict[str, Any]:
        """
        Analyze overall team performance in monitoring and feedback.
        
        Returns:
            Dictionary with team performance metrics
        """
        # Calculate metrics
        total_issues_detected = sum(len(feedback["issues"]) for feedback in self.feedback_history)
        total_feedback_exchanges = len(self.feedback_history)
        avg_issues_per_exchange = total_issues_detected / max(1, total_feedback_exchanges)
        
        # Analyze types of issues
        issue_types = {}
        for feedback in self.feedback_history:
            for issue in feedback["issues"]:
                issue_type = issue["type"]
                if issue_type not in issue_types:
                    issue_types[issue_type] = 0
                issue_types[issue_type] += 1
        
        # Analyze if feedback was addressed
        addressed_issues = 0
        for i in range(len(self.feedback_history) - 1):
            current_feedback = self.feedback_history[i]
            next_feedback = self.feedback_history[i + 1]
            
            if current_feedback["to_role"] == next_feedback["from_role"]:
                # Check if issues were addressed in next exchange
                current_issues = {issue["description"] for issue in current_feedback["issues"]}
                next_issues = {issue["description"] for issue in next_feedback["issues"]}
                addressed_issues += len(current_issues - next_issues)
        
        issue_resolution_rate = addressed_issues / max(1, total_issues_detected)
        
        # Prepare analysis
        analysis = {
            "total_monitoring_exchanges": total_feedback_exchanges,
            "total_issues_detected": total_issues_detected,
            "avg_issues_per_exchange": avg_issues_per_exchange,
            "issue_types": issue_types,
            "issue_resolution_rate": issue_resolution_rate,
            "team_monitoring_effectiveness": "high" if issue_resolution_rate > 0.7 else "medium" if issue_resolution_rate > 0.4 else "low"
        }
        
        self.logger.info(f"Team performance analysis completed: {analysis['team_monitoring_effectiveness']} effectiveness")
        return analysis
    
    def enhance_agent_prompt(self, base_prompt: str, monitoring_data: Dict[str, Any] = None) -> str:
        """
        Enhance an agent's prompt with mutual monitoring awareness.
        
        Args:
            base_prompt: The original prompt for the agent
            monitoring_data: Optional monitoring data from previous iterations
            
        Returns:
            Enhanced prompt with mutual monitoring elements
        """
        enhanced_prompt = base_prompt
        
        # Add mutual monitoring awareness to the prompt
        monitoring_addition = """
        
        As you develop your ranking, be aware that your teammate will be monitoring your work
        and may provide feedback. Similarly, you should monitor your teammate's work by:
        
        1. Checking for completeness and ensuring all items are ranked
        2. Identifying any potential inconsistencies in their reasoning
        3. Assessing if their rankings align with the scientific principles of lunar survival
        4. Considering if they've overlooked any critical factors
        
        If you notice issues, provide specific, constructive feedback that can help improve the team's overall ranking.
        """
        
        # Add specific insights from previous monitoring if available
        if monitoring_data and "feedback_history" in monitoring_data and monitoring_data["feedback_history"]:
            last_feedback = monitoring_data["feedback_history"][-1]
            if "to_role" in last_feedback and "feedback" in last_feedback:
                monitoring_addition += f"""
                
                In previous exchanges, the following feedback was provided:
                "{last_feedback['feedback']}"
                
                Consider this feedback as you develop your current ranking.
                """
        
        enhanced_prompt += monitoring_addition
        return enhanced_prompt