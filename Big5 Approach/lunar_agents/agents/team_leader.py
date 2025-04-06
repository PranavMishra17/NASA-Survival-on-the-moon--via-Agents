"""
Team leader agent for lunar survival challenge.
"""

from typing import List, Dict, Any, Optional

from agents.agent import Agent
import config

class TeamLeader(Agent):
    """Agent specialized in team leadership for the lunar survival challenge."""
    
    def __init__(self, use_closed_loop_comm: bool = False):
        super().__init__(
            role="Team Leader",
            expertise_description=config.AGENT_ROLES["Team Leader"],
            use_team_leadership=True,
            use_closed_loop_comm=use_closed_loop_comm
        )
        
        # Add team leadership specific knowledge
        self._initialize_leadership_knowledge()
    
    def _initialize_leadership_knowledge(self):
        """Initialize leadership-specific knowledge."""
        self.add_to_knowledge_base("leadership_principles", {
            "facilitation": "Guide team discussion without dominating it",
            "coordination": "Ensure team members contribute effectively",
            "feedback": "Provide constructive feedback to improve team performance",
            "goal_alignment": "Keep team focused on the primary objective",
            "conflict_resolution": "Address disagreements constructively"
        })
        
        # Add Big Five teamwork model knowledge
        self.add_to_knowledge_base("big_five_teamwork", {
            "team_leadership": "Ability to direct and coordinate activities, assess performance, motivate team members",
            "mutual_performance_monitoring": "Ability to develop common understandings of the team environment",
            "backup_behavior": "Ability to anticipate other team members' needs through accurate knowledge",
            "adaptability": "Ability to adjust strategies based on information gathered from the environment",
            "team_orientation": "Propensity to take others' behavior into account and prioritize team goals"
        })
    
    def lead_discussion(self, topic: str, team_member_response: str = None) -> str:
        """
        Lead a discussion on the given topic.
        
        Args:
            topic: The topic for discussion
            team_member_response: Optional response from another team member
            
        Returns:
            The team leader's response
        """
        prompt = f"""
        As the Team Leader, I need you to lead a discussion on the following topic:
        
        {topic}
        
        Please fulfill your leadership role by:
        1. Establishing clear expectations for the discussion
        2. Providing structure to the problem-solving approach
        3. Ensuring all perspectives are considered
        """
        
        if team_member_response:
            prompt += f"""
            
            Your team member has provided the following input:
            
            "{team_member_response}"
            
            Please respond to their input and guide the discussion forward. Consider where you agree and disagree,
            and provide a path toward consensus.
            """
        
        return self.chat(prompt)
    
    def synthesize_rankings(self, team_member_ranking: List[str], own_ranking: List[str] = None) -> str:
        """
        Synthesize rankings from team members into a consensus ranking.
        
        Args:
            team_member_ranking: Ranking from the team member
            own_ranking: Optional ranking from the team leader
            
        Returns:
            The team leader's response with synthesized ranking
        """
        if not own_ranking:
            own_ranking = self.get_item_ranking()
        
        # Make sure all items from the NASA list are included
        all_items_set = set(config.LUNAR_ITEMS)
        
        prompt = f"""
        As the Team Leader, I need you to synthesize the different rankings into a final consensus ranking.
        
        Your ranking:
        {self._format_ranking_for_prompt(own_ranking)}
        
        Team member's ranking:
        {self._format_ranking_for_prompt(team_member_ranking)}
        
        Please create a final consensus ranking that takes both perspectives into account and includes ALL items from NASA's lunar survival challenge exactly once:

        {', '.join(config.LUNAR_ITEMS)}
        
        IMPORTANT INSTRUCTIONS:
        1. Your final ranking MUST include ALL 15 items in the list above.
        2. Each item MUST appear EXACTLY ONCE in your ranking.
        3. Double-check that no items are missing or duplicated.
        4. Explain your reasoning for each item's placement, especially where there was disagreement.
        
        Present your final ranking as a numbered list from 1 to 15, with each item on a new line, formatted as:
        1. [Item name] - [Brief justification]
        """
        
        return self.chat(prompt)
    
    def _format_ranking_for_prompt(self, ranking: List[str]) -> str:
        """Format a ranking list for inclusion in a prompt."""
        if not ranking:
            return "No ranking provided"
        
        formatted = []
        for i, item in enumerate(ranking):
            formatted.append(f"{i+1}. {item}")
        
        return "\n".join(formatted)