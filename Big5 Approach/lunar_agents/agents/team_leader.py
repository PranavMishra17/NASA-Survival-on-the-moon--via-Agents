"""
Team leader agent for lunar survival challenge.
"""

from typing import List, Dict, Any, Optional

from agents.agent import Agent
import config

class TeamLeader(Agent):
    """Agent specialized in team leadership for the lunar survival challenge."""
    
    def __init__(self, use_closed_loop_comm=False):
        super().__init__(
            role="Team Leader",
            expertise_description=config.AGENT_ROLES["Team Leader"],
            use_team_leadership=True,
            use_closed_loop_comm=use_closed_loop_comm
        )
        
        # Add team leadership specific knowledge
        self._initialize_leadership_knowledge()
        self.shared_knowledge_base = {}
    
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
    
    def _format_ranking_for_prompt(self, ranking: List[str]) -> str:
        """Format a ranking list for inclusion in a prompt."""
        if not ranking:
            return "No ranking provided"
        
        formatted = []
        for i, item in enumerate(ranking):
            formatted.append(f"{i+1}. {item}")
        
        return "\n".join(formatted)
    
    def define_task(self, task_description):
        """Define the overall task and create subtask specifications."""
        prompt = f"""
        As the Team Leader, define the overall approach for: {task_description}
        
        Break this down into clear subtasks, specifying:
        1. The objective of each subtask
        2. The sequence in which they should be completed
        3. How to evaluate successful completion
        
        Provide clear, specific instructions that will guide the team through this process.
        """
        
        response = self.chat(prompt)
        
        # Update knowledge base with task definition
        self.update_knowledge_base("task_definition", {
            "description": task_description,
            "approach": response
        })
        
        return response
    
    def document_agent_capabilities(self, agent_descriptions):
        """Document capabilities and limitations of each agent."""
        prompt = f"""
        As Team Leader, document the capabilities and limitations of the team members:
        
        {agent_descriptions}
        
        For each team member, specify:
        1. Their areas of expertise
        2. Their potential limitations
        3. How they can best contribute to the team's success
        """
        
        response = self.chat(prompt)
        
        # Update knowledge base with agent capabilities
        self.update_knowledge_base("agent_capabilities", {
            "descriptions": agent_descriptions,
            "assessment": response
        })
        
        return response
    
    def update_knowledge_base(self, category, data):
        """Update the shared knowledge base with new information."""
        if category not in self.shared_knowledge_base:
            self.shared_knowledge_base[category] = {}
        
        self.shared_knowledge_base[category].update(data)
        self.logger.info(f"Updated knowledge base: {category}")
        
        return self.shared_knowledge_base[category]
    
    def synthesize_rankings(self, team_member_ranking, own_ranking=None):
        """Synthesize rankings from team members into a consensus ranking."""
        if not own_ranking:
            own_ranking = self.get_item_ranking()
        
        # Ensure all items from NASA list are included exactly once
        all_items_set = set(config.LUNAR_ITEMS)
        
        prompt = f"""
        As the Team Leader, synthesize these rankings into a final consensus.
        
        Your ranking:
        {self._format_ranking_for_prompt(own_ranking)}
        
        Team member's ranking:
        {self._format_ranking_for_prompt(team_member_ranking)}
        
        IMPORTANT INSTRUCTIONS:
        1. Your final ranking MUST include ALL 15 items exactly ONCE.
        2. The items must be from this list: {', '.join(config.LUNAR_ITEMS)}
        3. DOUBLE-CHECK that no items are duplicated or missing.
        4. Explain your reasoning for each item's placement.
        
        Present your final ranking as a numbered list from 1 to 15:
        1. [Item name] - [Brief justification]
        """
        
        response = self.chat(prompt)
        
        # Update knowledge base with final ranking decision
        self.update_knowledge_base("final_ranking", {
            "leader_ranking": own_ranking,
            "member_ranking": team_member_ranking,
            "consensus": self.get_item_ranking(response)
        })
        
        return response